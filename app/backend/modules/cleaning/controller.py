from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.cleaning.schema import CleanedDataResponse
from app.backend.modules.cleaning.service import CleaningService
from app.backend.modules.projects.service import ProjectService

router = APIRouter(prefix="/cleaning", tags=["cleaning"])


@router.post("/projects/{project_id}/run", response_model=CleanedDataResponse)
def run_cleaning(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> CleanedDataResponse:
    ProjectService(session).get_project(project_id, current_user)
    service = CleaningService(session)
    return CleanedDataResponse.model_validate(service.run(project_id))


@router.get("/projects/{project_id}", response_model=CleanedDataResponse | None)
def latest_cleaned_data(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> CleanedDataResponse | None:
    ProjectService(session).get_project(project_id, current_user)
    service = CleaningService(session)
    record = service.latest(project_id)
    return CleanedDataResponse.model_validate(record) if record else None
