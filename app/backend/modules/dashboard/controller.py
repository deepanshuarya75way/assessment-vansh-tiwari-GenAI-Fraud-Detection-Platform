from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.dashboard.schema import DashboardResponse
from app.backend.modules.dashboard.service import DashboardService
from app.backend.modules.projects.service import ProjectService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/projects/{project_id}/generate", response_model=DashboardResponse)
def generate_dashboard(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> DashboardResponse:
    ProjectService(session).get_project(project_id, current_user)
    return DashboardResponse.model_validate(DashboardService(session).generate(project_id))


@router.get("/projects/{project_id}", response_model=DashboardResponse | None)
def get_dashboard(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> DashboardResponse | None:
    ProjectService(session).get_project(project_id, current_user)
    dashboard = DashboardService(session).latest(project_id)
    return DashboardResponse.model_validate(dashboard) if dashboard else None
