"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.core.security import decode_access_token
from app.db.redis import get_redis_client
from app.db.session import get_db_session
from app.repositories.user_cache_repository import UserCacheRepository
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_settings_dependency() -> Settings:
    """Resolve settings for dependency injection."""
    return get_settings()


async def get_db() -> AsyncSession:
    """Resolve the request database session."""
    async for session in get_db_session():
        yield session


def get_user_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    """Resolve the user repository."""
    return UserRepository(session)


def get_user_cache_repository() -> UserCacheRepository:
    """Resolve the Redis-backed user cache repository."""
    return UserCacheRepository(get_redis_client())


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    """Resolve the authenticated user id from the bearer token."""
    from app.core.exceptions import UnauthorizedError

    if credentials is None:
        raise UnauthorizedError(detail="Missing bearer token")

    payload = decode_access_token(credentials.credentials)
    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError(detail="Token subject is missing")
    return str(subject)


SettingsDep = Annotated[Settings, Depends(get_settings_dependency)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserIdDep = Annotated[str, Depends(get_current_user_id)]
