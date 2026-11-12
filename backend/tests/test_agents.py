"""Unit tests for individual autonomous agents."""
import pytest
from app.agents.coordinator import CoordinatorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.coder import CodingAgent
from app.agents.tester import TestingAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.documenter import DocumentationAgent


@pytest.mark.asyncio
async def test_coordinator_classification():
    agent = CoordinatorAgent()
    state = {
        "name": "Fake News Detector",
        "user_request": "Build a machine learning fake news detector",
        "project_type": "ml"
    }
    result = await agent.execute(state)
    assert result["classified_type"] == "ml"
    assert "coder" in result["required_agents"]
    assert "tester" in result["required_agents"]


@pytest.mark.asyncio
async def test_planner_subtasks():
    agent = PlannerAgent()
    state = {
        "name": "Bus Management",
        "project_type": "web",
        "technologies": ["Python", "FastAPI"]
    }
    result = await agent.execute(state)
    assert len(result["subtasks"]) >= 4
    assert result["estimated_phases"] >= 4
    assert "coder" in result["required_agents"]


@pytest.mark.asyncio
async def test_researcher_domain_knowledge():
    agent = ResearcherAgent()
    state = {"name": "ML Project", "project_type": "ml"}
    result = await agent.execute(state)
    assert "algorithms_evaluated" in result
    assert len(result["sources_and_references"]) > 0


@pytest.mark.asyncio
async def test_coder_and_tester_loop():
    coder = CodingAgent()
    tester = TestingAgent()

    # Iteration 1: initial generation
    state = {
        "project_id": "test_proj_ml",
        "name": "Fake News ML",
        "project_type": "ml",
        "is_correction": False
    }
    coder_out = await coder.execute(state)
    assert coder_out["file_count"] > 3

    # Test iteration 1 (detects initial strict threshold or flaw)
    state["test_iteration"] = 1
    test_out = await tester.execute(state)
    # Testing agent should return structured result
    assert "total_tests" in test_out
    assert "passed" in test_out

    # Auto-Correction mode
    state["is_correction"] = True
    state["test_errors"] = test_out.get("errors", ["Threshold tuning required"])
    fixed_coder_out = await coder.execute(state)
    assert fixed_coder_out["is_correction"] is True

    # Test iteration 2 on fixed code
    state["test_iteration"] = 2
    retest_out = await tester.execute(state)
    print("DEBUG RETEST OUTPUT:", retest_out)
    assert retest_out["passed_all"] is True
    assert retest_out["failed"] == 0
