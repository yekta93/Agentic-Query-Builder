"""CLI entry point for Agentic Query Builder."""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from src.graph import build_graph
from src.state import State
from src.config_loader import get_config, reset_config, count_candidates

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/output")


def save_result(final_state: Any, suffix_id: int, out_dir: Path) -> None:
    """Persist the final state of a single run."""
    out_dir.mkdir(parents=True, exist_ok=True)

    result_data = {
        "suffix": final_state.get("suffix") if isinstance(final_state, dict) else getattr(final_state, "suffix", None),
        "question": final_state.get("question") if isinstance(final_state, dict) else getattr(final_state, "question", ""),
        "pql_query": final_state.get("pql_query") if isinstance(final_state, dict) else getattr(final_state, "pql_query", ""),
        "has_error": final_state.get("has_error") if isinstance(final_state, dict) else getattr(final_state, "has_error", False),
        "error": final_state.get("error") if isinstance(final_state, dict) else getattr(final_state, "error", None),
        "retry_count": final_state.get("retry_count") if isinstance(final_state, dict) else getattr(final_state, "retry_count", 0),
        "evaluation_result": str(final_state.get("evaluation_result") if isinstance(final_state, dict) else getattr(final_state, "evaluation_result", None)),
    }

    out_path = out_dir / f"result_{suffix_id}.json"
    try:
        import json

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        logger.info("Saved result → %s", out_path)
    except Exception as e:
        logger.error("Failed to save result: %s", e)


async def process_single(graph, suffix: int, out_dir: Path) -> None:
    """Run the full pipeline for a single example."""
    logger.info("Processing example with suffix: %s", suffix)

    initial_state = State(suffix=suffix, pql_query="")
    final_state = await graph.ainvoke(initial_state)

    save_result(final_state, suffix, out_dir)


async def run_for_candidate(args: argparse.Namespace, candidate_index: int) -> None:
    """Execute the pipeline for one configuration candidate."""
    reset_config()
    config = get_config(args.config, candidate_index=candidate_index)

    run_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = OUTPUT_DIR / f"{run_ts}_candidate_{candidate_index}"
    out_path.mkdir(parents=True, exist_ok=True)

    logger.info("[Candidate %d] Model: %s", candidate_index, config.graph_features.model)
    logger.info("[Candidate %d] Output directory: %s", candidate_index, out_path)

    # Build the graph with the selected configuration
    graph = await build_graph()

    # Resolve which examples to run
    if args.suffix.strip().lower() == "all":
        # For the demo we currently support a small fixed set.
        # Later this will read from data/demo.
        suffixes = list(range(1, 6))  # placeholder: 5 demo examples
    else:
        suffixes = [int(s.strip()) for s in args.suffix.split(",") if s.strip()]

    for suffix in suffixes:
        try:
            await process_single(graph, suffix, out_path)
        except Exception as e:
            logger.error("[Candidate %d] Failed on suffix %s: %s", candidate_index, suffix, e)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic Query Builder – SIEM Log Analytics")
    parser.add_argument(
        "--suffix", "-s",
        type=str,
        default="1",
        help="Example ID(s) to process (comma-separated) or 'all' (default: 1)",
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--candidate-index", "-ci",
        type=int,
        default=0,
        help="Which candidate from config.yaml to use (default: 0)",
    )
    parser.add_argument(
        "--all", "-a",
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
