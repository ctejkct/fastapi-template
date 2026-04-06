"""User endpoint tests with dependency overrides."""

from app.api.v1.endpoints.users import get_users_service
from app.schemas.users import UserCreateRequest, UserResponse, UserUpdateRequest


class StubUsersService:
    """Stub user service for endpoint tests."""

    async def create_user(self, request: UserCreateRequest) -> UserResponse:
        return UserResponse(id="user-1", email=request.email, full_name=request.full_name, is_active=True)

    async def get_user(self, user_id: str) -> UserResponse:
        return UserResponse(
            id=user_id,
            email="user@example.com",
            full_name="Template User",
            is_active=True,
        )

    async def list_users(self, limit: int = 100):
        return [await self.get_user("user-1")]

    async def update_user(self, user_id: str, request: UserUpdateRequest) -> UserResponse:
        return UserResponse(
            id=user_id,
            email="user@example.com",
            full_name=request.full_name or "Template User",
            is_active=True if request.is_active is None else request.is_active,
        )


def test_create_user_endpoint(client, app):
    app.dependency_overrides[get_users_service] = lambda: StubUsersService()
    response = client.post(
        "/api/v1/users",
        json={"email": "user@example.com", "full_name": "Template User", "password": "password123"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["data"]["email"] == "user@example.com"
