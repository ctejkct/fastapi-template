"""Authentication service tests."""

from dataclasses import dataclass

import pytest

from app.core.exceptions import UnauthorizedError
from app.core.security import verify_password
from app.schemas.authentication import LoginRequest, RegistrationRequest
from app.schemas.users import UserResponse
from app.services.authentication import AuthenticationService


@dataclass
class InMemoryUser:
    """Small in-memory user store model for tests."""

    id: str
    email: str
    full_name: str
    hashed_password: str
    is_active: bool = True


class FakeUserRepo:
    """Combined auth and user repository for service tests."""

    def __init__(self) -> None:
        self.users_by_id: dict[str, InMemoryUser] = {}
        self.users_by_email: dict[str, InMemoryUser] = {}

    async def get_by_email(self, email: str):
        user = self.users_by_email.get(email)
        if user is None:
            return None
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )

    async def create_credentials_user(self, email: str, full_name: str, hashed_password: str):
        user = InMemoryUser(id="user-1", email=email, full_name=full_name, hashed_password=hashed_password)
        self.users_by_id[user.id] = user
        self.users_by_email[user.email] = user
        return await self.get_by_email(email)

    async def get_hashed_password(self, user_id: str):
        user = self.users_by_id.get(user_id)
        return None if user is None else user.hashed_password

    async def get_by_id(self, user_id: str):
        user = self.users_by_id.get(user_id)
        if user is None:
            return None
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )


class FakeCacheRepo:
    """No-op cache repo for service tests."""

    def __init__(self) -> None:
        self.cache: dict[str, UserResponse] = {}

    async def get_user(self, user_id: str):
        return self.cache.get(user_id)

    async def set_user(self, user: UserResponse) -> None:
        self.cache[user.id] = user

    async def invalidate_user(self, user_id: str) -> None:
        self.cache.pop(user_id, None)


@pytest.mark.asyncio
async def test_register_hashes_password_and_returns_token():
    repo = FakeUserRepo()
    cache_repo = FakeCacheRepo()
    service = AuthenticationService(repo, repo, cache_repo)

    result = await service.register(
        RegistrationRequest(email="user@example.com", full_name="Template User", password="password123")
    )

    assert result.access_token
    stored_user = repo.users_by_id["user-1"]
    assert verify_password("password123", stored_user.hashed_password)


@pytest.mark.asyncio
async def test_login_rejects_invalid_password():
    repo = FakeUserRepo()
    cache_repo = FakeCacheRepo()
    service = AuthenticationService(repo, repo, cache_repo)
    await service.register(
        RegistrationRequest(email="user@example.com", full_name="Template User", password="password123")
    )

    with pytest.raises(UnauthorizedError):
        await service.login(LoginRequest(email="user@example.com", password="wrong-pass"))
