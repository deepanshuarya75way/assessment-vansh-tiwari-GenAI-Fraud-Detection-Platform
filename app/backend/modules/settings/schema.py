from pydantic import BaseModel, Field

from app.backend.common.schemas import TimestampedResponse


class SettingsPayload(BaseModel):
    theme: str = Field(default="light")
    notifications_enabled: bool = True
    alert_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    default_page_size: int = Field(default=25, ge=10, le=100)


class SettingsResponse(TimestampedResponse):
    user_id: str
    preferences: dict
