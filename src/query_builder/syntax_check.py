"""Syntax check node – validates the generated SLAQL query."""

import logging
from typing import Any

from src.state import State

logger = logging.getLogger(__name__)


async def syntax_check_node(state: State) -> dict[str, Any]:
    """
    Perform basic syntax validation on the generated query.

    Placeholder implementation. The full version will parse the query
    against the SLAQL grammar and return structured error information.
    """
    logger.info("Syntax check for suffix=%s", state.suffix)

    query = state.pql_query or ""
    has_error = False
    error_msg = None

    # Very lightweight heuristic checks for the demo
    if not query.strip():
        has_error = True
        error_msg = "Empty query"
    elif "from " not in query.lower():
        has_error = True
        error_msg = "Missing 'from' time range clause"

    return {
        "has_error": has_error,
        "error": error_msg,
        "syntax_check_result": {
            "valid": not has_error,
            "message": error_msg or "OK",
        },
        "retry_count": state.retry_count + (1 if has_error else 0),
    }
