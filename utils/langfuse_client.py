"""Langfuse tracing helpers for the LangGraph pipeline.

Usage
-----
1. Set LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY (and optionally LANGFUSE_HOST) in .env
2. Install:  pip install "agentic-query-builder[observability]"  or  pip install langfuse
3. Run the CLI as usual – each graph invocation is traced automatically.

If keys are missing, tracing is silently disabled so demo mode still works offline.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def is_langfuse_enabled() -> bool:
    """Return True when Langfuse credentials are present."""
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def get_langfuse_handler(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    tags: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
):
    """
    Create a Langfuse CallbackHandler for LangChain / LangGraph.

    Returns None when credentials are missing or the package is not installed,
    so the rest of the pipeline can run without observability.

    Compatible with both langfuse v2 (`langfuse.callback`) and v3 (`langfuse.langchain`).
    """
    if not is_langfuse_enabled():
        logger.debug("Langfuse keys not set → tracing disabled")
        return None

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    # Ensure env vars are visible to the SDK (some versions only read from env)
    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", public_key or "")
    os.environ.setdefault("LANGFUSE_SECRET_KEY", secret_key or "")
    os.environ.setdefault("LANGFUSE_HOST", host)

    default_tags = ["slaql", "agentic-query-builder"]
    if tags:
        default_tags = list(dict.fromkeys(default_tags + tags))

    try:
        # Prefer v2-style import (widely used)
        try:
            from langfuse.callback import CallbackHandler  # type: ignore

            handler = CallbackHandler(
                public_key=public_key,
                secret_key=secret_key,
                host=host,
                session_id=session_id,
                user_id=user_id,
                tags=default_tags,
                metadata=metadata or {},
            )
        except ImportError:
            # Fallback: langfuse v3
            from langfuse.langchain import CallbackHandler  # type: ignore

            handler = CallbackHandler()

        # Optional auth check (supported on many versions)
        if hasattr(handler, "auth_check"):
            try:
                if handler.auth_check():
                    logger.info("Langfuse client authenticated and ready")
                else:
                    logger.warning(
                        "Langfuse authentication failed – check PUBLIC/SECRET keys and HOST"
                    )
            except Exception as e:
                logger.warning("Langfuse auth_check failed: %s", e)
        else:
            logger.info("Langfuse CallbackHandler created (session_id=%s)", session_id)

        return handler

    except ImportError:
        logger.warning(
            "langfuse package not installed. "
            "Install with: pip install langfuse  or  pip install '.[observability]'"
        )
        return None
    except Exception as e:
        logger.warning("Could not initialise Langfuse handler: %s", e)
        return None


def build_invoke_config(
    suffix: int,
    candidate_index: int = 0,
    extra_tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Build the `config` dict passed to graph.ainvoke / graph.invoke.

    When Langfuse is disabled, returns an empty dict so behaviour is unchanged.
    """
    session_id = f"candidate_{candidate_index}_suffix_{suffix}"
    tags = ["slaql", f"candidate_{candidate_index}"]
    if extra_tags:
        tags.extend(extra_tags)

    handler = get_langfuse_handler(
        session_id=session_id,
        tags=tags,
        metadata={"suffix": suffix, "candidate_index": candidate_index},
    )

    if handler is None:
        return {}

    return {
        "callbacks": [handler],
        "run_name": f"slaql_query_{suffix}",
        "metadata": {
            # Used by Langfuse v3 to attach session to the trace
            "langfuse_session_id": session_id,
            "suffix": suffix,
            "candidate_index": candidate_index,
        },
    }


def flush_langfuse(handler: Any = None) -> None:
    """Best-effort flush so traces are sent before process exit."""
    if handler is not None and hasattr(handler, "flush"):
        try:
            handler.flush()
        except Exception as e:
            logger.debug("Langfuse handler.flush() failed: %s", e)

    try:
        from langfuse import get_client  # type: ignore

        get_client().flush()
    except Exception:
        pass
