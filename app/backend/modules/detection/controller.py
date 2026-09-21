from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.detection.schema import FraudResultResponse
from app.backend.modules.detection.service import DetectionService
from app.backend.modules.projects.service import ProjectService

router = APIRouter(prefix="/detection", tags=["detection"])


class DetectionArtifactResponse(BaseModel):
    project_id: str
    dataset_id: str
    strategy: str
    metrics: dict
    thresholds: dict[str, float]
    total_records: int
    fraud_count: int
    review_count: int
    safe_count: int


@router.post("/projects/{project_id}/run", response_model=DetectionArtifactResponse)
def run_detection(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> DetectionArtifactResponse:
    ProjectService(session).get_project(project_id, current_user)
    artifact = DetectionService(session).run(project_id)
    return DetectionArtifactResponse.model_validate(artifact.__dict__)


@router.get("/projects/{project_id}/results", response_model=list[FraudResultResponse])
def list_results(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[FraudResultResponse]:
    ProjectService(session).get_project(project_id, current_user)
    results = DetectionService(session).list_results(project_id)
    return [FraudResultResponse.model_validate(item) for item in results]
