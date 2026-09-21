from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.feedback.schema import FeedbackCreateRequest, FeedbackResponse
from app.backend.modules.feedback.service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/projects/{project_id}", response_model=FeedbackResponse)
def submit_feedback(
    project_id: str,
    payload: FeedbackCreateRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> FeedbackResponse:
    feedback = FeedbackService(session).submit(project_id, current_user, payload)
    return FeedbackResponse.model_validate(feedback)


@router.get("/projects/{project_id}", response_model=list[FeedbackResponse])
def history(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[FeedbackResponse]:
    feedback_items = FeedbackService(session).history(project_id, current_user)
    return [FeedbackResponse.model_validate(item) for item in feedback_items]