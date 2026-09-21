from app.backend.common.schemas import TimestampedResponse


class DashboardResponse(TimestampedResponse):
    project_id: str
    payload: dict
