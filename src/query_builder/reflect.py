"""Reflect node – analyzes errors and suggests improvements."""

import logging
from typing import Any

from src.state import State

logger = logging.getLogger(__name__)


async def reflect_node(state: State) -> dict[str, Any]:
    """
    Reflect on the previous error and produce feedback for the next generation attempt.

    Placeholder implementation.
    """
    logger.info("Reflect node (retry %d) for suffix=%s", state.retry_count, state.suffix)

    feedback = (
        f"Previous error: {state.error}. "
        "Please ensure the query starts with a valid 'from' time range "
        "and uses only supported SLAQL fields and operators."
    )

    return {
        "reflection_feedback": feedback,
        "has_error": False,  # clear the flag so the next syntax check starts fresh
    }
