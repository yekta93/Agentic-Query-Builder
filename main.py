"""CLI entry point for Agentic Query Builder."""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from src.graph import build_graph
from src.state import State
from src.config_loader import get_config, reset_config, count_candidates
from utils.helper import list_demo_suffixes, load_question

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/output")


def _to_dict(obj: Any) -> Any:
    """Best-effort conversion of state / pydantic objects to plain dict."""
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return obj
    return str(obj)


def g(final_state: Any, key: str, default=None):
    if isinstance(final_state, dict):
        return final_state.get(key, default)
    return getattr(final_state, key, default)


def save_structured_results(final_state: Any, suffix_id: int, out_dir: Path) -> None:
    """
    Persist results in the same layout as the original project:

        out_dir/
          metadata.json          (written once per candidate run)
          syntax_result/result_{id}.json
          evaluation/evaluation_{id}.json
          execution_result/execution_result_{id}.json
          result_{id}.json       (full combined snapshot)
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "syntax_result").mkdir(exist_ok=True)
    (out_dir / "evaluation").mkdir(exist_ok=True)
    (out_dir / "execution_result").mkdir(exist_ok=True)

    # --- syntax_result ---
    syntax_data = {
        "suffix": g(final_state, "suffix"),
        "question": g(final_state, "question"),
        "pql_query": g(final_state, "pql_query"),
        "syntax_check_result": _to_dict(g(final_state, "syntax_check_result")),
        "has_error": g(final_state, "has_error", False),
        "error": g(final_state, "error"),
        "retry_count": g(final_state, "retry_count", 0),
        "reflection_feedback": g(final_state, "reflection_feedback"),
    }
    path = out_dir / "syntax_result" / f"result_{suffix_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(syntax_data, f, indent=2, ensure_ascii=False)
    logger.info("Saved syntax_result → %s", path)

    # --- evaluation ---
    evaluation = _to_dict(g(final_state, "evaluation_result"))
    if evaluation is not None:
        path = out_dir / "evaluation" / f"evaluation_{suffix_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
        logger.info("Saved evaluation → %s", path)

    # --- execution_result ---
    execution = _to_dict(g(final_state, "execution_result"))
    exec_data = {
        "suffix": g(final_state, "suffix"),
        "pql_query": g(final_state, "pql_query"),
        "execution_result": execution,
    }
    path = out_dir / "execution_result" / f"execution_result_{suffix_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(exec_data, f, indent=2, ensure_ascii=False)
    logger.info("Saved execution_result → %s", path)

    # --- combined snapshot ---
    combined = {
        "suffix": g(final_state, "suffix"),
        "question": g(final_state, "question"),
        "pql_query": g(final_state, "pql_query"),
        "has_error": g(final_state, "has_error", False),
        "error": g(final_state, "error"),
        "retry_count": g(final_state, "retry_count", 0),
        "syntax_check_result": _to_dict(g(final_state, "syntax_check_result")),
        "evaluation_result": evaluation,
        "execution_result": execution,
        "reflection_feedback": g(final_state, "reflection_feedback"),
    }
    path = out_dir / f"result_{suffix_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    logger.info("Saved combined result → %s", path)


async def process_single(graph, suffix: int, out_dir: Path) -> None:
    """Run the full pipeline for a single example."""
    question = load_question(suffix)
    logger.info("Processing suffix=%s | question=%s", suffix, question[:80])

    initial_state = State(suffix=suffix, question=question, pql_query="")
    final_state = await graph.ainvoke(initial_state)

    save_structured_results(final_state, suffix, out_dir)


async def run_for_candidate(args: argparse.Namespace, candidate_index: int) -> None:
    """Execute the pipeline for one configuration candidate."""
    reset_config()
    config = get_config(args.config, candidate_index=candidate_index)

    run_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = OUTPUT_DIR / f"{run_ts}_candidate_{candidate_index}"
    out_path.mkdir(parents=True, exist_ok=True)

    # Save metadata once per candidate run
    metadata = {
        "candidate_index": candidate_index,
        "model": config.graph_features.model,
        "prompt_config": {
            "few_shots": config.graph_features.prompt_config.few_shots,
            "cim": config.graph_features.prompt_config.cim,
        },
        "reflect": config.graph_features.reflect,
        "syntax_checker": config.graph_features.syntax_checker,
        "translate": config.graph_features.translate,
    }
    with open(out_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info("[Candidate %d] Saved metadata.json", candidate_index)

    logger.info("[Candidate %d] Model: %s", candidate_index, config.graph_features.model)
    logger.info(
        "[Candidate %d] few_shots=%s, syntax_checker=%s, reflect=%s",
        candidate_index,
        config.graph_features.prompt_config.few_shots,
        config.graph_features.syntax_checker,
        config.graph_features.reflect,
    )
    logger.info("[Candidate %d] Output → %s", candidate_index, out_path)

    graph = await build_graph()

    if args.suffix.strip().lower() == "all":
        suffixes = list_demo_suffixes()
        if not suffixes:
            suffixes = list(range(1, 11))
    else:
        suffixes = [int(s.strip()) for s in args.suffix.split(",") if s.strip()]

    for suffix in suffixes:
        try:
            await process_single(graph, suffix, out_path)
        except Exception as e:
            logger.error(
                "[Candidate %d] Failed on suffix %s: %s", candidate_index, suffix, e
            )


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agentic Query Builder – SIEM Log Analytics Query Language (SLAQL)"
    )
    parser.add_argument(
        "--suffix",
        "-s",
        type=str,
        default="1",
        help="Example ID(s) to process (comma-separated) or 'all' (default: 1)",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--candidate-index",
        "-ci",
        type=int,
        default=0,
        help="Which candidate from config.yaml to use (default: 0)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Run every candidate defined in the config file",
    )

    args = parser.parse_args()

    if args.all:
        n = count_candidates(args.config)
        logger.info("Running all %d candidates...", n)
        for i in range(n):
            await run_for_candidate(args, i)
    else:
        await run_for_candidate(args, args.candidate_index)


if __name__ == "__main__":
    asyncio.run(main())
