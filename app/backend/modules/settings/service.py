from sqlalchemy.orm import Session

from app.backend.db.enterprise_models import User, UserSetting
from app.backend.modules.settings.repository import SettingsRepository
from app.backend.modules.settings.schema import SettingsPayload
from app.backend.modules.settings.utility import default_preferences
from app.backend.modules.settings.validation import normalize_settings


class SettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = SettingsRepository(session)

    def get_or_create(self, user: User) -> UserSetting:
        record = self.repository.find_by_user(user.id)
        if record:
            return record
        record = UserSetting(user_id=user.id, preferences=default_preferences())
        created = self.repository.add(record)
        self.session.commit()
        return created

    def update(self, user: User, payload: SettingsPayload) -> UserSetting:
        record = self.get_or_create(user)
        record.preferences = normalize_settings(payload)
        self.session.commit()
        self.session.refresh(record)
        return record
