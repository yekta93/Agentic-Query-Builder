"""Helper functions for loading demo data and building prompts."""

from pathlib import Path
from typing import List, Optional

DATA_DIR = Path("data/demo")


def load_question(suffix: int) -> str:
    """Load a natural language question by suffix ID."""
    path = DATA_DIR / "questions" / f"q{suffix:03d}.txt"
    if not path.exists():
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
    path = Path("artifacts/slaql_syntax.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def load_fields_guide() -> str:
    """Load the fields reference."""
    path = Path("artifacts/fields.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""
