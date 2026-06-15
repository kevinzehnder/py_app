"""Structured output models for the ai module."""

from pydantic import BaseModel, Field


class Greeting(BaseModel):
    """Structured result of the hello-world task."""

    message: str = Field(..., description="A short, friendly greeting.")
    language: str = Field(..., description="Language the greeting is written in.")
