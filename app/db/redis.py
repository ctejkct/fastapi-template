"""Redis client management."""

from redis.asyncio import Redis

from app.config.settings import get_settings

_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """Return a singleton Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def check_redis_connection() -> bool:
    """Verify that Redis responds to ping."""
    try:
        client = get_redis_client()
        await client.ping()
        return True
    except Exception:
        return False


async def close_redis_client() -> None:
    """Close the Redis connection pool."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
