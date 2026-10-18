"""Pydantic schemas used across the project."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class OutputQuery(BaseModel):
    """Structured output expected from the LLM for query generation."""

    query: str = Field(..., description="The generated SLAQL query")


class EvaluationResult(BaseModel):
    """Result produced by the Judge node."""

    score: float = Field(..., ge=0.0, le=1.0, description="Quality score between 0 and 1")
    valid_syntax: bool = Field(..., description="Whether the query passed syntax validation")
    comments: str = Field(default="", description="Human-readable evaluation comments")
    details: Optional[dict[str, Any]] = Field(default=None)


class QueryExample(BaseModel):
    """A single few-shot example."""

    index: int
    question: str
    query: str
    detail: str = ""
