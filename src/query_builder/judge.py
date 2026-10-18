"""Judge node – final quality evaluation of the generated query."""

import logging
from typing import Any

from src.config_loader import get_config
from src.state import State
from utils.helper import load_reference_query, load_syntax_guide
from utils.llm_clients import get_llm, has_api_key
from utils.schemas import EvaluationResult

logger = logging.getLogger(__name__)

JUDGE_PROMPT = """You are an expert evaluator of SIEM Log Analytics Query Language (SLAQL) queries.

Evaluate the generated query against the original question and the optional reference query.

Original question:
{question}

Generated query:
```
{generated_query}
```

Reference query (if available):
```
{reference_query}
```

SLAQL syntax reminder (short):
- Must start with a `from <time_range>` clause
- Pipeline commands: where, stats, sort, fields, timeseries, limit
- Use only supported fields

Return a JSON object with exactly these keys:
{{
  "score": <float between 0.0 and 1.0>,
  "valid_syntax": <true/false>,
  "comments": "<short justification, max 2 sentences>"
}}

Scoring guidelines:
- 0.0–0.3 : invalid or completely wrong
- 0.4–0.6 : partially correct, missing important filters or aggregations
- 0.7–0.85: mostly correct, minor issues
- 0.9–1.0 : excellent match to the question and good style
"""


def _heuristic_judge(state: State) -> EvaluationResult:
    """Rule-based evaluation used when no API key is present or LLM fails."""
    query = (state.pql_query or "").strip()
    has_syntax_error = bool(state.has_error)

    score = 0.0
    comments: list[str] = []

    if not query:
        comments.append("Empty query")
        score = 0.0
    elif has_syntax_error:
        comments.append(f"Syntax error: {state.error}")
        score = 0.2
    else:
        score = 0.55
        comments.append("Syntactically valid")

        lower = query.lower()
        if "where" in lower:
            score += 0.1
        if "stats" in lower or "timeseries" in lower:
            score += 0.1
        if "sort" in lower or "fields" in lower or "limit" in lower:
            score += 0.05

        ref = load_reference_query(state.suffix)
        if ref:
            ref_tokens = set(ref.lower().split())
            gen_tokens = set(lower.split())
            overlap = len(ref_tokens & gen_tokens) / max(len(ref_tokens), 1)
            if overlap >= 0.7:
                score += 0.2
                comments.append(f"High overlap with reference ({overlap:.0%})")
            elif overlap >= 0.4:
                score += 0.1
                comments.append(f"Moderate overlap with reference ({overlap:.0%})")
            else:
                comments.append(f"Low overlap with reference ({overlap:.0%})")

    score = min(round(score, 3), 1.0)
    return EvaluationResult(
        score=score,
        valid_syntax=not has_syntax_error,
        comments="; ".join(comments),
    )


async def _llm_judge(state: State) -> EvaluationResult:
    """LLM-as-judge evaluation."""
    config = get_config()
    ref = load_reference_query(state.suffix) or "(none)"

    prompt = JUDGE_PROMPT.format(
        question=state.question or "",
        generated_query=state.pql_query or "",
        reference_query=ref,
    )

    llm = get_llm(
        model=config.graph_features.model,
        temperature=0.0,
        timeout=config.timeout,
    )

    # Use structured output when possible
    structured = llm.with_structured_output(EvaluationResult)
    result = await structured.ainvoke(prompt)
    return result


async def judge_node(state: State) -> dict[str, Any]:
    """
    Produce a quality evaluation of the final query.

    - If OPENROUTER_API_KEY is set → LLM-as-judge
    - Otherwise → strong heuristic fallback (useful for offline demos)
    """
    logger.info("Judge node for suffix=%s", state.suffix)

    if has_api_key():
        try:
            evaluation = await _llm_judge(state)
            logger.info(
                "LLM-as-judge score=%.3f – %s",
                evaluation.score,
                evaluation.comments,
            )
            return {"evaluation_result": evaluation}
        except Exception as e:
            logger.warning("LLM judge failed (%s) → falling back to heuristic", e)

    evaluation = _heuristic_judge(state)
    logger.info(
        "Heuristic judge score=%.3f – %s",
        evaluation.score,
        evaluation.comments,
    )
    return {"evaluation_result": evaluation}
