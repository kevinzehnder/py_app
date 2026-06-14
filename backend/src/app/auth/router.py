"""JWT authentication router."""

from datetime import datetime, timedelta, timezone

import bcrypt
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = structlog.get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    subject: str
    email: str
    name: str
    role: str


def _hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def _check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)


# TODO: replace with DB lookup
_DEMO_PASSWORD_HASH: bytes | None = None


def _get_demo_hash() -> bytes:
    """Lazy-init the demo password hash to avoid slow import-time hashing."""
    global _DEMO_PASSWORD_HASH
    if _DEMO_PASSWORD_HASH is None:
        _DEMO_PASSWORD_HASH = _hash_password("secret")
    return _DEMO_PASSWORD_HASH


DEMO_USER = {
    "email": "admin@example.com",
    "name": "Admin",
    "role": "admin",
}


def create_access_token(data: dict) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {**data, "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_current_user(token: str = Depends(oauth2_scheme)) -> MeResponse:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        email: str = payload.get("sub", "")
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    return MeResponse(
        subject=email,
        email=email,
        name=payload.get("name", ""),
        role=payload.get("role", "viewer"),
    )


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    # TODO: replace with DB lookup
    user = DEMO_USER
    if form.username != user["email"] or not _check_password(form.password, _get_demo_hash()):
        logger.warning("login failed", username=form.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )

    token = create_access_token({
        "sub": user["email"],
        "name": user["name"],
        "role": user["role"],
    })
    logger.info("login success", email=user["email"])
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(current_user: MeResponse = Depends(get_current_user)) -> MeResponse:
    return current_user
