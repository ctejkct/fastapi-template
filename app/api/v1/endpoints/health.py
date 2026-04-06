"""Health check endpoints."""

from fastapi import APIRouter, status

from app.api.deps import SettingsDep
from app.db.redis import check_redis_connection
from app.db.session import check_database_connection
from app.schemas.common import HealthStatus

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check(settings: SettingsDep) -> HealthStatus:
    """Basic liveness probe."""
    return HealthStatus(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment.value,
    )


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> dict[str, object]:
    """Readiness check for PostgreSQL and Redis."""
    database_healthy = await check_database_connection()
    redis_healthy = await check_redis_connection()

    checks = {
        "postgres": "healthy" if database_healthy else "unhealthy",
        "redis": "healthy" if redis_healthy else "unhealthy",
    }
    overall_status = "ready" if database_healthy and redis_healthy else "not_ready"
    return {"status": overall_status, "checks": checks}
