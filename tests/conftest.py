"""Pytest fixtures for the template repository."""

import os
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ["ENVIRONMENT"] = "local"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["JWT_SECRET_KEY"] = "test-secret"


@pytest.fixture(scope="session")
def app():
    """Create a test app with startup side effects disabled."""
    with patch("app.main.init_db", new=AsyncMock()):
        from app.main import create_application

        yield create_application()


@pytest.fixture(scope="session")
def client(app) -> Generator[TestClient, None, None]:
    """Yield a synchronous test client."""
    with TestClient(app) as test_client:
        yield test_client
