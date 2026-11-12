"""Integration tests for persisted swarm execution and retry limits."""
import uuid
import shutil

import pytest

from app.config import settings
from app.database.models import AgentMessage, AgentRun, Project, TestResult as ResultRecord
from app.database.session import SessionLocal
from app.services.file_service import FileService
from app.workflows.engine import SwarmWorkflowEngine


@pytest.mark.asyncio
async def test_swarm_persists_agent_activity_and_stops_after_retry_limit():
    db = SessionLocal()
    project_id = f"workflow_test_{uuid.uuid4().hex[:12]}"
    project = Project(
        id=project_id,
        name="Workflow persistence test",
        description="Exercise persisted agent runs and bounded test retries.",
        project_type="general",
        technologies=[],
        status="PENDING",
    )
    db.add(project)
    db.commit()

    engine = SwarmWorkflowEngine(db)

    async def coordinator(_state):
        return {"classified_type": "general", "summary": "Classified test project."}

    async def planner(_state):
        return {"subtasks": [], "summary": "Created test plan."}

    async def researcher(_state):
        return {"summary": "Research completed."}

    async def coder(state):
        FileService.write_project_files(project_id, {"core.py": "class GeneratedCore:\n    pass\n"})
        return {"generated_files": ["core.py"], "summary": "Code generated."}

    async def failing_tester(state):
        iteration = state["test_iteration"]
        return {
            "iteration": iteration,
            "total_tests": 1,
            "passed": 0,
            "failed": 1,
            "errors": ["Expected a passing result."],
            "passed_all": False,
            "needs_correction": iteration <= settings.MAX_TEST_RETRIES,
            "details": [{"name": "sample", "status": "FAILED"}],
            "summary": "One test failed.",
        }

    engine.coordinator.execute = coordinator
    engine.planner.execute = planner
    engine.researcher.execute = researcher
    engine.coder.execute = coder
    engine.tester.execute = failing_tester

    try:
        events = [event async for event in engine.execute_swarm(project_id)]

        db.refresh(project)
        runs = db.query(AgentRun).filter(AgentRun.project_id == project_id).all()
        messages = db.query(AgentMessage).filter(AgentMessage.project_id == project_id).all()
        results = db.query(ResultRecord).filter(ResultRecord.project_id == project_id).all()

        assert events[-1]["type"] == "workflow_failed"
        assert project.status == "FAILED"
        assert project.retry_count == settings.MAX_TEST_RETRIES
        assert len(results) == settings.MAX_TEST_RETRIES + 1
        assert sum(run.agent_id == "coder" for run in runs) == settings.MAX_TEST_RETRIES + 1
        assert runs and all(run.status == "COMPLETED" for run in runs)
        assert messages and all(message.project_id == project_id for message in messages)
    finally:
        db.delete(project)
        db.commit()
        db.close()
        shutil.rmtree(settings.GENERATED_DIR / project_id, ignore_errors=True)
