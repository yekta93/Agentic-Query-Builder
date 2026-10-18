"""Reflect node – analyzes errors and produces feedback for the next generation attempt."""

import logging
from typing import Any

from src.state import State
from utils.helper import load_syntax_guide
from utils.llm_clients import get_llm
from src.config_loader import get_config

logger = logging.getLogger(__name__)

REFLECT_PROMPT = """You are a senior SLAQL (SIEM Log Analytics Query Language) reviewer.

The previous query generation attempt failed with the following error:
{error}

Original question:
{question}

Previous (invalid) query:
```
{query}
```

SLAQL Syntax Reference:
{syntax_guide}

Your task:
1. Briefly explain why the query is invalid.
2. Give concrete, actionable advice so the next generation attempt can produce a correct query.
3. Do NOT output a full corrected query – only the diagnosis and guidance.

Keep the response concise (max 150 words)."""


async def reflect_node(state: State) -> dict[str, Any]:
    """
    Reflect on the previous syntax error and produce feedback.
    """
    logger.info(
        "Reflect node (retry %d) for suffix=%s", state.retry_count, state.suffix
    )

    config = get_config()
    syntax_guide = load_syntax_guide()

    prompt = REFLECT_PROMPT.format(
        error=state.error or "Unknown error",
        question=state.question or "",
        query=state.pql_query or "",
        syntax_guide=syntax_guide[:3000],  # keep prompt size reasonable
    )

    try:
        llm = get_llm(
            model=config.graph_features.model,
            temperature=0.2,
            timeout=config.timeout,
        )
        response = await llm.ainvoke(prompt)
        feedback = response.content if hasattr(response, "content") else str(response)
        logger.info("Reflection feedback generated")
    except Exception as e:
        logger.warning("LLM reflection failed, using fallback feedback: %s", e)
        feedback = (
            f"Previous error: {state.error}. "
            "Please ensure the query starts with a valid 'from' time range "
            "and uses only supported SLAQL fields and pipeline commands "
            "(where, stats, sort, fields, timeseries)."
        )

    return {
        "reflection_feedback": feedback,
        # Clear the error flag so the next syntax check starts clean
        "has_error": False,
        "error": None,
    }
