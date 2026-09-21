from app.backend.modules.settings.schema import SettingsPayload


def normalize_settings(payload: SettingsPayload) -> dict:
    return payload.model_dump()
