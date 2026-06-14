"""Auth provider factory — selects and caches the active provider."""

from app.auth.providers._protocol import AuthProvider

_provider: AuthProvider | None = None


def get_provider() -> AuthProvider:
    """Return the cached auth provider instance, creating it if needed."""
    global _provider
    if _provider is not None:
        return _provider

    from app.core.config import get_settings

    settings = get_settings()

    if settings.AUTH_DISABLED:
        from app.auth.providers.disabled import DisabledProvider

        _provider = DisabledProvider()
    elif settings.AUTH_PROVIDER == "demo":
        from app.auth.providers.demo import DemoProvider

        _provider = DemoProvider()
    elif settings.AUTH_PROVIDER == "azure_ad":
        from app.auth.providers.azure_ad import AzureADProvider

        _provider = AzureADProvider(settings.AZURE_APP_CLIENT_ID, settings.AZURE_TENANT_ID)
    elif settings.AUTH_PROVIDER == "auth0":
        from app.auth.providers.auth0 import Auth0Provider

        _provider = Auth0Provider(
            settings.AUTH0_DOMAIN,
            settings.AUTH0_AUDIENCE,
            settings.AUTH0_ROLES_CLAIM,
        )
    else:
        raise ValueError(f"Unknown AUTH_PROVIDER: {settings.AUTH_PROVIDER!r}")

    return _provider
