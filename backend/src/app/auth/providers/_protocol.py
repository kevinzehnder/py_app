"""AuthProvider protocol — all providers must implement this interface."""

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.auth.dependencies import User


class AuthProvider(Protocol):
    async def startup(self) -> None:
        """Called once in lifespan before requests are accepted.

        Use for network-bound init (JWKS fetch, OpenID config load).
        No-op for providers that don't need it.
        """
        ...

    def create_dependency(self) -> Callable[..., Awaitable["User"]]:
        """Return a FastAPI-compatible async callable that resolves to User.

        FastAPI introspects the returned function's signature to resolve
        nested Depends() — so the returned function must use real annotations,
        not *args/**kwargs.
        """
        ...
