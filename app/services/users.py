"""User service implementation."""

import logging
from typing import List

from app.core.security import hash_password
from app.interfaces.repositories.users import IUserCacheRepository, IUserRepository
from app.interfaces.users import IUsersService
from app.schemas.users import UserCreateRequest, UserResponse, UserUpdateRequest

logger = logging.getLogger(__name__)


class UsersService(IUsersService):
    """User service with cache-aware reads."""

    def __init__(self, repo: IUserRepository, cache_repo: IUserCacheRepository) -> None:
        self.repo = repo
        self.cache_repo = cache_repo

    async def create_user(self, request: UserCreateRequest) -> UserResponse:
        logger.info("Creating user %s", request.email)
        user = await self.repo.create(
            {
                "email": request.email,
                "full_name": request.full_name,
                "hashed_password": hash_password(request.password),
            }
        )
        await self.cache_repo.set_user(user)
        return user

    async def get_user(self, user_id: str) -> UserResponse:
        cached_user = await self.cache_repo.get_user(user_id)
        if cached_user is not None:
            return cached_user

        user = await self.repo.get_by_id_or_raise(user_id)
        await self.cache_repo.set_user(user)
        return user

    async def list_users(self, limit: int = 100) -> List[UserResponse]:
        return await self.repo.get_all(limit=limit)

    async def update_user(self, user_id: str, request: UserUpdateRequest) -> UserResponse:
        user = await self.repo.update(user_id, request.model_dump(exclude_none=True))
        await self.cache_repo.invalidate_user(user_id)
        await self.cache_repo.set_user(user)
        return user
