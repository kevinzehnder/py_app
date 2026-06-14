"""Application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and `.env`."""

    APP_NAME: str = "admin-template"
    ENVIRONMENT: Literal["dev", "staging", "prod"] = "dev"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"

    MONGO_CONNECTION_STRING: str = "mongodb://root:password@localhost:27017/"
    MONGO_DB_NAME: str = "admin_template"
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = 5_000

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # Demo user — no DB, override via env vars for real deployments
    DEMO_EMAIL: str = "admin@example.com"
    DEMO_PASSWORD: str = "secret"
    DEMO_NAME: str = "Admin"
    DEMO_ROLE: str = "admin"

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()  # pyright: ignore[reportCallIssue]
