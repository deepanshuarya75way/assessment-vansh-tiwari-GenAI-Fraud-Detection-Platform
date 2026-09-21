from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.analytics.schema import AnalyticsResponse
from app.backend.modules.analytics.service import AnalyticsService
from app.backend.modules.projects.service import ProjectService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/projects/{project_id}/run", response_model=AnalyticsResponse)
def run_analytics(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> AnalyticsResponse:
    ProjectService(session).get_project(project_id, current_user)
    artifact = AnalyticsService(session).generate(project_id)
    return AnalyticsResponse.model_validate(artifact.__dict__)
