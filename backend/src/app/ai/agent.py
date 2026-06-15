"""Azure OpenAI model + Agent construction.

Builds a pydantic-ai ``Agent`` backed by Azure OpenAI using API-key auth.
Settings are read from ``app.core.config`` (``AZURE_OPENAI_*``).
"""

from functools import lru_cache

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

from app.ai.schemas import Greeting
from app.core.config import get_settings

INSTRUCTIONS = (
    "You are a concise assistant. Respond to the user's request with a single "
    "short, friendly greeting and report the language you used."
)


def _build_model() -> OpenAIChatModel:
    """Construct the Azure OpenAI chat model from settings.

    Raises ValueError if the required Azure settings are missing, so misconfig
    fails loudly instead of at request time.
    """
    settings = get_settings()
    missing = [
        name
        for name, value in (
            ("AZURE_OPENAI_ENDPOINT", settings.AZURE_OPENAI_ENDPOINT),
            ("AZURE_OPENAI_API_KEY", settings.AZURE_OPENAI_API_KEY),
            ("AZURE_OPENAI_DEPLOYMENT", settings.AZURE_OPENAI_DEPLOYMENT),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"Azure OpenAI is not configured; missing: {', '.join(missing)}")

    provider_kwargs = {
        "azure_endpoint": settings.AZURE_OPENAI_ENDPOINT,
        "api_key": settings.AZURE_OPENAI_API_KEY,
    }
    if settings.AZURE_OPENAI_API_VERSION:
        provider_kwargs["api_version"] = settings.AZURE_OPENAI_API_VERSION

    provider = AzureProvider(**provider_kwargs)
    # For Azure, the model name is the deployment name.
    return OpenAIChatModel(settings.AZURE_OPENAI_DEPLOYMENT, provider=provider)


@lru_cache
def get_agent() -> Agent[None, Greeting]:
    """Return the cached hello-world agent."""
    return Agent(
        _build_model(),
        output_type=Greeting,
        instructions=INSTRUCTIONS,
    )
