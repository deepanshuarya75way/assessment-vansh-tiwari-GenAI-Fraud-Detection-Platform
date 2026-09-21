from app.backend.db.enterprise_models import User
from app.backend.modules.auth.schema import TokenResponse


def build_token_response(token: str) -> TokenResponse:
    return TokenResponse(access_token=token)


def display_name(user: User) -> str:
    return user.full_name or user.email
