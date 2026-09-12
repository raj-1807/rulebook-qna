"""Pydantic schemas for the Rulebook QnA API."""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class QuestionState(str, Enum):
    """The three possible states for a question."""
    ANSWERABLE = "ANSWERABLE"
    NOT_FOUND = "NOT_FOUND"
    CONTRADICTORY = "CONTRADICTORY"


class AskRequest(BaseModel):
    """Request body for the /api/ask endpoint."""
    question: str = Field(..., min_length=1, max_length=2000, description="The question to ask")


class EvidenceItem(BaseModel):
    """A single piece of evidence from the corpus."""
    evidence_id: str = Field(..., description="Stable evidence identifier")
    chunk_id: str = Field(..., description="Chunk identifier with provenance")
    document: str = Field(..., description="Source document filename")
    page: Optional[int] = Field(None, description="Page number (for PDFs)")
    section: str = Field(..., description="Section title")
    text: str = Field(..., description="Exact passage text")
    score: float = Field(..., description="Retrieval score")


class ConflictDetail(BaseModel):
    """Details about a conflict between two evidence passages."""
    rule_a: EvidenceItem
    rule_b: EvidenceItem
    explanation: str = Field(..., description="Why these rules conflict")


class AskResponse(BaseModel):
    """Response body for the /api/ask endpoint."""
    state: QuestionState
    confidence: float = Field(..., ge=0.0, le=1.0)
    answer: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    conflicts: list[ConflictDetail] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Response for the health endpoint."""
    status: str = "ok"
    service: str = "rulebook-qna"
    corpus_loaded: bool = False
    chunks_count: int = 0
