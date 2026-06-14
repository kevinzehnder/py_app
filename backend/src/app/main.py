from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Configure logging before any app imports — ensures correct format in all
# processes, including uvicorn reload workers that never run __main__.py.
from app.core.logs import configure_logging, get_log_format_from_env, get_log_level_from_env

configure_logging(format=get_log_format_from_env(), log_level=get_log_level_from_env())

import fastapi
import structlog
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.auth.router import router as auth_router
from app.items.router import router as items_router
from app.middlewares import LoggerMiddleware
from app.schemas import KyException


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> AsyncGenerator:
    import app.database as db
    from app.auth.providers import get_provider

    logger = structlog.get_logger().bind(context="main")
    logger.info("starting application")
    provider = get_provider()
    await provider.startup()
    logger.info("auth provider ready", provider=type(provider).__name__)
    yield
    db.close_client()
    logger.info("shutting down application")


app = fastapi.FastAPI(
    title="Admin Template",
    description="FastAPI + React admin panel template",
    lifespan=lifespan,
    version="0.1.0",
    contact={"name": "Kevin Zehnder", "email": "kevin.zehnder@pm.me"},
    openapi_tags=[
        {"name": "items", "description": "Example CRUD resource"},
        {"name": "auth", "description": "Authentication"},
    ],
)

app.include_router(items_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

if __debug__:
    app.add_middleware(LoggerMiddleware)

logger = structlog.get_logger().bind(context="main")


@app.get("/health", tags=["default"])
def health() -> dict:
    return {"status": "ok"}


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, err: ValidationError) -> JSONResponse:
    logger.info("validation error", detail=err.errors())
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"error": "ValidationError", "detail": err.errors()}),
    )


@app.exception_handler(KyException)
async def kyexception_handler(request: Request, err: KyException) -> None:
    logger.info(
        "KyException",
        message=err.message,
        code=err.code,
        cause=repr(err.__cause__),
        path=str(request.url),
    )
    raise err.response()
