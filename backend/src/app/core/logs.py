"""Logging configuration."""

from __future__ import annotations

import logging
import logging.config
import os
from typing import Literal

import orjson
import structlog

DEFAULT_NOISY_LOGGERS = {
    "uvicorn": "INFO",
    "uvicorn.error": "INFO",
    "uvicorn.access": "WARNING",
    "httpx": "WARNING",
    "pymongo": "WARNING",
    "urllib3": "WARNING",
}

_configured = False


def orjson_dump_decoded(obj: object, *, default: object) -> str:
    """Serialize log payloads with orjson and return text."""
    return orjson.dumps(
        obj,
        default=default,
        option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
    ).decode("utf-8")


def _normalize_level(log_level: int | str) -> int:
    if isinstance(log_level, int):
        return log_level
    return logging._nameToLevel.get(log_level.upper(), logging.INFO)


def _shared_processors(use_utc: bool) -> list[object]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(
            fmt="iso" if use_utc else "%H:%M:%S",
            utc=use_utc,
        ),
    ]


def configure_logging(
    format: Literal["console", "json"] = "console",
    log_level: int | str = logging.INFO,
    *,
    force: bool = False,
    noisy_loggers: dict[str, int | str] | None = None,
) -> None:
    """Configure stdlib logging and structlog together."""
    global _configured

    if _configured and not force:
        return

    normalized_level = _normalize_level(log_level)
    use_json = format == "json"
    shared_processors = _shared_processors(use_utc=use_json)
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer(serializer=orjson_dump_decoded)
        if use_json
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=[
            *shared_processors,
            structlog.processors.format_exc_info,
        ],
    )

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structlog": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": renderer,
                    "foreign_pre_chain": [
                        *shared_processors,
                        structlog.processors.format_exc_info,
                    ],
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "structlog",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {
                "handlers": ["default"],
                "level": normalized_level,
            },
        }
    )

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)

    configure_foreign_loggers(noisy_loggers or DEFAULT_NOISY_LOGGERS)
    _configured = True


def configure_foreign_loggers(logger_levels: dict[str, int | str]) -> None:
    """Route third-party loggers through root and tame noisy defaults."""
    for logger_name, level in logger_levels.items():
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(_normalize_level(level))


def get_log_format_from_env() -> Literal["console", "json"]:
    """Resolve log format without needing full settings validation."""
    log_format = os.getenv("LOG_FORMAT")
    if log_format in {"console", "json"}:
        return log_format
    if os.getenv("LOG_JSON", "0") in {"1", "true", "TRUE", "yes", "YES"}:
        return "json"
    return "console"


def get_log_level_from_env() -> str:
    """Resolve log level without needing full settings validation."""
    if log_level := os.getenv("LOG_LEVEL"):
        return log_level
    if os.getenv("DEBUG", "0") in {"1", "true", "TRUE", "yes", "YES"}:
        return "DEBUG"
    return "INFO"
