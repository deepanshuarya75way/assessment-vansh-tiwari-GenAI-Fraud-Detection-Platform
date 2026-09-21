from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.projects.service import ProjectService
from app.backend.modules.validation.schema import ValidationResponse
from app.backend.modules.validation.service import ValidationService

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("/projects/{project_id}/run", response_model=ValidationResponse)
def run_validation(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ValidationResponse:
    ProjectService(session).get_project(project_id, current_user)
    service = ValidationService(session)
    return ValidationResponse.model_validate(service.run(project_id))
