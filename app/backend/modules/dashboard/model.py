from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.backend.db.base import Base


class DashboardSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "dashboard"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    project = relationship("Project", back_populates="dashboards")
