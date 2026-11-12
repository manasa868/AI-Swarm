"""Pydantic schemas for Transparent Legal AI."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LegalQueryCreate(BaseModel):
    question: str = Field(..., example="Is an employee non-compete clause enforceable if signed without additional consideration?")
    jurisdiction: Optional[str] = Field(default="United States / General Common Law")
    context_notes: Optional[str] = Field(default=None)


class LegalSourceSchema(BaseModel):
    id: str
    title: str
    source_type: str  # statute, precedent, regulation
    citation: str
    url_or_ref: Optional[str]
    excerpt: str
    relevance_score: float
    is_verified: bool

    class Config:
        from_attributes = True


class LegalQueryResponse(BaseModel):
    id: str
    question: str
    jurisdiction: str
    facts_identified: List[str]
    assumptions: List[str]
    missing_info: List[str]
    relevant_provisions: List[str]
    analysis: Optional[str]
    possible_issues: List[str]
    risks_uncertainties: List[Dict[str, Any]]
    explanation: Optional[str]
    limitations: List[str]
    disclaimer: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    sources: List[LegalSourceSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True
