"""Health endpoint tests."""

from unittest.mock import AsyncMock, patch


def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "version" in payload


def test_readiness_check(client):
    with patch("app.api.v1.endpoints.health.check_database_connection", new=AsyncMock(return_value=True)):
        with patch("app.api.v1.endpoints.health.check_redis_connection", new=AsyncMock(return_value=True)):
            response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
