"""Tests for Transparent Legal AI workflow and anti-hallucination policies."""
import pytest
from app.legal.legal_knowledge_base import search_legal_knowledge_base, LEGAL_DISCLAIMER_TEXT
from app.legal.legal_researcher import LegalResearchAgent
from app.legal.facts_analyzer import FactsAnalysisAgent
from app.legal.risk_analyzer import LegalRiskAnalysisAgent
from app.legal.legal_reviewer import LegalReviewerAgent


@pytest.mark.asyncio
async def test_legal_knowledge_base_search():
    matches = search_legal_knowledge_base("Is an employee non-compete enforceable?")
    assert len(matches) > 0
    assert any("noncompete" in m["topic"] or "contract" in m["topic"] for m in matches)
    assert matches[0]["is_verified"] is True


@pytest.mark.asyncio
async def test_facts_decomposition():
    agent = FactsAnalysisAgent()
    state = {"question": "Can I enforce a non-compete signed during employment with no pay raise?"}
    out = await agent.execute(state)
    assert len(out["facts_identified"]) > 0
    assert len(out["missing_information"]) > 0
    assert len(out["mapped_legal_issues"]) > 0


@pytest.mark.asyncio
async def test_legal_reviewer_mandatory_disclaimer():
    reviewer = LegalReviewerAgent()
    state = {
        "sources": [{"title": "Verified Statute", "citation": "16 CFR 910"}],
        "overall_explanation": "Based on contracts law, consideration is necessary.",
        "facts_identified": ["Contract signed without consideration"]
    }
    result = await reviewer.execute(state)
    assert result["audit_passed"] is True
    assert LEGAL_DISCLAIMER_TEXT in result["mandatory_disclaimer"]
