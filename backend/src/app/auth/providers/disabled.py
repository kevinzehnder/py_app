"""Disabled auth provider — injects a fake admin user, skips all token checks.

Only active when AUTH_DISABLED=1. Never use in production.
"""

import structlog

from app.auth.dependencies import User

logger = structlog.get_logger(__name__)


async def _fake_admin() -> User:
    return User(subject="debug", email="debug@local", name="Debug Admin", roles=["admin"])


class DisabledProvider:
    async def startup(self) -> None:
        logger.warning("auth disabled — all requests will be authenticated as debug admin")

    def create_dependency(self):
        return _fake_admin
