from sqlalchemy import desc, select

from app.backend.common.repository import BaseRepository
from app.backend.db.enterprise_models import DashboardSnapshot


class DashboardRepository(BaseRepository[DashboardSnapshot]):
    model = DashboardSnapshot

    def latest_for_project(self, project_id: str) -> DashboardSnapshot | None:
        stmt = (
            select(DashboardSnapshot)
            .where(DashboardSnapshot.project_id == project_id)
            .order_by(desc(DashboardSnapshot.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)
