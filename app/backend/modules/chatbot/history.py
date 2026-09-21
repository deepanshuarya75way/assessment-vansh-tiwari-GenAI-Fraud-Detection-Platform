from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.backend.db.enterprise_models import ChatMessage
from app.backend.modules.projects.service import ProjectService


class ConversationHistoryManager:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_turns(self, session_id: str, current_user, limit: int = 20) -> list[dict[str, Any]]:
        ProjectService(self.session).get_project(session_id, current_user)
        stmt = select(ChatMessage).where(ChatMessage.project_id == session_id).order_by(desc(ChatMessage.created_at)).limit(limit)
        messages = list(self.session.scalars(stmt))
        messages.reverse()
        return [self._to_turn(message) for message in messages]

    def latest_turn(self, session_id: str, current_user) -> dict[str, Any] | None:
        ProjectService(self.session).get_project(session_id, current_user)
        stmt = select(ChatMessage).where(ChatMessage.project_id == session_id).order_by(desc(ChatMessage.created_at)).limit(1)
        message = self.session.scalar(stmt)
        return self._to_turn(message) if message else None

    @staticmethod
    def _to_turn(message: ChatMessage) -> dict[str, Any]:
        payload = message.context_payload or {}
        return {
            "id": message.id,
            "session_id": message.project_id,
            "user_id": message.user_id,
            "question": message.question,
            "answer": message.answer,
            "intent": payload.get("intent", "dataset_summary"),
            "confidence": payload.get("confidence", 0.0),
            "summary": payload.get("summary", message.answer),
            "important_findings": payload.get("important_findings", []),
            "evidence": payload.get("evidence", []),
            "recommendations": payload.get("recommendations", []),
            "next_suggested_questions": payload.get("next_suggested_questions", []),
            "visual_response": payload.get("visual_response", {"type": "message"}),
            "context_metadata": payload.get("context_metadata", {}),
            "answer_source": message.answer_source,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "chat_message_id": message.id,
        }