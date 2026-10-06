from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedResponse(ORMBaseModel):
    id: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    message: str



class FeedbackCreate(ORMBaseModel):
    prediction_id: str
    prediction_label: int = Field(..., ge=0, le=1)
    actual_label: int = Field(..., ge=0, le=1)
    analyst_id: str
    features: dict[str, object]
    class FeedbackResponse(FeedbackCreate, TimestampedResponse):
        is_valid: bool = True
