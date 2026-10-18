"""Helper functions for loading demo data and building prompts."""

import logging
from pathlib import Path
from typing import List, Optional

from utils.schemas import QueryExample

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "demo"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"


def load_question(suffix: int) -> str:
    """Load a natural language question by suffix ID."""
    path = DATA_DIR / "questions" / f"q{suffix:03d}.txt"
    if not path.exists():
        logger.warning("Question file not found: %s", path)
        return f"Demo question for example {suffix}"
    return path.read_text(encoding="utf-8").strip()


def load_reference_query(suffix: int) -> Optional[str]:
    """Load the reference SLAQL query for a given suffix."""
    path = DATA_DIR / "queries" / f"q{suffix:03d}.slaql"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def load_detail(suffix: int) -> Optional[str]:
    """Load the step-by-step explanation for a given suffix."""
    path = DATA_DIR / "details" / f"q{suffix:03d}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def list_demo_suffixes() -> List[int]:
    """Return the list of available demo example IDs."""
    questions_dir = DATA_DIR / "questions"
    if not questions_dir.exists():
        return []
    suffixes = []
    for p in questions_dir.glob("q*.txt"):
        try:
            num = int(p.stem[1:])  # q001 → 1
            suffixes.append(num)
        except ValueError:
            continue
    return sorted(suffixes)


def load_syntax_guide() -> str:
    """Load the SLAQL syntax reference."""
    path = ARTIFACTS_DIR / "slaql_syntax.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    logger.warning("Syntax guide not found: %s", path)
    return "SLAQL syntax reference not available."


def load_fields_guide() -> str:
    """Load the fields reference."""
    path = ARTIFACTS_DIR / "fields.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    logger.warning("Fields guide not found: %s", path)
    return "SLAQL fields reference not available."


def load_few_shots(exclude_suffix: Optional[int] = None) -> str:
    """
    Build a formatted few-shot string from the demo dataset.

    Args:
        exclude_suffix: If provided, this example is excluded (leave-one-out).
    """
    questions_dir = DATA_DIR / "questions"
    queries_dir = DATA_DIR / "queries"
    details_dir = DATA_DIR / "details"

    if not questions_dir.exists():
        logger.warning("Demo questions directory not found")
        return "No few-shot examples available."

    question_files = sorted(questions_dir.glob("q*.txt"))
    examples: List[QueryExample] = []

    for q_path in question_files:
        try:
            idx = int(q_path.stem[1:])
        except ValueError:
            continue

        if exclude_suffix is not None and idx == exclude_suffix:
            continue

        query_path = queries_dir / f"q{idx:03d}.slaql"
        detail_path = details_dir / f"q{idx:03d}.md"

        question = q_path.read_text(encoding="utf-8").strip()
        query = query_path.read_text(encoding="utf-8").strip() if query_path.exists() else ""
        detail = detail_path.read_text(encoding="utf-8").strip() if detail_path.exists() else ""

        examples.append(
            QueryExample(index=idx, question=question, query=query, detail=detail)
        )

    if not examples:
        return "No few-shot examples available."

    logger.info("Loaded %d few-shot examples", len(examples))

    formatted_parts = []
    for i, ex in enumerate(examples, start=1):
        part = (
            f"Example {i} (ID {ex.index})\n"
            f"{'-' * 70}\n"
            f"Question:\n{ex.question}\n\n"
            f"SLAQL Query:\n```\n{ex.query}\n```\n"
        )
        if ex.detail:
            part += f"\nExplanation:\n{ex.detail}\n"
        part += f"{'=' * 70}\n"
        formatted_parts.append(part)

    return "\n".join(formatted_parts)
