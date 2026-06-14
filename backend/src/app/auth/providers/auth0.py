"""Auth0 provider — RS256 JWT validation via JWKS endpoint.

Fetches public keys from https://{domain}/.well-known/jwks.json on startup
and validates bearer tokens using python-jose.

Auth0 custom claims (e.g. roles) are often namespaced:
  https://myapp.com/roles → configure AUTH0_ROLES_CLAIM accordingly.
"""

import httpx
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.auth.dependencies import User
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

# tokenUrl left empty — Auth0 issues tokens externally, not via this app
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="", auto_error=True)


class Auth0Provider:
    def __init__(self, domain: str, audience: str, roles_claim: str) -> None:
        self._domain = domain
        self._audience = audience
        self._roles_claim = roles_claim
        self._jwks: dict = {}

    async def startup(self) -> None:
        url = f"https://{self._domain}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            self._jwks = resp.json()
        logger.info("auth0 JWKS loaded", domain=self._domain)

    def create_dependency(self):
        # Capture self — JWKS dict is populated in startup() before any request
        provider = self

        async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
            try:
                payload = jwt.decode(
                    token,
                    provider._jwks,
                    algorithms=["RS256"],
                    audience=provider._audience,
                    issuer=f"https://{provider._domain}/",
                )
            except JWTError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from e

            roles = payload.get(provider._roles_claim, [])
            return User(
                subject=payload["sub"],
                email=payload.get("email", payload["sub"]),
                name=payload.get("name", ""),
                roles=roles if isinstance(roles, list) else [roles],
            )

        return get_current_user
