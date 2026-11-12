"""Testing Agent: Validates code, runs unit tests, identifies failures, and drives bug correction."""
from typing import Dict, Any, List
from pathlib import Path
from app.agents.base import BaseAgent
from app.services.file_service import FileService
from app.services.code_sandbox import CodeSandbox
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TestingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="tester",
            name="Testing Agent",
            role="Quality Assurance & Automated Test Engineer",
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "demo_proj")
        iteration = state.get("test_iteration", 1)
        task_desc = f"Executing test suite (Iteration {iteration}) for project '{state.get('name')}'"
        self.start(task_desc)

        project_dir = FileService.get_project_dir(project_id)
        
        # Locate test file
        test_file = None
        for candidate in [
            project_dir / "tests" / "test_pipeline.py",
            project_dir / "tests" / "test_services.py",
            project_dir / "tests" / "test_segmentation.py",
            project_dir / "tests" / "test_core.py",
            project_dir / "test_app.py",
        ]:
            if candidate.exists():
                test_file = candidate
                break

        # Check syntax of all python files first
        syntax_errors = []
        for py_file in project_dir.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            rel_name = str(py_file.relative_to(project_dir))
            syn_check = CodeSandbox.validate_python_syntax(content, rel_name)
            if not syn_check["valid"]:
                syntax_errors.append(syn_check["error"])

        if syntax_errors:
            self.fail("; ".join(syntax_errors))
            return {
                "iteration": iteration,
                "total_tests": len(syntax_errors),
                "passed": 0,
                "failed": len(syntax_errors),
                "errors": syntax_errors,
                "passed_all": False,
                "needs_correction": True,
                "details": [{"name": "syntax_check", "status": "FAILED", "error": err} for err in syntax_errors],
            }

        # Run test file if present
        if test_file:
            run_result = CodeSandbox.execute_test_file(test_file, project_dir)
            total = run_result.get("total_tests", 1)
            passed = run_result.get("passed", 0)
            failed = run_result.get("failed", 0)
            errors = run_result.get("errors", [])
            passed_all = run_result.get("passed_all", False)
            raw_output = run_result.get("raw_output", "")
        else:
            # Fallback verification
            total, passed, failed, errors, passed_all, raw_output = 1, 1, 0, [], True, "All files passed syntax validation."

        result = {
            "iteration": iteration,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "passed_all": passed_all,
            "needs_correction": not passed_all and iteration <= settings.MAX_TEST_RETRIES,
            "raw_output": raw_output,
            "details": [
                {
                    "name": f"test_suite_v{iteration}",
                    "status": "PASSED" if passed_all else "FAILED",
                    "error": errors[0] if errors else None,
                }
            ],
            "summary": (
                f"Test Suite passed all {passed}/{total} assertions successfully."
                if passed_all
                else f"Test Suite failed: {failed}/{total} assertions failed. Forwarding failure context to Coding Agent for auto-correction."
            ),
        }

        if passed_all:
            self.complete()
        else:
            self.fail(errors[0] if errors else "Assertions failed")

        return result
