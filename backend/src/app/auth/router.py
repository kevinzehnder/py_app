"""Auth endpoints."""

from datetime import datetime, timedelta, timezone

import bcrypt
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, User
from app.core.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = structlog.get_logger(__name__)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Demo user — no database. Replace with a DB lookup when you need real users.
# Credentials are read from settings so they can be overridden via env vars.
# ---------------------------------------------------------------------------

_demo_hash: bytes | None = None


def _get_demo_hash() -> bytes:
    global _demo_hash
    if _demo_hash is None:
        settings = get_settings()
        _demo_hash = bcrypt.hashpw(settings.DEMO_PASSWORD.encode(), bcrypt.gensalt())
    return _demo_hash


def _check_demo(email: str, password: str) -> bool:
    settings = get_settings()
    return email == settings.DEMO_EMAIL and bcrypt.checkpw(password.encode(), _get_demo_hash())


def _create_token(email: str, name: str, role: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": email, "name": name, "role": role, "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    settings = get_settings()
    if not _check_demo(form.username, form.password):
        logger.warning("login failed", username=form.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = _create_token(email=settings.DEMO_EMAIL, name=settings.DEMO_NAME, role=settings.DEMO_ROLE)
    logger.info("login success", email=settings.DEMO_EMAIL)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=User)
def me(user: CurrentUser) -> User:
    return user
