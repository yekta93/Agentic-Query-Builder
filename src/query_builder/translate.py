"""Translate node – optional translation of the input question."""

import logging
from typing import Any

from src.state import State
from utils.helper import load_question

logger = logging.getLogger(__name__)


async def translate_node(state: State) -> dict[str, Any]:
    """
    Optionally translate the question (e.g. Persian → English).

    Currently a no-op that simply ensures a question is present.
    Can later be extended with an LLM translation step.
    """
    logger.info("Translate node for suffix=%s", state.suffix)

    question = state.question or state.question_en
    if not question:
        question = load_question(state.suffix)

    return {
        "question": question,
        "translated_question": question,
    }
