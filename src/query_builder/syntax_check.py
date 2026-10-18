"""Syntax check node – validates the generated SLAQL query."""

import logging
import re
from typing import Any

from src.state import State

logger = logging.getLogger(__name__)

# Very lightweight rule-based checks. Can be replaced later with a real parser.
REQUIRED_CLAUSE = re.compile(r"\bfrom\s+", re.IGNORECASE)
SUPPORTED_PIPE_COMMANDS = {
    "where", "stats", "sort", "fields", "timeseries", "limit", "head", "tail"
}


def _basic_validate(query: str) -> tuple[bool, str | None]:
    """Return (is_valid, error_message)."""
    if not query or not query.strip():
        return False, "Empty query"

    if not REQUIRED_CLAUSE.search(query):
        return False, "Missing required 'from' time-range clause"

    # Check that every pipe segment starts with a known command
    lines = [ln.strip() for ln in query.splitlines() if ln.strip()]
    for line in lines:
        if line.startswith("|"):
            cmd = line.lstrip("| ").split()[0].lower() if line.lstrip("| ") else ""
            if cmd and cmd not in SUPPORTED_PIPE_COMMANDS:
                return False, f"Unsupported pipeline command: '{cmd}'"

    return True, None


async def syntax_check_node(state: State) -> dict[str, Any]:
    """
    Perform basic syntax validation on the generated SLAQL query.
    """
    logger.info("Syntax check for suffix=%s", state.suffix)

    query = state.pql_query or ""
    is_valid, error_msg = _basic_validate(query)

    retry_count = state.retry_count
    if not is_valid:
        retry_count += 1

    result = {
        "valid": is_valid,
        "message": error_msg or "OK",
    }

    logger.info("Syntax check result: valid=%s, message=%s", is_valid, result["message"])

    return {
        "has_error": not is_valid,
        "error": error_msg,
        "syntax_check_result": result,
        "retry_count": retry_count,
    }
