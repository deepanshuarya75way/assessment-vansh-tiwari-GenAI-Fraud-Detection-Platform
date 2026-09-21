from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.backend.core.enums import ProjectStatus
from app.backend.modules.analytics.model import AnalyticsArtifact
from app.backend.modules.analytics.repository import AnalyticsRepository
from app.backend.modules.analytics.utility import risk_distribution, timeline_counts, top_counts
from app.backend.modules.analytics.validation import ensure_analytics_inputs
from app.backend.modules.logs.service import LogService
from app.backend.modules.projects.service import ProjectService
from app.backend.utils.storage import write_json


class AnalyticsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AnalyticsRepository(session)
        self.log_service = LogService(session)

    def generate(self, project_id: str) -> AnalyticsArtifact:
        dataset, df, results = self.repository.latest_assets(project_id)
        ensure_analytics_inputs(dataset is not None, bool(results))
        assert dataset is not None
        assert df is not None

        fraud_results = [item for item in results if item.predicted_label == "fraud"]
        review_results = [item for item in results if item.predicted_label == "review"]
        safe_results = [item for item in results if item.predicted_label == "safe"]
        semantic = dataset.schema_profile["semantic_columns"]
        risk_scores = [item.risk_score for item in results]

        payload = {
            "dataset_statistics": {
                "row_count": dataset.row_count,
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "semantic_columns": semantic,
            },
            "fraud_statistics": {
                "fraud_count": len(fraud_results),
                "review_count": len(review_results),
                "safe_count": len(safe_results),
                "average_risk_score": round(sum(risk_scores) / max(len(risk_scores), 1), 2),
            },
            "charts": {
                "risk_distribution": risk_distribution(risk_scores),
                "category_analysis": top_counts(df[semantic["category"]]) if semantic.get("category") else [],
                "timeline_analysis": timeline_counts(df, semantic.get("date")),
                "location_analysis": top_counts(df[semantic["location"]]) if semantic.get("location") else [],
                "merchant_analysis": top_counts(df[semantic["merchant"]]) if semantic.get("merchant") else [],
            },
            "tables": {
                "top_risk_transactions": [
                    {
                        "row_identifier": item.row_identifier,
                        "predicted_label": item.predicted_label,
                        "risk_score": item.risk_score,
                        "confidence_score": item.confidence_score,
                        "raw_record": item.raw_record,
                    }
                    for item in results[:20]
                ]
            },
        }

        project = ProjectService(self.session).repository.get(project_id)
        project.status = ProjectStatus.ANALYZED
        write_json(Path(dataset.raw_parquet_path).with_name("analytics.json"), payload)
        self.session.commit()
        self.log_service.record(
            "analytics.completed",
            "Analytics payload generated.",
            project_id=project_id,
            details={"fraud_count": len(fraud_results), "review_count": len(review_results)},
        )
        return AnalyticsArtifact(project_id=project_id, payload=payload)
