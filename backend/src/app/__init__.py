"""App package init.

Configure logging here so it is set up before any ``app.*`` submodule is
imported — including uvicorn reload workers that import ``app.main:app``
directly and never run ``__main__.py``. ``configure_logging`` is idempotent,
so the later ``bootstrap()`` call is a no-op.
"""

from app.core.logs import (
    configure_logging,
    get_log_format_from_env,
    get_log_level_from_env,
)

configure_logging(
    format=get_log_format_from_env(),
    log_level=get_log_level_from_env(),
)
