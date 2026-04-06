"""Application settings loaded from environment variables."""

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Supported runtime environments."""

    DEVELOPMENT = "development"
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Central application settings object."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)

    app_name: str = Field(default="FastAPI Template")
    app_version: str = Field(default="0.1.0")
    api_prefix: str = Field(default="/api/v1")

    host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8080)

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/zml_template"
    )
    database_echo: bool = Field(default=False)
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)

    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_default_ttl_seconds: int = Field(default=300)

    jwt_secret_key: str = Field(default="change-me")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=60)

    cors_origins: str = Field(default="http://localhost:3000")
    log_level: str = Field(default="INFO")
    log_json_format: bool = Field(default=False)

    @field_validator("api_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        value = value.strip("\"'")
        if not value.startswith("/"):
            return f"/{value}"
        return value

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        normalized = value.upper()
        if normalized not in valid_levels:
            raise ValueError(f"Invalid log level: {value}. Must be one of {sorted(valid_levels)}")
        return normalized

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


def load_settings_for_environment(env: str | None = None) -> Settings:
    """Load base and environment-specific env files when present."""
    import os

    selected_env = env or os.getenv("ENVIRONMENT", "development")
    env_files = []

    base_env = Path(".env")
    env_specific = Path(f".env.{selected_env}")

    if base_env.exists():
        env_files.append(base_env)
    if env_specific.exists():
        env_files.append(env_specific)

    if env_files:
        return Settings(_env_file=tuple(str(path) for path in env_files))
    return Settings()


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return load_settings_for_environment()


settings = get_settings()
