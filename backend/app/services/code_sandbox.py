"""Code Sandbox and Automated Test Execution Service."""
import ast
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List


class CodeSandbox:
    """Safely validates and executes generated code tests."""

    @staticmethod
    def validate_python_syntax(code_str: str, file_path: str = "") -> Dict[str, Any]:
        """Check code syntax without executing."""
        try:
            ast.parse(code_str)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"SyntaxError in {file_path} (line {e.lineno}): {e.msg}",
                "line": e.lineno,
                "offset": e.offset,
            }

    @staticmethod
    def execute_test_file(test_file_path: Path, cwd: Path) -> Dict[str, Any]:
        """Execute a Python test file using python or pytest in an isolated subprocess."""
        if not test_file_path.exists():
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 1,
                "errors": [f"Test file not found: {test_file_path}"],
                "details": [],
            }

        # Run with current python executable, -B (don't write/read bytecode), and relative test path
        rel_test_path = str(test_file_path.relative_to(cwd)).replace("\\", "/")
        cmd = [sys.executable, "-B", "-m", "unittest", rel_test_path]
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PYTHONPATH": str(cwd)},
            )
            stdout = result.stdout
            stderr = result.stderr
            combined = f"{stdout}\n{stderr}"

            # Parse unittest output
            passed = "OK" in stderr or "OK" in stdout
            total = 1
            details = []
            
            if "Ran " in stderr:
                try:
                    ran_part = stderr.split("Ran ")[1].split(" ")[0]
                    total = int(ran_part)
                except Exception:
                    total = 1

            if passed:
                return {
                    "total_tests": total,
                    "passed": total,
                    "failed": 0,
                    "errors": [],
                    "raw_output": combined,
                    "passed_all": True,
                    "details": [{"name": "unittest_suite", "status": "PASSED"}],
                }
            else:
                return {
                    "total_tests": total,
                    "passed": 0,
                    "failed": total,
                    "errors": [stderr.strip() or stdout.strip() or "Test failed"],
                    "raw_output": combined,
                    "passed_all": False,
                    "details": [
                        {
                            "name": "unittest_suite",
                            "status": "FAILED",
                            "error": stderr.strip() or stdout.strip(),
                        }
                    ],
                }
        except subprocess.TimeoutExpired:
            return {
                "total_tests": 1,
                "passed": 0,
                "failed": 1,
                "errors": ["Test execution timed out after 15 seconds."],
                "raw_output": "TimeoutExpired",
                "passed_all": False,
                "details": [{"name": "timeout", "status": "FAILED", "error": "Execution timed out"}],
            }
        except Exception as e:
            return {
                "total_tests": 1,
                "passed": 0,
                "failed": 1,
                "errors": [f"Failed to run test: {str(e)}"],
                "raw_output": str(e),
                "passed_all": False,
                "details": [{"name": "runner_error", "status": "FAILED", "error": str(e)}],
            }
