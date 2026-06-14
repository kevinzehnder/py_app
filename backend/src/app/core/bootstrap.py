"""Application bootstrap helpers."""

from __future__ import annotations

import structlog

from .config import Settings, get_settings
from .logs import configure_logging, get_log_format_from_env, get_log_level_from_env


def bootstrap(*, force_logging: bool = False) -> Settings:
    """Configure logging first, then load validated settings."""
    configure_logging(
        format=get_log_format_from_env(),
        log_level=get_log_level_from_env(),
        force=force_logging,
    )

    logger = structlog.get_logger(__name__)

    try:
        settings = get_settings()
    except Exception:
        logger.exception("configuration error")
        raise

    logger.info("core initialized")
    logger.debug("settings loaded")
    return settings
