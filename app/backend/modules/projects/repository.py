from sqlalchemy import select

from app.backend.common.repository import BaseRepository
from app.backend.db.enterprise_models import Project


class ProjectRepository(BaseRepository[Project]):
    model = Project

    def list_by_owner(self, owner_id: str) -> list[Project]:
        return list(self.session.scalars(select(Project).where(Project.owner_id == owner_id)))
