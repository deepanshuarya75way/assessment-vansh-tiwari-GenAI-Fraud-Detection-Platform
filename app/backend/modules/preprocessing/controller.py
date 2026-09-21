from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.preprocessing.schema import PreprocessingResponse
from app.backend.modules.preprocessing.service import PreprocessingService
from app.backend.modules.projects.service import ProjectService

router = APIRouter(prefix="/preprocessing", tags=["preprocessing"])


@router.post("/projects/{project_id}/run", response_model=PreprocessingResponse)
def run_preprocessing(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> PreprocessingResponse:
    ProjectService(session).get_project(project_id, current_user)
    artifact = PreprocessingService(session).prepare(project_id)
    return PreprocessingResponse(
        original_feature_columns=artifact.original_feature_columns,
        numeric_columns=artifact.numeric_columns,
        categorical_columns=artifact.categorical_columns,
        feature_names=artifact.feature_names,
        label_column=artifact.label_column,
        transformer_path=artifact.transformer_path,
        engineered_frame_path=artifact.engineered_frame_path,
    )
