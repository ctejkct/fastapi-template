"""Async PostgreSQL session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import get_settings

settings = get_settings()

engine_kwargs = {"echo": settings.database_echo, "pool_pre_ping": True}
if not settings.database_url.startswith("sqlite"):
    engine_kwargs["pool_size"] = settings.database_pool_size
    engine_kwargs["max_overflow"] = settings.database_max_overflow

engine = create_async_engine(settings.database_url, **engine_kwargs)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session per request."""
    async with SessionLocal() as session:
        yield session


async def check_database_connection() -> bool:
    """Verify the database is reachable."""
    try:
        async with engine.begin() as connection:
            await connection.run_sync(lambda _: None)
        return True
    except Exception:
        return False


async def close_database_engine() -> None:
    """Dispose the async engine."""
    await engine.dispose()
