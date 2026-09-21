from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.projects.service import ProjectService
from app.backend.modules.uploads.schema import DatasetPreviewResponse, DatasetResponse, UploadResponse
from app.backend.modules.uploads.service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post(
    "/projects/{project_id}",
    status_code=status.HTTP_201_CREATED,
)
async def upload_project_files(
    project_id: str,
    files: list[UploadFile] = File(...),
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> dict:
    project_service = ProjectService(session)
    project = project_service.get_project(project_id, current_user)
    upload_service = UploadService(session)
    upload_records, dataset, preview = await upload_service.upload_files(project, files)
    return {
        "uploads": [UploadResponse.model_validate(item).model_dump() for item in upload_records],
        "dataset": DatasetResponse.model_validate(dataset).model_dump(),
        "preview": DatasetPreviewResponse(columns=preview["columns"], rows=preview["preview"]).model_dump(),
    }


@router.get("/projects/{project_id}", response_model=list[UploadResponse])
def list_project_uploads(
    project_id: str,
    _: object = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[UploadResponse]:
    service = UploadService(session)
    return [UploadResponse.model_validate(item) for item in service.list_uploads(project_id)]


@router.get("/projects/{project_id}/dataset", response_model=DatasetResponse)
def latest_dataset(
    project_id: str,
    _: object = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> DatasetResponse:
    service = UploadService(session)
    return DatasetResponse.model_validate(service.latest_dataset(project_id))
