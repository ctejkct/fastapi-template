"""Redis-backed user cache repository."""

import json
from typing import Optional

from redis.asyncio import Redis

from app.config.settings import get_settings
from app.core.exceptions import ExternalServiceError
from app.interfaces.repositories.users import IUserCacheRepository
from app.schemas.users import UserResponse


class UserCacheRepository(IUserCacheRepository):
    """Simple read-through cache for user payloads."""

    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client
        self.settings = get_settings()

    def _key(self, user_id: str) -> str:
        return f"user:{user_id}"

    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        try:
            raw_value = await self.redis.get(self._key(user_id))
            if raw_value is None:
                return None
            return UserResponse.model_validate(json.loads(raw_value))
        except Exception as exc:
            raise ExternalServiceError(detail=f"Redis read failed: {exc}") from exc

    async def set_user(self, user: UserResponse) -> None:
        try:
            await self.redis.set(
                self._key(user.id),
                user.model_dump_json(),
                ex=self.settings.redis_default_ttl_seconds,
            )
        except Exception as exc:
            raise ExternalServiceError(detail=f"Redis write failed: {exc}") from exc

    async def invalidate_user(self, user_id: str) -> None:
        try:
            await self.redis.delete(self._key(user_id))
        except Exception as exc:
            raise ExternalServiceError(detail=f"Redis delete failed: {exc}") from exc
