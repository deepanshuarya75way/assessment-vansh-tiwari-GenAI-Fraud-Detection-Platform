from sqlalchemy.orm import Session

from app.backend.core.exceptions import ConflictError
from app.backend.modules.auth.repository import UserRepository


def ensure_email_available(session: Session, email: str) -> None:
    repository = UserRepository(session)
    if repository.find_by_email(email):
        raise ConflictError(f"User with email '{email}' already exists.")
