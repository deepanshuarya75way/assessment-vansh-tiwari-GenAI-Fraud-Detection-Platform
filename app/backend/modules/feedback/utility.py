from __future__ import annotations

from typing import Any

from app.backend.db.enterprise_models import AnalystFeedback, FraudResult


def build_retraining_payload(feedback: AnalystFeedback, result: FraudResult | None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "feedback_id": feedback.id,
        "project_id": feedback.project_id,
        "dataset_id": feedback.dataset_id,
        "result_id": feedback.result_id,
        "feedback_type": feedback.feedback_type,
        "original_label": feedback.original_label,
        "corrected_label": feedback.corrected_label,
        "notes": feedback.notes,
        "payload": feedback.payload,
    }
    if result:
        payload["result"] = {
            "row_identifier": result.row_identifier,
            "predicted_label": result.predicted_label,
            "risk_score": result.risk_score,
            "confidence_score": result.confidence_score,
            "model_name": result.model_name,
        }
    return payload