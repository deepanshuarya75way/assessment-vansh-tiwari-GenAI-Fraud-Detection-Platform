from __future__ import annotations

import time
from typing import Any

import numpy as np
import pandas as pd

from app.backend.modules.ml.artifacts import FraudDetectionArtifact, PredictionRecord
from app.backend.modules.ml.model_manager import ModelManager
from app.backend.modules.ml.risk_scoring import RiskScoringEngine
from app.backend.modules.ml.utils import normalize_scores


class FraudDetectionEngine:
    def __init__(self, model_manager: ModelManager | None = None, risk_engine: RiskScoringEngine | None = None) -> None:
        self.model_manager = model_manager or ModelManager()
        self.risk_engine = risk_engine or RiskScoringEngine()

    def infer(
        self,
        training_artifact,
        feature_frame: pd.DataFrame,
        row_identifiers: list[str],
        feature_importance: list[dict[str, Any]] | None = None,
    ) -> FraudDetectionArtifact:
        started_at = time.time()
        model = self.model_manager.load_model(training_artifact)
        selected_frame = feature_frame[training_artifact.feature_columns]

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(selected_frame)[:, 1]
            predictions = model.predict(selected_frame)
            confidence = np.max(model.predict_proba(selected_frame), axis=1)
            anomaly_scores = None
        else:
            anomaly_scores = -model.score_samples(selected_frame) if hasattr(model, "score_samples") else -model.decision_function(selected_frame)
            probabilities = normalize_scores(anomaly_scores)
            predictions = (probabilities >= np.quantile(probabilities, 0.9)).astype(int)
            confidence = 1.0 - normalize_scores(np.abs(probabilities - np.median(probabilities)))

        risk = self.risk_engine.score(probabilities, confidence, anomaly_scores)
        fraud_labels = ["fraud" if int(pred) == 1 else "safe" for pred in predictions]

        records: list[PredictionRecord] = []
        for index, row_identifier in enumerate(row_identifiers):
            label = fraud_labels[index]
            reason = None if label == "safe" else "Transaction risk exceeded the dataset-derived fraud threshold."
            records.append(
                PredictionRecord(
                    row_identifier=row_identifier,
                    predicted_label=label,
                    fraud_probability=float(probabilities[index]),
                    confidence_score=float(confidence[index]),
                    normalized_risk_score=float(risk["normalized_scores"][index]),
                    risk_band=risk["risk_bands"][index],
                    model_name=training_artifact.model_name,
                    explanation=reason,
                    explanation_payload={
                        "risk_score": risk["risk_scores"][index],
                        "band": risk["risk_bands"][index],
                        "thresholds": risk["thresholds"],
                    },
                    prediction_metadata={
                        "model_version": training_artifact.model_version,
                        "dataset_id": training_artifact.dataset_id,
                    },
                )
            )

        fraud_count = sum(1 for item in records if item.predicted_label == "fraud")
        review_count = sum(1 for item in records if item.risk_band == "medium")
        safe_count = sum(1 for item in records if item.predicted_label == "safe")
        summary = {
            "dataset_id": training_artifact.dataset_id,
            "model_name": training_artifact.model_name,
            "model_version": training_artifact.model_version,
            "total_records": len(records),
            "fraud_count": fraud_count,
            "review_count": review_count,
            "safe_count": safe_count,
            "fraud_probability_mean": round(float(np.mean(probabilities)) if len(probabilities) else 0.0, 4),
            "confidence_mean": round(float(np.mean(confidence)) if len(confidence) else 0.0, 4),
        }
        return FraudDetectionArtifact(
            dataset_id=training_artifact.dataset_id,
            model_name=training_artifact.model_name,
            model_kind=training_artifact.model_kind,
            model_version=training_artifact.model_version,
            predictions=records,
            summary=summary,
            risk_distribution={"high": fraud_count, "medium": review_count, "low": safe_count},
            confidence_scores=[round(float(value), 4) for value in confidence],
            feature_importance=feature_importance or [],
            metadata={
                "training_status": training_artifact.training_status,
                "training_time_seconds": training_artifact.training_time_seconds,
                "processing_time_seconds": round(time.time() - started_at, 4),
            },
        )