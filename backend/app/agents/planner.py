"""Planner Agent: Decomposes requirements into structured subtasks with dependencies."""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
import uuid


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="planner",
            name="Planner Agent",
            role="System Architect & Task Decomposer",
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        task_desc = f"Analyzing requirements and decomposing project '{state.get('name')}'"
        self.start(task_desc)

        user_req = state.get("user_request", "")
        project_type = state.get("project_type", "general")
        tech_stack = state.get("technologies", [])

        # Domain-driven subtask decomposition
        if project_type == "ml":
            subtasks = [
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Data Pipeline & Preprocessing",
                    "description": "Design data ingestion, cleaning, TF-IDF / vectorization pipeline, and train/test split.",
                    "assigned_agent": "researcher",
                    "dependencies": [],
                    "order_index": 1,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Model Architecture & Training Script",
                    "description": "Implement machine learning classifier, training loop, hyperparameter tuning, and metric evaluation.",
                    "assigned_agent": "coder",
                    "dependencies": ["Data Pipeline & Preprocessing"],
                    "order_index": 2,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "REST API Inference Server",
                    "description": "Expose trained model with FastAPI inference endpoints, request validation, and prediction responses.",
                    "assigned_agent": "coder",
                    "dependencies": ["Model Architecture & Training Script"],
                    "order_index": 3,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Automated Unit & Integration Testing",
                    "description": "Execute automated test suites for data pipeline, model prediction sanity, and API endpoints.",
                    "assigned_agent": "tester",
                    "dependencies": ["REST API Inference Server"],
                    "order_index": 4,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Security & Architecture Review",
                    "description": "Audit model serialization safety, input boundary sanitization, and architectural compliance.",
                    "assigned_agent": "reviewer",
                    "dependencies": ["Automated Unit & Integration Testing"],
                    "order_index": 5,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Comprehensive College Documentation",
                    "description": "Synthesize complete 22-section project documentation and Star UML diagrams.",
                    "assigned_agent": "documenter",
                    "dependencies": ["Security & Architecture Review"],
                    "order_index": 6,
                },
            ]
        elif project_type == "web":
            subtasks = [
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Database Schema & Entity Models",
                    "description": "Design relational models (Admin, Student, Driver, Bus, Route, Assignment).",
                    "assigned_agent": "researcher",
                    "dependencies": [],
                    "order_index": 1,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Backend REST API Services",
                    "description": "Implement CRUD endpoints, authentication hooks, route tracking, and business logic.",
                    "assigned_agent": "coder",
                    "dependencies": ["Database Schema & Entity Models"],
                    "order_index": 2,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "API & Logic Testing",
                    "description": "Validate API contract, edge cases, route assignments, and data persistence.",
                    "assigned_agent": "tester",
                    "dependencies": ["Backend REST API Services"],
                    "order_index": 3,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Code Review & Quality Assurance",
                    "description": "Verify code quality, security vulnerabilities, SQL injection safety, and modularity.",
                    "assigned_agent": "reviewer",
                    "dependencies": ["API & Logic Testing"],
                    "order_index": 4,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Dynamic Documentation Generation",
                    "description": "Generate system architecture, module specifications, and user manual.",
                    "assigned_agent": "documenter",
                    "dependencies": ["Code Review & Quality Assurance"],
                    "order_index": 5,
                },
            ]
        elif project_type == "data_analysis":
            subtasks = [
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Exploratory Data Analysis & Strategy",
                    "description": "Formulate clustering strategy (RFM analysis, PCA, KMeans) and metrics.",
                    "assigned_agent": "researcher",
                    "dependencies": [],
                    "order_index": 1,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Data Pipeline & Clustering Engine",
                    "description": "Implement data cleaning, scaling, KMeans clustering, silhouette evaluation, and export.",
                    "assigned_agent": "coder",
                    "dependencies": ["Exploratory Data Analysis & Strategy"],
                    "order_index": 2,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Statistical Validation & Test Suite",
                    "description": "Validate cluster coherence, null handling, and statistical thresholds.",
                    "assigned_agent": "tester",
                    "dependencies": ["Data Pipeline & Clustering Engine"],
                    "order_index": 3,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Methodology Review",
                    "description": "Review clustering assumptions, dimensionality reduction, and segment explainability.",
                    "assigned_agent": "reviewer",
                    "dependencies": ["Statistical Validation & Test Suite"],
                    "order_index": 4,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Analytics Report & Documentation",
                    "description": "Compile analytical findings, business interpretations, and methodology report.",
                    "assigned_agent": "documenter",
                    "dependencies": ["Methodology Review"],
                    "order_index": 5,
                },
            ]
        else:
            # General software tasks
            subtasks = [
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Requirements & Technical Specification",
                    "description": "Define interfaces, functional constraints, and library stack.",
                    "assigned_agent": "researcher",
                    "dependencies": [],
                    "order_index": 1,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Core Implementation",
                    "description": "Develop modular codebase adhering to design patterns and solid principles.",
                    "assigned_agent": "coder",
                    "dependencies": ["Requirements & Technical Specification"],
                    "order_index": 2,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Automated Unit Testing",
                    "description": "Create and execute unit tests, verifying edge cases and error handling.",
                    "assigned_agent": "tester",
                    "dependencies": ["Core Implementation"],
                    "order_index": 3,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "Quality & Security Review",
                    "description": "Perform static analysis, cyclomatic complexity check, and code quality review.",
                    "assigned_agent": "reviewer",
                    "dependencies": ["Automated Unit Testing"],
                    "order_index": 4,
                },
                {
                    "id": f"task_{uuid.uuid4().hex[:8]}",
                    "title": "System Documentation",
                    "description": "Generate comprehensive project guide and technical manuals.",
                    "assigned_agent": "documenter",
                    "dependencies": ["Quality & Security Review"],
                    "order_index": 5,
                },
            ]

        output = {
            "subtasks": subtasks,
            "execution_order": [t["title"] for t in subtasks],
            "estimated_phases": len(subtasks),
            "required_agents": list(set([t["assigned_agent"] for t in subtasks])),
            "technology_recommendations": tech_stack or ["Python", "FastAPI", "SQLite", "PyTest"],
            "summary": f"Decomposed project into {len(subtasks)} structured subtasks with dependency management.",
        }

        self.complete()
        return output
