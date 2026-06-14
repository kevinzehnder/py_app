import logging
import random

import pytest
from fastapi.testclient import TestClient

from app.core.logs import configure_logging

TEST_LOGGER_LEVELS = {
    "uvicorn": "DEBUG",
    "uvicorn.error": "DEBUG",
    "uvicorn.access": "DEBUG",
    "httpx": "DEBUG",
    "httpcore": "DEBUG",
}


def pytest_configure(config: pytest.Config) -> None:
    """Configure structlog before test module import/collection."""
    configure_logging(
        format="console",
        log_level="DEBUG",
        force=True,
        noisy_loggers=TEST_LOGGER_LEVELS,
    )


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale() -> list:
    """set faker to CH"""
    return ["de_CH"]


@pytest.fixture(scope="session", autouse=True)
def faker_seed() -> float:
    """use a fresh random seed every time"""
    return random.random()


@pytest.fixture(autouse=True)
def caplog(caplog):
    """Capture structlog logs with pytest caplog."""
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture(scope="session")
def client() -> TestClient:
    from app.main import app
    return TestClient(app)
