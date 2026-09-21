from pydantic import Field

from app.backend.common.schemas import ORMBaseModel, TimestampedResponse
from app.backend.core.enums import FeedbackType, FraudLabel


class FeedbackCreateRequest(ORMBaseModel):
    feedback_type: FeedbackType = FeedbackType.LABEL_CORRECTION
    result_id: str | None = None
    corrected_label: FraudLabel | None = None
    notes: str | None = Field(default=None, max_length=4000)
    payload: dict | None = None


class FeedbackResponse(TimestampedResponse):
    project_id: str
    dataset_id: str | None
    result_id: str | None
    user_id: str | None
    feedback_type: str
    original_label: str | None
    corrected_label: str | None
    notes: str | None
    payload: dict | None