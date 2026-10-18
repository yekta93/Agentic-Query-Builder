"""Shared state definition for the LangGraph workflow."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class State(BaseModel):
    """State object that flows through the agentic pipeline."""

    # Input
    suffix: int = Field(..., description="Example ID from the demo dataset")
    question: str = Field(default="", description="Natural language question")
    question_en: str = Field(default="", description="English version of the question")

    # Generated artifacts
    pql_query: str = Field(default="", description="Generated SLAQL query")
    translated_question: Optional[str] = Field(default=None, description="Translated question if translate stage is enabled")

    # Validation & reflection
    syntax_check_result: Optional[dict[str, Any]] = Field(default=None)
    has_error: bool = Field(default=False)
    error: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)
    reflection_feedback: Optional[str] = Field(default=None)

    # Evaluation
    evaluation_result: Optional[Any] = Field(default=None)
    execution_result: Optional[dict[str, Any]] = Field(default=None)

    # Metadata
    attempts: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True
