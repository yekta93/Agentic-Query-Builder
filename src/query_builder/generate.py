"""Generate node – converts natural language into an SLAQL query."""

import logging
from typing import Any

from src.config_loader import get_config
from src.state import State
from utils.helper import (
    load_question,
    load_few_shots,
    load_syntax_guide,
    load_fields_guide,
    load_reference_query,
)
from utils.llm_clients import create_structured_chain, has_api_key
from utils.schemas import OutputQuery

logger = logging.getLogger(__name__)


def _build_system_prompt(include_few_shots: bool) -> str:
    """Construct the system prompt for SLAQL generation."""
    parts = [
        "You are an expert SIEM Log Analytics Query Language (SLAQL) engineer.\n",
        "Your only task is to convert a natural language question into a single, valid SLAQL query.\n\n",
        "Rules:\n",
        "- Output ONLY a valid JSON object of the form {\"query\": \"YOUR_SLAQL_QUERY\"}\n",
        "- Do not add explanations or markdown outside the JSON.\n",
        "- Use only the fields and syntax defined in the reference below.\n",
        "- Prefer clear, readable pipeline-style queries.\n\n",
    ]

    if include_few_shots:
        parts.append(
            "You will receive few-shot examples with explanations. "
            "Learn the style and patterns from them.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "FEW-SHOT EXAMPLES\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "{few_shots}\n\n"
        )

    parts.append(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "SLAQL SYNTAX REFERENCE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "{syntax_guide}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "AVAILABLE FIELDS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "{fields_guide}\n\n"
        "If you detect any mistake, correct it using the syntax guide before producing the final answer."
    )

    return "".join(parts)


def _build_user_prompt() -> str:
    return (
        "Write an SLAQL query for the following question:\n\n"
        "{question}\n\n"
        "{reflection_section}"
    )


class QueryGenerator:
    """Generates SLAQL queries from natural language using few-shot learning."""

    def __init__(self):
        self.config = get_config()
        self._setup_chain()

    def _setup_chain(self):
        features = self.config.graph_features
        include_few_shots = features.prompt_config.few_shots

        system_prompt = _build_system_prompt(include_few_shots=include_few_shots)
        user_prompt = _build_user_prompt()

        self.chain = create_structured_chain(
            model=features.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=OutputQuery,
            temperature=self.config.temperature,
            timeout=self.config.timeout,
        )
        self.include_few_shots = include_few_shots
        logger.info(
            "QueryGenerator ready (model=%s, few_shots=%s)",
            features.model,
            include_few_shots,
        )

    def generate(
        self,
        question: str,
        exclude_suffix: int | None = None,
        reflection_feedback: str | None = None,
    ) -> str:
        """Generate an SLAQL query for the given question."""
        syntax_guide = load_syntax_guide()
        fields_guide = load_fields_guide()

        if reflection_feedback:
            reflection_section = (
                "IMPORTANT – Previous attempt failed. Please follow this feedback:\n"
                f"{reflection_feedback}\n"
            )
        else:
            reflection_section = ""

        inputs: dict[str, Any] = {
            "question": question,
            "syntax_guide": syntax_guide,
            "fields_guide": fields_guide,
            "reflection_section": reflection_section,
        }

        if self.include_few_shots:
            inputs["few_shots"] = load_few_shots(exclude_suffix=exclude_suffix)
        else:
            inputs["few_shots"] = "Few-shot examples are disabled for this run."

        logger.info("Calling LLM to generate SLAQL query...")
        result: OutputQuery = self.chain.invoke(inputs)
        logger.info("Generated query:\n%s", result.query)
        return result.query.strip()


async def generate_node(state: State) -> dict[str, Any]:
    """
    LangGraph node that generates an SLAQL query from the input question.
    On retries it also incorporates reflection feedback.

    Demo / offline mode:
    --------------------
    If OPENROUTER_API_KEY is not set, the node falls back to the reference
    query stored in data/demo/queries/. This allows the full pipeline to be
    exercised without an API key. Remove or comment out the fallback block
    when you have a real key and want live LLM generation.
    """
    logger.info(
        "Generate node started (suffix=%s, retry=%s)",
        state.suffix,
        state.retry_count,
    )

    question = state.question or state.question_en
    if not question:
        question = load_question(state.suffix)

    # ------------------------------------------------------------------
    # DEMO FALLBACK (no API key)
    # Comment out this block once you set OPENROUTER_API_KEY and want
    # real LLM generation.
    # ------------------------------------------------------------------
    if not has_api_key():
        logger.warning(
            "OPENROUTER_API_KEY not found → using reference query as demo fallback "
            "(suffix=%s). Set the key in .env to enable live LLM generation.",
            state.suffix,
        )
        ref = load_reference_query(state.suffix)
        if ref:
            return {
                "pql_query": ref,
                "question": question,
                "error": None,
                "has_error": False,
            }
        # If no reference exists, still return a minimal valid query so the
        # rest of the pipeline can run.
        return {
            "pql_query": 'from last 24h\n| where severity == "high"\n| stats count() by event_type',
            "question": question,
            "error": None,
            "has_error": False,
        }
    # ------------------------------------------------------------------

    try:
        generator = QueryGenerator()
        pql_query = generator.generate(
            question=question,
            exclude_suffix=state.suffix,
            reflection_feedback=state.reflection_feedback,
        )
        return {
            "pql_query": pql_query,
            "question": question,
            "error": None,
            "has_error": False,
        }
    except Exception as e:
        error_msg = f"Query generation failed: {e}"
        logger.error(error_msg)
        return {
            "pql_query": state.pql_query or "",
            "question": question,
            "error": error_msg,
            "has_error": True,
        }
