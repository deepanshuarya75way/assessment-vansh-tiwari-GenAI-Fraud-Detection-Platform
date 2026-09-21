from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.explainability.schema import ExplainabilityResponse
from app.backend.modules.explainability.service import ExplainabilityService
from app.backend.modules.projects.service import ProjectService

router = APIRouter(prefix="/explainability", tags=["explainability"])


@router.post("/projects/{project_id}/run", response_model=list[ExplainabilityResponse])
def run_explainability(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[ExplainabilityResponse]:
    ProjectService(session).get_project(project_id, current_user)
    items = ExplainabilityService(session).run(project_id)
    return [ExplainabilityResponse.model_validate(item.__dict__) for item in items]
