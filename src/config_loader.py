"""Configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List, Optional

import yaml
from pydantic import BaseModel, Field


class PromptConfig(BaseModel):
    few_shots: bool = False
    cim: bool = False  # reserved for future context injection methods


class GraphFeatures(BaseModel):
    model: str = "google/gemma-2-27b-it"
    prompt_config: PromptConfig = Field(default_factory=PromptConfig)
    syntax_checker: bool = True
    reflect: bool = True
    translate: bool = False


class DataPaths(BaseModel):
    questions_dir: str = "data/demo/questions"
    queries_dir: str = "data/demo/queries"
    details_dir: str = "data/demo/details"
    syntax_guide: str = "artifacts/slaql_syntax.md"
    fields_guide: str = "artifacts/fields.md"
    output_dir: str = "data/output"


class AppConfig(BaseModel):
    graph_features: GraphFeatures = Field(default_factory=GraphFeatures)
    data: DataPaths = Field(default_factory=DataPaths)
    temperature: float = 0.0
    max_retries: int = 3
    timeout: int = 60


# ---------------------------------------------------------------------------
# Global config cache
# ---------------------------------------------------------------------------
_config: Optional[AppConfig] = None
_raw_candidates: List[dict[str, Any]] = []


def reset_config() -> None:
    """Clear the cached configuration (useful for tests and multi-candidate runs)."""
    global _config
    _config = None


def count_candidates(config_path: str | Path = "config.yaml") -> int:
    """Return the number of candidates defined in the config file."""
    path = Path(config_path)
    if not path.exists():
        return 1
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return len(raw.get("candidates", [1]))


def get_config(
    config_path: str | Path = "config.yaml",
    candidate_index: int = 0,
) -> AppConfig:
    """
    Load and return the application configuration.

    Supports multiple candidates defined under the `candidates` key.
    """
    global _config, _raw_candidates

    if _config is not None and candidate_index == 0:
        return _config

    path = Path(config_path)
    if not path.exists():
        # Return sensible defaults when no config file is present
        _config = AppConfig()
        return _config

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    _raw_candidates = raw.get("candidates", [])
    defaults = raw.get("defaults", {})
    data_section = raw.get("data", {})

    if not _raw_candidates:
        # Single default candidate
        features = GraphFeatures()
    else:
        idx = max(0, min(candidate_index, len(_raw_candidates) - 1))
        cand = _raw_candidates[idx]

        prompt_list = cand.get("prompt_config", [])
        prompt_cfg = PromptConfig(
            few_shots="few-shots" in prompt_list or "few_shots" in prompt_list,
            cim="cim" in prompt_list,
        )

        features = GraphFeatures(
            model=cand.get("model", "google/gemma-2-27b-it"),
            prompt_config=prompt_cfg,
            syntax_checker=bool(cand.get("syntax_checker", True)),
            reflect=bool(cand.get("reflect", True)),
            translate=bool(cand.get("translate", False)),
        )

    config = AppConfig(
        graph_features=features,
        data=DataPaths(**data_section) if data_section else DataPaths(),
        temperature=float(defaults.get("temperature", 0.0)),
        max_retries=int(defaults.get("max_retries", 3)),
        timeout=int(defaults.get("timeout", 60)),
    )

    # Allow environment variable override for the model
    env_model = os.getenv("DEFAULT_MODEL")
    if env_model:
        config.graph_features.model = env_model

    _config = config
    return config
