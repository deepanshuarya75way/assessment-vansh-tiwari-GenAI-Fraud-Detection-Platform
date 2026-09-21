from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import Field

from app.backend.common.schemas import ORMBaseModel, TimestampedResponse


class ChatRequest(ORMBaseModel):
    question: str = Field(min_length=2, max_length=4000)
    session_id: str | None = Field(default=None, description="Active analysis session ID; falls back to the route session ID.")


class ChatTurnResponse(TimestampedResponse):
    session_id: str
    user_id: str | None
    question: str
    answer: str
    intent: str
    confidence: float
    summary: str
    important_findings: list[str]
    evidence: list[dict[str, Any]]
    recommendations: list[str]
    next_suggested_questions: list[str]
    visual_response: dict[str, Any]
    context_metadata: dict[str, Any]
    answer_source: str
    chat_message_id: str | None = None


class ChatResponse(TimestampedResponse):
    project_id: str
    user_id: str | None
    question: str
    answer: str
    answer_source: str
    context_payload: dict | None


@dataclass(slots=True)
class ChatConversationArtifact:
    id: str
    session_id: str
    user_id: str | None
    question: str
    answer: str
    intent: str
    confidence: float
    summary: str
    important_findings: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    next_suggested_questions: list[str] = field(default_factory=list)
    visual_response: dict[str, Any] = field(default_factory=dict)
    context_metadata: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    answer_source: str = "dataset_session_grounded"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    chat_message_id: str | None = None