"""Authentication schemas."""

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema
from app.schemas.users import UserResponse


class RegistrationRequest(BaseSchema):
    """Registration request schema."""

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseSchema):
    """Login request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class AuthResponse(BaseSchema):
    """Authentication response schema."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
