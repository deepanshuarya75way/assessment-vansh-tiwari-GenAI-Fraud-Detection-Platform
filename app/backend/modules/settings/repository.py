from sqlalchemy import select

from app.backend.common.repository import BaseRepository
from app.backend.db.enterprise_models import UserSetting


class SettingsRepository(BaseRepository[UserSetting]):
    model = UserSetting

    def find_by_user(self, user_id: str) -> UserSetting | None:
        return self.session.scalar(select(UserSetting).where(UserSetting.user_id == user_id))
