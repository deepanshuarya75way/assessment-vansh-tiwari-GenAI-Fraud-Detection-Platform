from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.neighbors import LocalOutlierFactor
from sqlalchemy.orm import Session

from app.backend.core.enums import ProjectStatus
from app.backend.modules.detection.model import DetectionArtifact
from app.backend.db.enterprise_models import FraudResult
from app.backend.modules.detection.repository import DetectionRepository
from app.backend.modules.detection.utility import (
    default_contamination,
    label_from_risk,
    normalize_scores,
    supervised_metrics,
)
from app.backend.modules.detection.validation import ensure_detection_sample_size
from app.backend.modules.logs.service import LogService
from app.backend.modules.preprocessing.service import PreprocessingService
from app.backend.modules.projects.service import ProjectService
from app.backend.utils.dataframe import make_row_identifier
from app.backend.utils.ml import save_joblib_artifact
from app.backend.utils.storage import write_json


class DetectionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = DetectionRepository(session)
        self.log_service = LogService(session)

    def run(self, project_id: str) -> DetectionArtifact:
        dataset, cleaned = self.repository.latest_dataset_and_cleaned(project_id)
        if not dataset or not cleaned:
            raise ValueError("Run cleaning before fraud detection.")

        prepared = PreprocessingService(self.session).prepare(project_id)
        X = prepared.feature_matrix
        ensure_detection_sample_size(len(X))
        row_ids = make_row_identifier(prepared.dataframe, dataset.schema_profile["semantic_columns"]).astype(str).tolist()
        raw_records = prepared.dataframe.replace({np.nan: None}).to_dict(orient="records")
        contamination = default_contamination(len(X))
        metrics: dict[str, float] = {}
        strategy = "unsupervised_ensemble"

        if prepared.label_series is not None and prepared.label_series.nunique() >= 2:
            strategy = "supervised_ensemble"
            y = prepared.label_series.to_numpy()
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=42,
                stratify=y if len(np.unique(y)) > 1 else None,
            )
            rf_model = RandomForestClassifier(
                n_estimators=250,
                random_state=42,
                class_weight="balanced",
                n_jobs=-1,
            )
            gb_model = HistGradientBoostingClassifier(random_state=42)
            anomaly_model = IsolationForest(
                n_estimators=250,
                contamination=contamination,
                random_state=42,
            )
            rf_model.fit(X_train, y_train)
            gb_model.fit(X_train, y_train)
            anomaly_model.fit(X_train)

            rf_prob = rf_model.predict_proba(X)[:, 1]
            gb_prob = gb_model.predict_proba(X)[:, 1]
            anomaly_prob = normalize_scores(-anomaly_model.score_samples(X))
            combined_probability = 0.45 * rf_prob + 0.35 * gb_prob + 0.20 * anomaly_prob
            risk_scores = np.clip(combined_probability * 100, 0, 100)

            test_prob = (
                0.45 * rf_model.predict_proba(X_test)[:, 1]
                + 0.35 * gb_model.predict_proba(X_test)[:, 1]
                + 0.20 * normalize_scores(-anomaly_model.score_samples(X_test))
            )
            metrics = supervised_metrics(y_test, test_prob)
            model_name = "random_forest + hist_gradient_boosting + isolation_forest"
            save_joblib_artifact(project_id, "fraud_detection_supervised", {
                "rf_model": rf_model,
                "gb_model": gb_model,
                "anomaly_model": anomaly_model,
            })
        else:
            iso_model = IsolationForest(
                n_estimators=300,
                contamination=contamination,
                random_state=42,
            )
            iso_model.fit(X)
            iso_scores = normalize_scores(-iso_model.score_samples(X))

            if len(X) > 15:
                neighbor_count = min(35, len(X) - 1)
                lof_model = LocalOutlierFactor(
                    n_neighbors=max(5, neighbor_count),
                    contamination=contamination,
                )
                lof_model.fit_predict(X)
                lof_scores = normalize_scores(-lof_model.negative_outlier_factor_)
                combined_scores = 0.6 * iso_scores + 0.4 * lof_scores
                save_joblib_artifact(project_id, "fraud_detection_unsupervised", {
                    "iso_model": iso_model,
                    "contamination": contamination,
                })
                model_name = "isolation_forest + local_outlier_factor"
            else:
                combined_scores = iso_scores
                save_joblib_artifact(project_id, "fraud_detection_unsupervised", {
                    "iso_model": iso_model,
                    "contamination": contamination,
                })
                model_name = "isolation_forest"
            risk_scores = np.clip(combined_scores * 100, 0, 100)
            metrics = {"contamination": contamination}

        fraud_threshold = float(np.quantile(risk_scores, 1 - contamination))
        review_threshold = float(np.quantile(risk_scores, max(0.0, 1 - contamination * 2.5)))
        predicted_labels = label_from_risk(risk_scores, fraud_threshold, review_threshold)
        confidence_scores = np.clip(np.abs(risk_scores - review_threshold) / max(100 - review_threshold, 1), 0, 1)

        self.repository.result_repository.clear_for_dataset(dataset.id)
        for row_identifier, label, risk, confidence, raw_record in zip(
            row_ids,
            predicted_labels,
            risk_scores,
            confidence_scores,
            raw_records,
            strict=False,
        ):
            self.repository.result_repository.add(
                FraudResult(
                    dataset_id=dataset.id,
                    row_identifier=row_identifier,
                    predicted_label=label,
                    risk_score=float(risk),
                    confidence_score=float(confidence),
                    model_name=model_name,
                    explanation_text=None,
                    explanation_payload=None,
                    affected_features=None,
                    raw_record=raw_record,
                    feedback_label=None,
                )
            )

        project = ProjectService(self.session).repository.get(project_id)
        project.status = ProjectStatus.DETECTED
        summary = {
            "project_id": project_id,
            "dataset_id": dataset.id,
            "strategy": strategy,
            "metrics": metrics,
            "thresholds": {
                "fraud_threshold": fraud_threshold,
                "review_threshold": review_threshold,
            },
            "total_records": len(predicted_labels),
            "fraud_count": predicted_labels.count("fraud"),
            "review_count": predicted_labels.count("review"),
            "safe_count": predicted_labels.count("safe"),
        }
        target = Path(cleaned.cleaned_parquet_path).with_name("detection_summary.json")
        write_json(target, summary)
        self.session.commit()
        self.log_service.record(
            "detection.completed",
            "Fraud detection completed.",
            project_id=project_id,
            details=summary,
        )
        return DetectionArtifact(**summary)

    def list_results(self, project_id: str) -> list[FraudResult]:
        dataset, _ = self.repository.latest_dataset_and_cleaned(project_id)
        if not dataset:
            return []
        return self.repository.result_repository.list_for_dataset(dataset.id)
