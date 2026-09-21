from app.backend.common.schemas import TimestampedResponse


class FraudResultResponse(TimestampedResponse):
    dataset_id: str
    row_identifier: str
    predicted_label: str
    risk_score: float
    confidence_score: float
    model_name: str
    explanation_text: str | None
    explanation_payload: dict | None
    affected_features: list[str] | None
    raw_record: dict
    feedback_label: str | None


class DetectionSummaryResponse:
    pass
