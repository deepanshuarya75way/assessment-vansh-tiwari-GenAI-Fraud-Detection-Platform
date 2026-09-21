from sqlalchemy.orm import Session

from app.backend.db.enterprise_models import User, Project
from app.backend.modules.projects.repository import ProjectRepository
from app.backend.modules.projects.schema import ProjectCreateRequest
from app.backend.modules.projects.validation import ensure_project_owner


class ProjectService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ProjectRepository(session)

    def create_project(self, payload: ProjectCreateRequest, current_user: User) -> Project:
        project = Project(
            owner_id=current_user.id,
            name=payload.name,
            description=payload.description,
        )
        created = self.repository.add(project)
        self.session.commit()
        return created

    def list_projects(self, current_user: User) -> list[Project]:
        return self.repository.list_by_owner(current_user.id)

    def get_project(self, project_id: str, current_user: User) -> Project:
        project = self.repository.get(project_id)
        ensure_project_owner(project, current_user)
        return project
