"""AI Swarm Master Workflow Engine: Stateful Orchestration with Closed-Loop Testing & Retries."""
import asyncio
import datetime
import uuid
from typing import Dict, Any, AsyncGenerator, List, Optional
from sqlalchemy.orm import Session
from app.database.models import (
    Project,
    Task,
    AgentRun,
    AgentMessage,
    WorkflowState,
    TestResult,
    Review,
    Document,
)
from app.agents.coordinator import CoordinatorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.coder import CodingAgent
from app.agents.tester import TestingAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.documenter import DocumentationAgent
from app.config import settings
from app.services.file_service import FileService
from app.services.uml_service import generate_project_diagrams


class SwarmWorkflowEngine:
    def __init__(self, db: Session):
        self.db = db
        self.coordinator = CoordinatorAgent()
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.coder = CodingAgent()
        self.tester = TestingAgent()
        self.reviewer = ReviewerAgent()
        self.documenter = DocumentationAgent()
        self._current_project_id: Optional[str] = None
        self._active_run_ids: Dict[str, str] = {}

    async def execute_swarm(self, project_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute complete multi-agent workflow yielding real-time events for SSE."""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            yield {"type": "error", "message": f"Project {project_id} not found"}
            return

        self._current_project_id = project_id
        project.status = "RUNNING"
        project.started_at = datetime.datetime.utcnow()
        project.progress = 5.0
        project.current_agent = "Coordinator Agent"
        self.db.commit()

        yield {
            "type": "project_status",
            "project_id": project_id,
            "status": "RUNNING",
            "progress": 5.0,
            "current_agent": "Coordinator Agent",
            "message": "Swarm initialized. Coordinator starting task analysis.",
        }
        await asyncio.sleep(0.4)

        state: Dict[str, Any] = {
            "project_id": project_id,
            "name": project.name,
            "user_request": project.description,
            "project_type": project.project_type,
            "technologies": project.technologies or [],
            "subtasks": [],
            "active_agent": "coordinator",
            "agent_outputs": {},
            "test_results": {},
            "review_results": {},
            "errors": [],
            "retries": 0,
            "final_result": {},
        }

        # -------------------------------------------------------------
        # STEP 1: COORDINATOR AGENT
        # -------------------------------------------------------------
        yield await self._record_and_emit_agent_start("coordinator", "Coordinator Agent", "Analyzing task and classifying workflow")
        coord_output = await self.coordinator.execute(state)
        state["agent_outputs"]["coordinator"] = coord_output
        state["project_type"] = coord_output["classified_type"]
        project.project_type = coord_output["classified_type"]
        project.progress = 15.0
        self.db.commit()

        yield await self._record_and_emit_agent_complete("coordinator", "Coordinator Agent", coord_output)
        await asyncio.sleep(0.5)

        # -------------------------------------------------------------
        # STEP 2: PLANNER AGENT
        # -------------------------------------------------------------
        project.current_agent = "Planner Agent"
        project.progress = 25.0
        self.db.commit()
        yield await self._record_and_emit_agent_start("planner", "Planner Agent", "Decomposing requirements into subtasks")
        
        planner_output = await self.planner.execute(state)
        state["agent_outputs"]["planner"] = planner_output
        state["subtasks"] = planner_output.get("subtasks", [])

        # Persist subtasks into DB
        for st in state["subtasks"]:
            db_task = Task(
                id=st["id"],
                project_id=project_id,
                title=st["title"],
                description=st["description"],
                assigned_agent=st["assigned_agent"],
                dependencies=st.get("dependencies", []),
                order_index=st.get("order_index", 0),
                status="PENDING",
            )
            self.db.add(db_task)
        self.db.commit()

        self._create_message("coordinator", "planner", "TASK_ASSIGNMENT", "Plan generated with subtasks.", data=planner_output)
        yield await self._record_and_emit_agent_complete("planner", "Planner Agent", planner_output)
        await asyncio.sleep(0.5)

        # -------------------------------------------------------------
        # STEP 3: RESEARCHER AGENT
        # -------------------------------------------------------------
        project.current_agent = "Researcher Agent"
        project.progress = 40.0
        self.db.commit()
        yield await self._record_and_emit_agent_start("researcher", "Researcher Agent", "Investigating architectural patterns and standards")

        research_output = await self.researcher.execute(state)
        state["agent_outputs"]["researcher"] = research_output

        self._create_message("planner", "researcher", "TASK_RESULT", "Technical research completed.", data=research_output)
        yield await self._record_and_emit_agent_complete("researcher", "Researcher Agent", research_output)
        await asyncio.sleep(0.5)

        # -------------------------------------------------------------
        # STEP 4: CODING AGENT (Iteration 1)
        # -------------------------------------------------------------
        project.current_agent = "Coding Agent"
        project.progress = 55.0
        self.db.commit()
        yield await self._record_and_emit_agent_start("coder", "Coding Agent", "Synthesizing modular multi-file codebase")

        state["is_correction"] = False
        coder_output = await self.coder.execute(state)
        state["agent_outputs"]["coder"] = coder_output

        self._create_message("researcher", "coder", "TASK_ASSIGNMENT", "Code files generated on disk.", data=coder_output)
        yield await self._record_and_emit_agent_complete("coder", "Coding Agent", coder_output)
        await asyncio.sleep(0.5)

        # -------------------------------------------------------------
        # STEP 4.5: PROJECT-SPECIFIC UML ANALYSIS & GENERATION
        # -------------------------------------------------------------
        project.current_agent = "UML Diagram Generator"
        project.progress = 63.0
        self.db.commit()
        yield {
            "type": "diagrams_generating",
            "project_id": project_id,
            "message": "Analyzing generated source code and creating UML diagrams.",
        }
        try:
            diagram_manifest = generate_project_diagrams(
                project_id,
                project.name,
                project.description,
            )
        except (OSError, ValueError, SyntaxError) as exc:
            raise RuntimeError(f"UML generation failed: {exc}") from exc
        state["uml_diagrams"] = diagram_manifest
        self._create_message(
            "coder",
            "reviewer",
            "TASK_RESULT",
            "Generated source analyzed; five project-specific UML diagrams saved.",
            data={"diagrams": list(diagram_manifest)},
        )
        yield {
            "type": "diagrams_generated",
            "project_id": project_id,
            "diagrams": list(diagram_manifest.values()),
            "message": f"Generated {len(diagram_manifest)} UML diagrams from project source.",
        }

        # -------------------------------------------------------------
        # STEP 5: TESTING AGENT & CLOSED-LOOP CORRECTION
        # -------------------------------------------------------------
        project.current_agent = "Testing Agent"
        project.progress = 70.0
        self.db.commit()
        test_output: Dict[str, Any] = {}
        for iteration in range(1, settings.MAX_TEST_RETRIES + 2):
            state["test_iteration"] = iteration
            project.current_agent = "Testing Agent" if iteration == 1 else "Testing Agent (Re-test)"
            project.status = "RUNNING"
            self.db.commit()
            task_desc = (
                "Running automated unit tests in sandbox"
                if iteration == 1
                else f"Re-running test suite after correction attempt {iteration - 1}"
            )
            yield await self._record_and_emit_agent_start("tester", "Testing Agent", task_desc)

            test_output = await self.tester.execute(state)
            state["test_results"] = test_output
            self._record_db_test_result(project_id, iteration, test_output)
            yield await self._record_and_emit_agent_complete("tester", "Testing Agent", test_output)

            if test_output.get("passed_all"):
                break

            if iteration > settings.MAX_TEST_RETRIES:
                project.status = "FAILED"
                project.progress = 70.0
                project.current_agent = None
                project.error_message = (
                    f"Tests still failing after {settings.MAX_TEST_RETRIES} correction attempts."
                )
                project.completed_at = datetime.datetime.utcnow()
                self.db.commit()
                yield {
                    "type": "workflow_failed",
                    "project_id": project_id,
                    "status": "FAILED",
                    "progress": project.progress,
                    "retry_count": project.retry_count,
                    "test_results": test_output,
                    "message": project.error_message,
                }
                return

            project.retry_count = iteration
            project.status = "RETRYING"
            self.db.commit()
            yield {
                "type": "test_failure_detected",
                "iteration": iteration,
                "retry_count": iteration,
                "errors": test_output.get("errors", []),
                "message": (
                    f"Testing Agent identified defects. Forwarding failure context to "
                    f"Coding Agent for correction attempt {iteration} of {settings.MAX_TEST_RETRIES}."
                ),
            }
            self._create_message(
                "tester",
                "coder",
                "ERROR",
                "Unit test failure detected. Code correction requested.",
                data=test_output,
            )

            project.current_agent = "Coding Agent (Auto-Fix)"
            self.db.commit()
            yield await self._record_and_emit_agent_start(
                "coder",
                "Coding Agent",
                f"Applying correction attempt {iteration} based on test failure",
            )
            state["is_correction"] = True
            state["test_errors"] = test_output.get("errors", [])
            coder_output = await self.coder.execute(state)
            state["agent_outputs"]["coder"] = coder_output
            self._create_message(
                "coder",
                "tester",
                "RETRY",
                "Code correction completed; re-test requested.",
                data=coder_output,
            )
            yield await self._record_and_emit_agent_complete("coder", "Coding Agent", coder_output)
            diagram_manifest = generate_project_diagrams(
                project_id,
                project.name,
                project.description,
            )
            state["uml_diagrams"] = diagram_manifest
            yield {
                "type": "diagrams_generated",
                "project_id": project_id,
                "diagrams": list(diagram_manifest.values()),
                "message": "Updated UML diagrams to match the corrected source code.",
            }

        # -------------------------------------------------------------
        # STEP 6: REVIEWER AGENT
        # -------------------------------------------------------------
        project.current_agent = "Reviewer Agent"
        project.progress = 85.0
        self.db.commit()
        yield await self._record_and_emit_agent_start("reviewer", "Reviewer Agent", "Auditing code quality, security posture, and architecture")

        state["review_results"] = await self.reviewer.execute(state)
        review_output = state["review_results"]

        # Persist review
        db_review = Review(
            id=f"rev_{uuid.uuid4().hex[:10]}",
            project_id=project_id,
            reviewer_agent="Reviewer Agent",
            code_quality_score=review_output["code_quality_score"],
            security_score=review_output["security_score"],
            architecture_score=review_output["architecture_score"],
            approved=review_output["approved"],
            summary=review_output["summary"],
            findings=review_output["findings"],
            recommendations=review_output["recommendations"],
        )
        self.db.add(db_review)
        self.db.commit()

        self._create_message("tester", "reviewer", "REVIEW", "Test results approved for final review.", data=review_output)
        yield await self._record_and_emit_agent_complete("reviewer", "Reviewer Agent", review_output)
        await asyncio.sleep(0.5)

        # -------------------------------------------------------------
        # STEP 7: DOCUMENTATION AGENT
        # -------------------------------------------------------------
        project.current_agent = "Documentation Agent"
        project.progress = 95.0
        self.db.commit()
        yield await self._record_and_emit_agent_start("documenter", "Documentation Agent", "Compiling dynamic 22-section major project report")

        doc_output = await self.documenter.execute(state)
        state["agent_outputs"]["documenter"] = doc_output

        # Persist document
        db_doc = Document(
            id=f"doc_{uuid.uuid4().hex[:10]}",
            project_id=project_id,
            title=doc_output["document_title"],
            content_markdown=doc_output["markdown_content"],
            sections=doc_output["sections"],
            file_path=doc_output["file_path"],
        )
        self.db.add(db_doc)
        self.db.commit()

        self._create_message("reviewer", "documenter", "FINAL_RESULT", "Academic documentation generated.", data=doc_output)
        yield await self._record_and_emit_agent_complete("documenter", "Documentation Agent", doc_output)
        await asyncio.sleep(0.4)

        # -------------------------------------------------------------
        # FINAL WRAPUP
        # -------------------------------------------------------------
        project.status = "COMPLETED"
        project.progress = 100.0
        project.current_agent = None
        project.completed_at = datetime.datetime.utcnow()
        project.generated_path = str(FileService.get_project_dir(project_id))
        project.execution_summary = {
            "total_agents": 7,
            "tasks_completed": len(state["subtasks"]),
            "tests_passed": test_output.get("passed", 0),
            "total_tests": test_output.get("total_tests", 0),
            "files_generated": len(coder_output.get("generated_files", [])),
            "review_score": review_output.get("overall_score", 9.5),
            "docs_sections": doc_output.get("section_count", 22),
            "uml_diagrams": len(state.get("uml_diagrams", {})),
        }
        self.db.commit()

        yield {
            "type": "workflow_completed",
            "project_id": project_id,
            "status": "COMPLETED",
            "progress": 100.0,
            "execution_summary": project.execution_summary,
            "file_tree": FileService.get_file_tree(project_id),
            "documentation": doc_output,
            "message": "AI Swarm completed all phases successfully.",
        }

    async def _record_and_emit_agent_start(self, agent_id: str, agent_name: str, task_desc: str) -> Dict[str, Any]:
        """Persist a running agent record and format its start event."""
        now = datetime.datetime.utcnow()
        run_record = AgentRun(
            id=f"run_{uuid.uuid4().hex[:10]}",
            project_id=self._current_project_id,
            agent_id=agent_id,
            agent_name=agent_name,
            task_description=task_desc,
            status="RUNNING",
            started_at=now,
        )
        self.db.add(run_record)
        self.db.commit()
        self._active_run_ids[agent_id] = run_record.id
        project = self.db.query(Project).filter(Project.id == self._current_project_id).first()
        return {
            "type": "agent_started",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "task": task_desc,
            "progress": project.progress if project else 0.0,
            "timestamp": now.isoformat(),
        }

    async def _record_and_emit_agent_complete(self, agent_id: str, agent_name: str, output_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.datetime.utcnow()
        run_id = self._active_run_ids.get(agent_id)
        run_record = self.db.query(AgentRun).filter(AgentRun.id == run_id).first() if run_id else None
        if run_record:
            run_record.status = "COMPLETED"
            run_record.output_payload = output_data
            run_record.completed_at = now
            if run_record.started_at:
                run_record.duration_seconds = max(
                    0.0, (now - run_record.started_at).total_seconds()
                )
            self.db.commit()
        return {
            "type": "agent_completed",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "output": output_data,
            "summary": output_data.get("summary", ""),
            "timestamp": now.isoformat(),
        }

    def _create_message(self, from_agent: str, to_agent: str, msg_type: str, content: str, data: Dict[str, Any] = None):
        if not self._current_project_id:
            raise RuntimeError("Cannot persist an agent message without an active project.")
        msg = AgentMessage(
            id=f"msg_{uuid.uuid4().hex[:10]}",
            project_id=self._current_project_id,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=msg_type,
            content=content,
            data=data or {},
            timestamp=datetime.datetime.utcnow(),
        )
        self.db.add(msg)
        self.db.commit()

    def _record_db_test_result(self, project_id: str, iteration: int, test_output: Dict[str, Any]):
        db_res = TestResult(
            id=f"test_{uuid.uuid4().hex[:10]}",
            project_id=project_id,
            iteration=iteration,
            total_tests=test_output.get("total_tests", 0),
            passed=test_output.get("passed", 0),
            failed=test_output.get("failed", 0),
            skipped=test_output.get("skipped", 0),
            details=test_output.get("details", []),
            raw_output=test_output.get("raw_output", ""),
            passed_all=test_output.get("passed_all", False),
        )
        self.db.add(db_res)
        self.db.commit()
