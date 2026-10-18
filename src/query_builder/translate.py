"""Translate node – optional translation of the input question."""

import logging
from typing import Any

from src.state import State

logger = logging.getLogger(__name__)


async def translate_node(state: State) -> dict[str, Any]:
    """
    Optionally translate the question (e.g. Persian → English).

    Placeholder: currently a no-op.
    """
    logger.info("Translate node for suffix=%s (no-op in current version)", state.suffix)

    return {
        "translated_question": state.question or state.question_en,
    }
