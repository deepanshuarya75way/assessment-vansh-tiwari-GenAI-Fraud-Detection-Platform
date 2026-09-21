from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.backend.db.base import Base


class ReportArtifact(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reports"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(40), default="pdf_ready_json", nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    project = relationship("Project", back_populates="reports")
