import time

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class LoggerMiddleware(BaseHTTPMiddleware):
    """Request timing and logging middleware."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        logger = structlog.get_logger()
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception:
            total_time = 1000 * (time.time() - start_time)
            logger.error(
                "unhandled exception",
                path=str(request.url.path),
                method=request.method,
                exc_info=True,
                elapsed_ms=f"{total_time:.2f}",
            )
            raise

        total_time = 1000 * (time.time() - start_time)

        if response.status_code in (200, 201):
            logger.info(
                "request",
                path=str(request.url.path),
                method=request.method,
                status=response.status_code,
                elapsed_ms=f"{total_time:.2f}",
            )
        else:
            logger.info(
                "request",
                path=str(request.url.path),
                method=request.method,
                status=response.status_code,
                elapsed_ms=f"{total_time:.2f}",
            )

        return response
