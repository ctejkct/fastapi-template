"""Authentication service interface."""

from abc import ABC, abstractmethod

from app.schemas.authentication import AuthResponse, LoginRequest, RegistrationRequest
from app.schemas.users import UserResponse


class IAuthenticationService(ABC):
    """Contract for authentication use cases."""

    @abstractmethod
    async def register(self, request: RegistrationRequest) -> AuthResponse:
        """Register a new user."""

    @abstractmethod
    async def login(self, request: LoginRequest) -> AuthResponse:
        """Authenticate an existing user."""

    @abstractmethod
    async def get_me(self, user_id: str) -> UserResponse:
        """Return the current authenticated user."""
