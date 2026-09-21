from pydantic import Field

from app.backend.common.schemas import ORMBaseModel, TimestampedResponse
from app.backend.core.enums import ProjectStatus


class ProjectCreateRequest(ORMBaseModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class ProjectResponse(TimestampedResponse):
    owner_id: str
    name: str
    description: str | None
    status: ProjectStatus
