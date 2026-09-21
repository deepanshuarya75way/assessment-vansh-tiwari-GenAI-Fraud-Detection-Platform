from __future__ import annotations

import time
from dataclasses import asdict

import numpy as np

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent
from app.backend.core.exceptions import ProcessingError
from app.backend.core.enums import FraudLabel


class FraudDetectionAgent(BaseAgent):
    name = "fraud_detection_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Computing fraud risk scores from processed features.")]
        matrix = context.artifacts.get("feature_matrix")
        feature_names = context.artifacts.get("feature_names", [])
        if matrix is None:
            raise ProcessingError("Fraud detection agent requires a prepared feature matrix.")

        if hasattr(matrix, "shape"):
            row_count = int(matrix.shape[0])
            column_count = int(matrix.shape[1])
        else:
            row_count = len(matrix)
            column_count = len(matrix[0]) if matrix else 0

        numeric_view = np.asarray(matrix, dtype=float)
        row_means = np.nanmean(np.abs(numeric_view), axis=1)
        row_stdev = np.nanstd(numeric_view, axis=1)
        risk_scores = np.clip((row_means + row_stdev) * 25.0, 0.0, 100.0)
        fraud_threshold = float(np.quantile(risk_scores, 0.9))
        review_threshold = float(np.quantile(risk_scores, 0.75))

        results: list[dict[str, object]] = []
        for index, risk_score in enumerate(risk_scores):
            if risk_score >= fraud_threshold:
                label = FraudLabel.FRAUD.value
                confidence = min(0.99, float(risk_score / 100.0))
            elif risk_score >= review_threshold:
                label = FraudLabel.REVIEW.value
                confidence = 0.65 + float((risk_score - review_threshold) / max(100.0 - review_threshold, 1.0)) * 0.2
            else:
                label = FraudLabel.SAFE.value
                confidence = max(0.5, 1.0 - float(risk_score / 200.0))

            results.append(
                {
                    "row_identifier": str(index),
                    "predicted_label": label,
                    "risk_score": round(float(risk_score), 4),
                    "confidence_score": round(float(confidence), 4),
                    "fraud_probability": round(float(risk_score / 100.0), 4),
                    "risk_band": "high" if label == FraudLabel.FRAUD.value else "medium" if label == FraudLabel.REVIEW.value else "low",
                    "feature_snapshot": {name: None for name in feature_names[:10]},
                }
            )

        fraud_count = sum(1 for item in results if item["predicted_label"] == FraudLabel.FRAUD.value)
        review_count = sum(1 for item in results if item["predicted_label"] == FraudLabel.REVIEW.value)
        safe_count = sum(1 for item in results if item["predicted_label"] == FraudLabel.SAFE.value)

        payload = {
            "dataset_id": context.dataset_id,
            "strategy": "dataset_risk_scoring",
            "risk_distribution": {
                "low": safe_count,
                "medium": review_count,
                "high": fraud_count,
            },
            "confidence_scores": [item["confidence_score"] for item in results],
            "fraud_results": results,
            "summary": {
                "total_records": row_count,
                "fraud_count": fraud_count,
                "review_count": review_count,
                "safe_count": safe_count,
                "fraud_threshold": round(fraud_threshold, 4),
                "review_threshold": round(review_threshold, 4),
            },
            "feature_count": column_count,
        }
        return self._build_result(
            status="success",
            summary="Fraud risk scores computed from uploaded dataset.",
            metadata={"dataset_id": context.dataset_id, "row_count": row_count},
            payload=payload,
            logs=logs,
            started_at=started_at,
        )