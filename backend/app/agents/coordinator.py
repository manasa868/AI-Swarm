"""Coordinator Agent: The central orchestrator that analyzes, decomposes, routes, and aggregates."""
from typing import Dict, Any, List, Optional
import datetime
from app.agents.base import BaseAgent


class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="coordinator",
            name="Coordinator Agent",
            role="Swarm Commander & Master Orchestrator",
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_request = state.get("user_request", "")
        project_type = state.get("project_type", "general")
        name = state.get("name", "Project")

        self.start(f"Analyzing prompt and structuring execution graph for '{name}'")

        # Classification check & validation
        classified_type = self._classify_project_type(user_request, project_type)
        
        # Decide workflow pipeline and parallel/sequential execution sequence
        if classified_type == "legal":
            required_agents = [
                "coordinator", "legal_researcher", "facts_analyzer",
                "risk_analyzer", "legal_explainer", "legal_reviewer"
            ]
            pipeline = ["Task Ingestion", "Legal Research", "Facts Decomposition", "Risk Assessment", "Plain Explanation", "Legal Review"]
        else:
            required_agents = [
                "coordinator", "planner", "researcher", "coder",
                "tester", "reviewer", "documenter"
            ]
            pipeline = [
                "Requirement Analysis",
                "Subtask Decomposition",
                "Technical Research",
                "Codebase Synthesis",
                "Sandbox Unit Testing",
                "Bug Auto-Correction (if needed)",
                "Security & Code Review",
                "Dynamic Documentation Compilation"
            ]

        output = {
            "classified_type": classified_type,
            "project_name": name,
            "required_agents": required_agents,
            "pipeline_stages": pipeline,
            "parallel_capable_stages": ["researcher", "coder"] if classified_type != "legal" else [],
            "max_test_retries": 3,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "summary": f"Coordinator classified project as '{classified_type.upper()}' and activated {len(required_agents)} specialized autonomous agents.",
        }

        self.complete()
        return output

    def _classify_project_type(self, user_request: str, explicit_type: str) -> str:
        req_lower = user_request.lower()
        if explicit_type and explicit_type != "general":
            return explicit_type
        if any(w in req_lower for w in ["machine learning", "ml", "fake news", "predict", "model", "train", "dataset"]):
            return "ml"
        if any(w in req_lower for w in ["web", "react", "fastapi", "bus", "management system", "dashboard", "crud"]):
            return "web"
        if any(w in req_lower for w in ["segmentation", "cluster", "data analysis", "rfm", "eda", "variance"]):
            return "data_analysis"
        if any(w in req_lower for w in ["legal", "contract", "law", "statute", "non-compete", "clause", "lawyer"]):
            return "legal"
        return "general"
