"""Demo auth provider — HS256 JWT with a single hardcoded user.

Uses bcrypt password hashing. Intended for development and template demos only.
Replace with a real user database for production.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.auth.dependencies import User
from app.core.config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class DemoProvider:
    async def startup(self) -> None:
        pass

    def create_dependency(self):
        async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
            settings = get_settings()
            try:
                payload = jwt.decode(
                    token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
                )
            except JWTError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from e

            email: str = payload.get("sub", "")
            # Support both old "role" (str) and new "roles" (list) token claims
            raw_roles = payload.get("roles")
            if raw_roles is None:
                raw_roles = [payload.get("role", "viewer")]

            return User(
                subject=email,
                email=email,
                name=payload.get("name", ""),
                roles=raw_roles,
            )

        return get_current_user
