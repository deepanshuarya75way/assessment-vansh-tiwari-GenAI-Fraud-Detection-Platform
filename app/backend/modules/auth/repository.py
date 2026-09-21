from sqlalchemy import select

from app.backend.common.repository import BaseRepository
from app.backend.db.enterprise_models import User


class UserRepository(BaseRepository[User]):
    model = User

    def find_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))
