from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    project_id: str
    payload: dict
