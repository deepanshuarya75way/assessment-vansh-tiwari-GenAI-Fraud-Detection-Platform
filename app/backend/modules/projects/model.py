from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.backend.core.enums import ProjectStatus
from app.backend.db.base import Base


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, native_enum=False),
        default=ProjectStatus.CREATED,
        nullable=False,
    )

    owner = relationship("User", back_populates="projects")
    uploads = relationship("UploadRecord", back_populates="project")
    datasets = relationship("DatasetRecord", back_populates="project")
    dashboards = relationship("DashboardSnapshot", back_populates="project")
    reports = relationship("ReportArtifact", back_populates="project")
    chats = relationship("ChatMessage", back_populates="project")
    feedback_entries = relationship("AnalystFeedback", back_populates="project")
    logs = relationship("AppLog", back_populates="project")
