"""High-level AI task functions."""

from app.ai.agent import get_agent
from app.ai.schemas import Greeting

DEFAULT_PROMPT = "Say hello to the world."


async def hello_world(prompt: str = DEFAULT_PROMPT) -> Greeting:
    """Run the hello-world task against Azure OpenAI and return a Greeting."""
    result = await get_agent().run(prompt)
    return result.output
