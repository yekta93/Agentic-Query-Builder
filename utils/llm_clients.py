"""LLM client factory and helpers."""

import os
from typing import Any, Optional

from langchain_openai import ChatOpenAI


def get_llm(
    model: str = "google/gemma-2-27b-it",
    temperature: float = 0.0,
    timeout: int = 60,
) -> ChatOpenAI:
    """
    Create a ChatOpenAI client configured for OpenRouter (or any OpenAI-compatible endpoint).

    Requires OPENROUTER_API_KEY environment variable.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is not set. "
            "Copy .env.example to .env and add your key."
        )

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        timeout=timeout,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/yekta93/Agentic-Query-Builder",
            "X-Title": "Agentic Query Builder",
        },
    )
