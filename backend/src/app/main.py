from contextlib import asynccontextmanager
from typing import AsyncGenerator

import fastapi
import structlog
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.middlewares import LoggerMiddleware
from app.schemas import KyException
from app.web.router import STATIC_DIR as WEB_STATIC_DIR
from app.web.router import router as web_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> AsyncGenerator:
    import app.database as db
    from app.auth.providers import get_provider

    logger = structlog.get_logger().bind(context="main")
    logger.info("starting application")
    provider = get_provider()
    await provider.startup()
    logger.info("auth provider ready", provider=type(provider).__name__)

    if settings.MONGO_ENABLED:
        db.ensure_connection()
        db.create_collection_indices()

    yield

    if settings.MONGO_ENABLED:
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

app.include_router(auth_router)
app.include_router(web_router)

# The items example CRUD depends on MongoDB — only register it when enabled.
if settings.MONGO_ENABLED:
    from app.items.router import router as items_router

    app.include_router(items_router)

# Server-rendered frontend static assets (CSS/JS/themes/favicon).
app.mount("/web/static", StaticFiles(directory=WEB_STATIC_DIR), name="web-static")

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
