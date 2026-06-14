"""Auth endpoints."""

from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, User
from app.core.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = structlog.get_logger(__name__)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Login endpoint — only available when AUTH_PROVIDER=demo
# ---------------------------------------------------------------------------

if get_settings().AUTH_PROVIDER == "demo" and not get_settings().AUTH_DISABLED:
    import bcrypt
    from fastapi.security import OAuth2PasswordRequestForm
    from jose import jwt

    _demo_hash: bytes | None = None

    def _get_demo_hash() -> bytes:
        global _demo_hash
        if _demo_hash is None:
            s = get_settings()
            _demo_hash = bcrypt.hashpw(s.DEMO_PASSWORD.encode(), bcrypt.gensalt())
        return _demo_hash

    def _check_demo(email: str, password: str) -> bool:
        s = get_settings()
        return email == s.DEMO_EMAIL and bcrypt.checkpw(password.encode(), _get_demo_hash())

    def _create_token(email: str, name: str, role: str) -> str:
        s = get_settings()
        expire = datetime.now(timezone.utc) + timedelta(minutes=s.JWT_EXPIRE_MINUTES)
        return jwt.encode(
            {"sub": email, "name": name, "roles": [role], "exp": expire},
            s.JWT_SECRET_KEY,
            algorithm=s.JWT_ALGORITHM,
        )

    @router.post("/login", response_model=TokenResponse)
    def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
        s = get_settings()
        if not _check_demo(form.username, form.password):
            logger.warning("login failed", username=form.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        token = _create_token(email=s.DEMO_EMAIL, name=s.DEMO_NAME, role=s.DEMO_ROLE)
        logger.info("login success", email=s.DEMO_EMAIL)
        return TokenResponse(access_token=token)


# ---------------------------------------------------------------------------
# /me — works for all providers
# ---------------------------------------------------------------------------


@router.get("/me", response_model=User)
def me(user: CurrentUser) -> User:
    return user
