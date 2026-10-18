"""Judge node – final quality evaluation of the generated query."""

import logging
from typing import Any

from src.state import State

logger = logging.getLogger(__name__)


async def judge_node(state: State) -> dict[str, Any]:
    """
    Produce a simple evaluation of the final query.

    Placeholder implementation.
    """
    logger.info("Judge node for suffix=%s", state.suffix)

    score = 0.0
    if state.pql_query and not state.has_error:
        score = 0.85  # placeholder score

    evaluation = {
        "score": score,
        "valid_syntax": not state.has_error,
        "comments": "Placeholder evaluation – replace with LLM-as-judge or rule-based scoring.",
    }

    return {
        "evaluation_result": evaluation,
    }
