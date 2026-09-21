from app.backend.core.enums import FeedbackType
from app.backend.core.exceptions import ProcessingError
from app.backend.modules.feedback.schema import FeedbackCreateRequest


def ensure_feedback_request(payload: FeedbackCreateRequest) -> None:
    if payload.feedback_type == FeedbackType.LABEL_CORRECTION and not payload.corrected_label:
        raise ProcessingError("Corrected label is required for label correction feedback.")
    if payload.feedback_type == FeedbackType.LABEL_CORRECTION and not payload.result_id:
        raise ProcessingError("A fraud result identifier is required for label correction feedback.")