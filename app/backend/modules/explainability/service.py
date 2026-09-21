import pandas as pd
from sqlalchemy.orm import Session

from app.backend.core.enums import ProjectStatus
from app.backend.modules.explainability.model import FraudExplanation
from app.backend.modules.explainability.repository import ExplainabilityRepository
from app.backend.modules.explainability.utility import build_score_maps, explanation_reason
from app.backend.modules.explainability.validation import ensure_results_exist
from app.backend.modules.logs.service import LogService
from app.backend.modules.projects.service import ProjectService
from app.backend.utils.dataframe import make_row_identifier


class ExplainabilityService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ExplainabilityRepository(session)
        self.log_service = LogService(session)

    def run(self, project_id: str) -> list[FraudExplanation]:
        dataset, df, results = self.repository.latest_assets(project_id)
        if dataset is None or df is None:
            raise ValueError("Run detection before explainability.")
        ensure_results_exist(len(results))

        row_ids = make_row_identifier(df, dataset.schema_profile["semantic_columns"]).astype(str)
        row_index = {row_id: idx for idx, row_id in enumerate(row_ids.tolist())}
        score_maps = build_score_maps(df)
        baselines = {}
        for column in df.columns:
            series = df[column]
            if pd.api.types.is_numeric_dtype(series):
                baselines[column] = float(series.median()) if not series.dropna().empty else 0.0
            else:
                mode = series.mode(dropna=True)
                baselines[column] = mode.iloc[0] if not mode.empty else None

        artifacts: list[FraudExplanation] = []
        for result in results:
            idx = row_index.get(result.row_identifier)
            if idx is None:
                continue
            contributions = []
            for column, series in score_maps.items():
                score = float(series.iloc[idx]) if idx < len(series) else 0.0
                contributions.append((column, score))
            contributions.sort(key=lambda item: item[1], reverse=True)
            top_features = [name for name, score in contributions[:5] if score > 0]
            payload = {
                feature: {
                    "score": round(next(score for name, score in contributions if name == feature), 4),
                    "value": result.raw_record.get(feature),
                    "baseline": baselines.get(feature),
                    "reason": explanation_reason(
                        feature,
                        result.raw_record.get(feature),
                        baselines.get(feature),
                    ),
                }
                for feature in top_features
            }
            explanation_text = (
                "This record was flagged because "
                + "; ".join(item["reason"] for item in payload.values())
                if payload
                else "This record was flagged due to elevated combined anomaly signals in the uploaded dataset."
            )
            result.explanation_text = explanation_text
            result.affected_features = top_features
            result.explanation_payload = payload
            artifacts.append(
                FraudExplanation(
                    row_identifier=result.row_identifier,
                    predicted_label=result.predicted_label,
                    risk_score=result.risk_score,
                    explanation_text=explanation_text,
                    affected_features=top_features,
                    explanation_payload=payload,
                )
            )

        project = ProjectService(self.session).repository.get(project_id)
        project.status = ProjectStatus.EXPLAINED
        self.session.commit()
        self.log_service.record(
            "explainability.completed",
            "Explainability generated for fraud results.",
            project_id=project_id,
            details={"results": len(artifacts)},
        )
        return artifacts
