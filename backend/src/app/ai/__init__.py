"""AI module — minimal pydantic-ai integration over Azure OpenAI.

Optional feature: requires the ``ai`` extra (``uv sync --extra ai``) and the
``AZURE_OPENAI_*`` settings. Not wired into any router yet.

Separation of concerns:
- ``schemas``  — structured output models
- ``agent``   — Azure OpenAI model/provider + Agent construction
- ``service`` — high-level task functions (the "hello world" entry point)
- ``agobis``  — AGOBIS Grundbuch RTF fetch (pi-tools; no pydantic-ai dependency)

``hello_world``/``Greeting`` are imported lazily so that importing this package
(e.g. for the AGOBIS task) does not require the optional ``ai`` extra.
"""

from typing import TYPE_CHECKING, Any

from app.ai.agobis import RtfResult, fetch_grundstueck_rtf

if TYPE_CHECKING:
    from app.ai.schemas import Greeting
    from app.ai.service import hello_world

__all__ = ["Greeting", "RtfResult", "fetch_grundstueck_rtf", "hello_world"]


def __getattr__(name: str) -> Any:
    """Lazily resolve pydantic-ai-backed symbols (optional ``ai`` extra)."""
    if name == "hello_world":
        from app.ai.service import hello_world

        return hello_world
    if name == "Greeting":
        from app.ai.schemas import Greeting

        return Greeting
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
