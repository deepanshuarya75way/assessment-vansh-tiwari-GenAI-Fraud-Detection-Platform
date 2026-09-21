from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedResponse(ORMBaseModel):
    id: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    message: str
