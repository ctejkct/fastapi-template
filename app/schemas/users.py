"""User schemas."""

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema, TimestampMixin


class UserCreateRequest(BaseSchema):
    """Request schema for user creation."""

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdateRequest(BaseSchema):
    """Request schema for user updates."""

    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    is_active: bool | None = None


class UserResponse(TimestampMixin):
    """User response schema."""

    id: str
    email: EmailStr
    full_name: str
    is_active: bool
