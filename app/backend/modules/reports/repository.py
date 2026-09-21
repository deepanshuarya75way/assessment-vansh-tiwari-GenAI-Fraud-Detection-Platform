from sqlalchemy import desc, select

from app.backend.common.repository import BaseRepository
from app.backend.db.enterprise_models import ReportArtifact


class ReportRepository(BaseRepository[ReportArtifact]):
    model = ReportArtifact

    def list_for_project(self, project_id: str) -> list[ReportArtifact]:
        stmt = select(ReportArtifact).where(ReportArtifact.project_id == project_id).order_by(desc(ReportArtifact.created_at))
        return list(self.session.scalars(stmt))

    def latest_for_project(self, project_id: str) -> ReportArtifact | None:
        stmt = select(ReportArtifact).where(ReportArtifact.project_id == project_id).order_by(desc(ReportArtifact.created_at))
        return self.session.scalar(stmt)