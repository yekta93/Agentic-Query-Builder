"""LangGraph workflow definition for the Agentic Query Builder."""

import logging
from pathlib import Path

from langgraph.graph import StateGraph, END

from src.state import State
from src.config_loader import get_config

logger = logging.getLogger(__name__)


def route_after_syntax_check(state: State) -> str:
    """
    Determine the next node after syntax_check.

    - If there is an error, reflection is enabled, and retry limit is not reached → reflect
    - Otherwise → judge
    """
    cfg = get_config()

    if (
        cfg.graph_features.reflect
        and state.has_error
        and state.retry_count < 3
    ):
        logger.info("Routing to 'reflect' node (retry count: %d)", state.retry_count)
        return "reflect"

    logger.info("Routing to 'judge' node")
    return "judge"


async def build_graph():
    """
    Build and compile the LangGraph workflow.

    Pipeline (stages are config-gated):

        [translate?] → generate → [syntax_check? → [reflect?]↩] → judge → execute → END
    """
    # Import agents here to avoid circular imports at module level
    from src.query_builder.generate import generate_node
    from src.query_builder.syntax_check import syntax_check_node
    from src.query_builder.reflect import reflect_node
    from src.query_builder.translate import translate_node
    from src.query_builder.judge import judge_node
    from src.query_builder.execute import execute_node

    cfg = get_config()
    features = cfg.graph_features
    workflow = StateGraph(State)

    # ------------------------------------------------------------------ nodes
    if features.translate:
        workflow.add_node("translate", translate_node)

    workflow.add_node("generate", generate_node)

    if features.syntax_checker:
        workflow.add_node("syntax_check", syntax_check_node)
        if features.reflect:
            workflow.add_node("reflect", reflect_node)

    workflow.add_node("judge", judge_node)
    workflow.add_node("execute", execute_node)

    # ------------------------------------------------------------------ entry
    if features.translate:
        workflow.set_entry_point("translate")
        workflow.add_edge("translate", "generate")
    else:
        workflow.set_entry_point("generate")

    # ------------------------------------------------------------------ edges
    if features.syntax_checker:
        workflow.add_edge("generate", "syntax_check")

        if features.reflect:
            workflow.add_conditional_edges(
                "syntax_check",
                route_after_syntax_check,
                {"reflect": "reflect", "judge": "judge"},
            )
            workflow.add_edge("reflect", "syntax_check")
        else:
            workflow.add_edge("syntax_check", "judge")
    else:
        workflow.add_edge("generate", "judge")

    workflow.add_edge("judge", "execute")
    workflow.add_edge("execute", END)

    # ---------------------------------------------------------------- compile
    graph = workflow.compile()
    logger.info("Agentic Query Builder graph compiled successfully.")

    # Optional: save a visual representation
    try:
        graph_dir = Path(__file__).parent
        png_bytes = graph.get_graph().draw_mermaid_png()
        (graph_dir / "graph.png").write_bytes(png_bytes)
        logger.info("Saved graph.png to %s", graph_dir)
    except Exception as e:
        logger.warning("Could not generate graph.png: %s", e)

    return graph
