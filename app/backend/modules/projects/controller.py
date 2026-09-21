from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.projects.schema import ProjectCreateRequest, ProjectResponse
from app.backend.modules.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ProjectResponse:
    service = ProjectService(session)
    return ProjectResponse.model_validate(service.create_project(payload, current_user))


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[ProjectResponse]:
    service = ProjectService(session)
    return [ProjectResponse.model_validate(project) for project in service.list_projects(current_user)]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ProjectResponse:
    service = ProjectService(session)
    return ProjectResponse.model_validate(service.get_project(project_id, current_user))
