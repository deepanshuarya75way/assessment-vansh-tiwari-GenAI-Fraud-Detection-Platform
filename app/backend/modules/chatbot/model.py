from typing import Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.backend.core.enums import ChatAnswerSource
from app.backend.db.base import Base


class ChatMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chats"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_source: Mapped[str] = mapped_column(String(40), default=ChatAnswerSource.RULE_BASED.value, nullable=False)
    context_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    project = relationship("Project", back_populates="chats")
    user = relationship("User", back_populates="chats")