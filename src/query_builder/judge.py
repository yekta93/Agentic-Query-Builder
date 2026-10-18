"""Judge node – final quality evaluation of the generated query."""

import logging
from typing import Any

from src.state import State
from utils.helper import load_reference_query
from utils.schemas import EvaluationResult

logger = logging.getLogger(__name__)


async def judge_node(state: State) -> dict[str, Any]:
    """
    Produce a simple evaluation of the final query.

    Current implementation uses lightweight heuristics + comparison with
    the reference query when available. Can later be replaced by an LLM-as-judge.
    """
    logger.info("Judge node for suffix=%s", state.suffix)

    query = (state.pql_query or "").strip()
    has_syntax_error = bool(state.has_error)

    score = 0.0
    comments = []

    if not query:
        comments.append("Empty query")
        score = 0.0
    elif has_syntax_error:
        comments.append(f"Syntax error: {state.error}")
        score = 0.2
    else:
        score = 0.6  # base score for a syntactically valid query
        comments.append("Query is syntactically valid")

        # Bonus if it contains common useful clauses
        lower = query.lower()
        if "where" in lower:
            score += 0.1
        if "stats" in lower or "timeseries" in lower:
            score += 0.1
        if "sort" in lower or "fields" in lower:
            score += 0.05

        # Compare with reference if available
        ref = load_reference_query(state.suffix)
        if ref:
            # Very rough similarity: check whether key tokens overlap
            ref_tokens = set(ref.lower().split())
            gen_tokens = set(lower.split())
            overlap = len(ref_tokens & gen_tokens) / max(len(ref_tokens), 1)
            if overlap > 0.5:
                score += 0.15
                comments.append(f"Good overlap with reference query ({overlap:.0%})")
            else:
                comments.append(f"Low overlap with reference query ({overlap:.0%})")

    score = min(score, 1.0)

    evaluation = EvaluationResult(
        score=round(score, 3),
        valid_syntax=not has_syntax_error,
        comments="; ".join(comments),
    )

    logger.info("Evaluation score=%.3f – %s", evaluation.score, evaluation.comments)

    return {
        "evaluation_result": evaluation,
    }
