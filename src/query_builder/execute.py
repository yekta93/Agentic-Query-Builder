"""Execute node – runs (or mocks) the generated SLAQL query."""

import logging
from typing import Any

from src.state import State

logger = logging.getLogger(__name__)


async def execute_node(state: State) -> dict[str, Any]:
    """
    Execute the query against a SIEM backend.

    In demo mode this returns a mocked result so the pipeline can be demonstrated
    without a real SIEM connection.
    """
    logger.info("Execute node for suffix=%s", state.suffix)

    mocked_result = {
        "status": "success",
        "rows_returned": 42,
        "sample": [
            {"user": "alice", "source_ip": "10.0.1.15", "count": 12},
            {"user": "bob", "source_ip": "192.168.3.22", "count": 8},
        ],
        "note": "This is a mocked execution result for demonstration purposes.",
    }

    return {
        "execution_result": mocked_result,
    }
