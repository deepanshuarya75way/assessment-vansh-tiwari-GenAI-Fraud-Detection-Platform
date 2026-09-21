from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.reports.schema import ReportResponse
from app.backend.modules.reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/projects/{project_id}/generate", response_model=ReportResponse)
def generate_report(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ReportResponse:
    report = ReportService(session).generate(project_id, current_user)
    return ReportResponse.model_validate(report)


@router.get("/projects/{project_id}/latest", response_model=ReportResponse | None)
def latest_report(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ReportResponse | None:
    report = ReportService(session).latest(project_id)
    return ReportResponse.model_validate(report) if report else None
