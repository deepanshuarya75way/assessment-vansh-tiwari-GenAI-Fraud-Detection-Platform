from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.modules.settings.schema import SettingsPayload, SettingsResponse
from app.backend.modules.settings.service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/me", response_model=SettingsResponse)
def get_my_settings(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> SettingsResponse:
    service = SettingsService(session)
    return SettingsResponse.model_validate(service.get_or_create(current_user))


@router.put("/me", response_model=SettingsResponse)
def update_my_settings(
    payload: SettingsPayload,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> SettingsResponse:
    service = SettingsService(session)
    return SettingsResponse.model_validate(service.update(current_user, payload))
