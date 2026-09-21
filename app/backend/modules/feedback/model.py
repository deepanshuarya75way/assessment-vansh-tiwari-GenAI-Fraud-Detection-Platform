from typing import Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.backend.core.enums import FeedbackType
from app.backend.db.base import Base


class AnalystFeedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "feedback"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    dataset_id: Mapped[str | None] = mapped_column(ForeignKey("datasets.id"), index=True)
    result_id: Mapped[str | None] = mapped_column(ForeignKey("fraud_results.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    feedback_type: Mapped[str] = mapped_column(String(40), nullable=False, default=FeedbackType.LABEL_CORRECTION.value)
    original_label: Mapped[str | None] = mapped_column(String(20))
    corrected_label: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    project = relationship("Project", back_populates="feedback_entries")
    user = relationship("User", back_populates="feedback_entries")