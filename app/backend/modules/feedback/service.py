from pathlib import Path

from sqlalchemy.orm import Session

from app.backend.core.exceptions import NotFoundError
from app.backend.core.enums import FraudLabel
from app.backend.db.enterprise_models import FraudResult, AnalystFeedback
from app.backend.modules.feedback.repository import FeedbackRepository
from app.backend.modules.feedback.schema import FeedbackCreateRequest
from app.backend.modules.feedback.utility import build_retraining_payload
from app.backend.modules.feedback.validation import ensure_feedback_request
from app.backend.modules.logs.service import LogService
from app.backend.modules.projects.service import ProjectService
from app.backend.utils.storage import project_storage_path, write_json


class FeedbackService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = FeedbackRepository(session)
        self.log_service = LogService(session)

    def submit(self, project_id: str, current_user, payload: FeedbackCreateRequest) -> AnalystFeedback:
        ensure_feedback_request(payload)
        ProjectService(self.session).get_project(project_id, current_user)

        result = None
        dataset_id = None
        original_label = None
        corrected_label = payload.corrected_label.value if payload.corrected_label else None

        if payload.result_id:
            result = self.session.get(FraudResult, payload.result_id)
            if not result or result.dataset.project_id != project_id:
                raise NotFoundError("Fraud result was not found for the current project.")
            dataset_id = result.dataset_id
            original_label = result.predicted_label
            if corrected_label:
                result.feedback_label = corrected_label

        feedback = AnalystFeedback(
            project_id=project_id,
            dataset_id=dataset_id,
            result_id=payload.result_id,
            user_id=current_user.id,
            feedback_type=payload.feedback_type.value,
            original_label=original_label,
            corrected_label=corrected_label,
            notes=payload.notes,
            payload=payload.payload,
        )
        created = self.repository.add(feedback)

        retraining_payload = build_retraining_payload(created, result)
        write_json(Path(project_storage_path(project_id, "feedback", f"{created.id}.json")), retraining_payload)

        self.session.commit()
        self.log_service.record(
            "feedback.recorded",
            "Analyst feedback captured.",
            project_id=project_id,
            user_id=current_user.id,
            details={"feedback_type": created.feedback_type, "result_id": created.result_id},
        )
        return created

    def history(self, project_id: str, current_user) -> list[AnalystFeedback]:
        ProjectService(self.session).get_project(project_id, current_user)
        return self.repository.list_for_project(project_id)