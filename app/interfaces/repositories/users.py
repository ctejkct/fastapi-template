"""User repository and cache interfaces."""

from abc import ABC, abstractmethod
from typing import Optional

from app.interfaces.repositories.base import IRepository
from app.schemas.users import UserResponse


class IUserRepository(IRepository[UserResponse], ABC):
    """User repository contract."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get a user by email."""

    @abstractmethod
    async def get_hashed_password(self, user_id: str) -> Optional[str]:
        """Get the stored password hash for a user."""


class IUserCacheRepository(ABC):
    """Redis-backed user cache contract."""

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """Get a cached user."""

    @abstractmethod
    async def set_user(self, user: UserResponse) -> None:
        """Cache a user payload."""

    @abstractmethod
    async def invalidate_user(self, user_id: str) -> None:
        """Invalidate a cached user."""
