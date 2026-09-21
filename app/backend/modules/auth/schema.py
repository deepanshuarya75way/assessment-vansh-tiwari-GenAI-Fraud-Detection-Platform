from pydantic import EmailStr, Field

from app.backend.common.schemas import ORMBaseModel, TimestampedResponse
from app.backend.core.enums import UserRole


class RegisterRequest(ORMBaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=200)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.ANALYST


class LoginRequest(ORMBaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(ORMBaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(TimestampedResponse):
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
