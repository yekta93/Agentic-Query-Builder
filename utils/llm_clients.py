"""LLM client factory and helpers."""

import os
from typing import Type

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


def has_api_key() -> bool:
    """Return True if an OpenRouter (or compatible) API key is available."""
    return bool(os.getenv("OPENROUTER_API_KEY"))


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
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/yekta93/Agentic-Query-Builder",
            "X-Title": "Agentic Query Builder",
        },
    )


def create_structured_chain(
    model: str,
    system_prompt: str,
    user_prompt: str,
    output_model: Type[BaseModel],
    temperature: float = 0.0,
    timeout: int = 60,
):
    """
    Create a LangChain chain that returns a structured Pydantic object.
    """
    llm = get_llm(model=model, temperature=temperature, timeout=timeout)
    structured_llm = llm.with_structured_output(output_model)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )

    return prompt | structured_llm
