"""Auth dependencies — import these in routers."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel


class User(BaseModel):
    subject: str
    email: str
    name: str
    roles: list[str] = []


def _make_get_current_user():
    from app.auth.providers import get_provider

    return get_provider().create_dependency()


# Assigned at module import — provider factory runs once, returns a FastAPI-
# compatible async callable whose signature FastAPI can introspect for Depends().
get_current_user = _make_get_current_user()


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if "admin" not in user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


# Typed dependency aliases — use these in routers
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
