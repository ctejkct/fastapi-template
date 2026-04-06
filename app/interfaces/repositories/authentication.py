"""Authentication repository interfaces."""

from abc import ABC, abstractmethod

from app.schemas.users import UserResponse


class IAuthenticationRepository(ABC):
    """Contract for auth-specific repository operations."""

    @abstractmethod
    async def get_by_email(self, email: str) -> UserResponse | None:
        """Load a user by email."""

    @abstractmethod
    async def create_credentials_user(
        self, email: str, full_name: str, hashed_password: str
    ) -> UserResponse:
        """Create a user during registration."""
