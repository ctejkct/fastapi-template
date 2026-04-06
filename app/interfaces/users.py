"""User service interface."""

from abc import ABC, abstractmethod
from typing import List

from app.schemas.users import UserCreateRequest, UserResponse, UserUpdateRequest


class IUsersService(ABC):
    """Contract for user management use cases."""

    @abstractmethod
    async def create_user(self, request: UserCreateRequest) -> UserResponse:
        """Create a user."""

    @abstractmethod
    async def get_user(self, user_id: str) -> UserResponse:
        """Fetch a user by id."""

    @abstractmethod
    async def list_users(self, limit: int = 100) -> List[UserResponse]:
        """List users."""

    @abstractmethod
    async def update_user(self, user_id: str, request: UserUpdateRequest) -> UserResponse:
        """Update a user."""
