from sqlalchemy import desc, select

from app.backend.common.repository import BaseRepository
from app.backend.db.enterprise_models import AnalystFeedback


class FeedbackRepository(BaseRepository[AnalystFeedback]):
    model = AnalystFeedback

    def list_for_project(self, project_id: str) -> list[AnalystFeedback]:
        stmt = select(AnalystFeedback).where(AnalystFeedback.project_id == project_id).order_by(desc(AnalystFeedback.created_at))
        return list(self.session.scalars(stmt))

    def latest_for_project(self, project_id: str) -> AnalystFeedback | None:
        stmt = select(AnalystFeedback).where(AnalystFeedback.project_id == project_id).order_by(desc(AnalystFeedback.created_at))
        return self.session.scalar(stmt)