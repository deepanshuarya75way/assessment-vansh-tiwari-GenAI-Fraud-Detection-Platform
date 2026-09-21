from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.backend.core.config import get_settings
from app.backend.core.security import decode_access_token
from app.backend.db.session import get_db_session
from app.backend.db.enterprise_models import User
from app.backend.modules.auth.service import AuthService

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db_session),
) -> User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    try:
        return AuthService(session).get_user(user_id)
    except Exception as exc:  # pragma: no cover - mapped to HTTP for runtime safety
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user was not found.") from exc