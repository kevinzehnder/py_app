"""AI module — minimal pydantic-ai integration over Azure OpenAI.

Optional feature: requires the ``ai`` extra (``uv sync --extra ai``) and the
``AZURE_OPENAI_*`` settings. Not wired into any router yet.

Separation of concerns:
- ``schemas``  — structured output models
- ``agent``   — Azure OpenAI model/provider + Agent construction
- ``service`` — high-level task functions (the "hello world" entry point)
"""

from app.ai.schemas import Greeting
from app.ai.service import hello_world

__all__ = ["Greeting", "hello_world"]
