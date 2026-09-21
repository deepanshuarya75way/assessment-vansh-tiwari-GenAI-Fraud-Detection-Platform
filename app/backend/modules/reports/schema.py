from app.backend.common.schemas import TimestampedResponse


class ReportResponse(TimestampedResponse):
    project_id: str
    report_type: str
    payload: dict
