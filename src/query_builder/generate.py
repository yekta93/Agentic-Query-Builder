"""Generate node – converts natural language into an SLAQL query."""

import logging
from typing import Any

from src.state import State

logger = logging.getLogger(__name__)


async def generate_node(state: State) -> dict[str, Any]:
    """
    Generate an SLAQL query from the input question.

    This is a placeholder implementation.
    The full version will:
    - Load few-shot examples (if enabled)
    - Load SLAQL syntax and field references
    - Call the configured LLM
    - Return the generated query
    """
    logger.info("Generate node started for suffix=%s", state.suffix)

    # TODO: Implement full generation logic with LLM + few-shot
    # For now return a simple placeholder so the graph can be exercised.
    placeholder_query = (
        'from last 24h\n'
        '| where event_type == "login" and severity == "high"\n'
        '| stats count() by user, source_ip\n'
        '| sort count desc'
    )

    return {
        "pql_query": placeholder_query,
        "question": state.question or f"Demo question for example {state.suffix}",
    }
