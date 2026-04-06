"""Database initialization helpers."""

from app.db.models import UserORM  # noqa: F401


async def init_db() -> None:
    """Load ORM metadata. Schema changes should be applied with Alembic."""
    return None
