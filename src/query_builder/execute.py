"""Execute node – runs (or mocks) the generated SLAQL query."""

import logging
from typing import Any

from src.state import State

logger = logging.getLogger(__name__)


async def execute_node(state: State) -> dict[str, Any]:
    """
    Execute the query against a SIEM backend.

    In the current public version this returns a realistic mocked result
    so the full pipeline can be demonstrated without a real SIEM connection.
    """
    logger.info("Execute node for suffix=%s", state.suffix)

    if state.has_error or not state.pql_query:
        return {
            "execution_result": {
                "status": "skipped",
                "reason": "Query has errors or is empty",
                "rows_returned": 0,
            }
        }

    # Mocked result that looks realistic for portfolio demos
    mocked_result = {
        "status": "success",
        "query": state.pql_query,
        "rows_returned": 17,
        "execution_time_ms": 142,
        "sample_rows": [
            {"user": "alice", "source_ip": "10.0.1.15", "count": 7},
            {"user": "bob", "source_ip": "192.168.3.22", "count": 5},
            {"user": "charlie", "source_ip": "10.0.4.8", "count": 3},
            {"user": "dave", "source_ip": "172.16.0.9", "count": 2},
        ],
        "note": "Mocked execution result for demonstration purposes. "
                "In production this node would call the real SIEM API.",
    }

    logger.info("Mock execution completed (rows=%d)", mocked_result["rows_returned"])

    return {
        "execution_result": mocked_result,
    }
