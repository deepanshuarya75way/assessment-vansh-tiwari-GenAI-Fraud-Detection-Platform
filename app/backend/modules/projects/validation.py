from app.backend.core.exceptions import AuthorizationError
from app.backend.db.enterprise_models import User, Project


def ensure_project_owner(project: Project, user: User) -> None:
    if project.owner_id != user.id and user.role != "admin":
        raise AuthorizationError("You do not have access to this project.")
