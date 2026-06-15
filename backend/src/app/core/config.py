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

    MONGO_ENABLED: bool = True  # set false to run without MongoDB
    MONGO_CONNECTION_STRING: str = "mongodb://root:password@localhost:27017/"
    MONGO_DB_NAME: str = "admin_template"
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = 5_000

    # Auth provider selection
    AUTH_PROVIDER: Literal["demo", "azure_ad", "auth0"] = "demo"
    AUTH_DISABLED: bool = False  # inject fake admin, skip token checks (dev only)

    # Demo provider — HS256 JWT, single hardcoded user
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # Demo user — no DB, override via env vars for real deployments
    DEMO_EMAIL: str = "admin@example.com"
    DEMO_PASSWORD: str = "secret"
    DEMO_NAME: str = "Admin"
    DEMO_ROLE: str = "admin"

    # Azure AD provider
    AZURE_APP_CLIENT_ID: str = ""
    AZURE_TENANT_ID: str = ""

    # Auth0 provider
    AUTH0_DOMAIN: str = ""      # e.g. "myapp.eu.auth0.com"
    AUTH0_AUDIENCE: str = ""
    AUTH0_ROLES_CLAIM: str = "roles"

    # Azure AI Foundry / Azure OpenAI (ai module) — API-key auth
    AZURE_OPENAI_ENDPOINT: str = ""          # e.g. "https://my-res.openai.azure.com/openai/v1/"
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = ""       # optional for legacy non-v1 endpoints
    AZURE_OPENAI_DEPLOYMENT: str = ""        # deployment name, e.g. "gpt-5-mini"

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
