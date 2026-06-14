"""Azure AD provider — single-tenant OAuth2 via fastapi_azure_auth.

Requires: pip install "app[azure]"

Validates RS256 JWTs issued by Azure Entra ID. JWKS/OpenID config loaded on startup.
Roles must be assigned as Azure AD App Roles and will appear in the token's "roles" claim.
"""

import structlog
from fastapi import Depends

from app.auth.dependencies import User

logger = structlog.get_logger(__name__)


class AzureADProvider:
    def __init__(self, app_client_id: str, tenant_id: str) -> None:
        try:
            from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer  # type: ignore[import]
        except ImportError as e:
            raise ImportError(
                'Azure AD provider requires fastapi-azure-auth. '
                'Install with: pip install "app[azure]"'
            ) from e

        self._scheme = SingleTenantAzureAuthorizationCodeBearer(
            app_client_id=app_client_id,
            tenant_id=tenant_id,
            scopes={f"api://{app_client_id}/user_impersonation": "user_impersonation"},
        )

    async def startup(self) -> None:
        await self._scheme.openid_config.load_config()
        logger.info("azure ad openid config loaded")

    def create_dependency(self):
        scheme = self._scheme

        async def get_current_user(azure_user=Depends(scheme)) -> User:
            claims = azure_user.claims if hasattr(azure_user, "claims") else {}
            roles = getattr(azure_user, "roles", None) or claims.get("roles", [])
            return User(
                subject=getattr(azure_user, "oid", claims.get("oid", claims.get("sub", ""))),
                email=getattr(azure_user, "preferred_username", None)
                    or claims.get("email", ""),
                name=getattr(azure_user, "name", None) or claims.get("name", ""),
                roles=roles if isinstance(roles, list) else [roles],
            )

        return get_current_user
