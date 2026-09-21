from sqlalchemy.orm import Session

from app.backend.core.exceptions import AuthorizationError
from app.backend.core.security import create_access_token, get_password_hash, verify_password
from app.backend.db.enterprise_models import User
from app.backend.modules.auth.repository import UserRepository
from app.backend.modules.auth.schema import LoginRequest, RegisterRequest, TokenResponse
from app.backend.modules.auth.utility import build_token_response
from app.backend.modules.auth.validation import ensure_email_available


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = UserRepository(session)

    def register_user(self, payload: RegisterRequest) -> User:
        ensure_email_available(self.session, payload.email)
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            password_hash=get_password_hash(payload.password),
            role=payload.role,
        )
        created = self.repository.add(user)
        self.session.commit()
        return created

    def authenticate(self, payload: LoginRequest) -> TokenResponse:
        user = self.repository.find_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise AuthorizationError("Invalid email or password.")
        token = create_access_token(user.id)
        return build_token_response(token)

    def get_user(self, user_id: str) -> User:
        return self.repository.get(user_id)
