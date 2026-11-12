"""Agent Registry and Inspection Endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.session import get_db
from app.database.models import AgentRun, AgentMessage

router = APIRouter(prefix="/agents", tags=["agents"])

REGISTERED_AGENTS = [
    {
        "id": "coordinator",
        "name": "Coordinator Agent",
        "role": "Master Workflow Orchestrator & Task Decomposer",
        "capabilities": ["Task Classification", "Dependency Mapping", "Dynamic Routing", "Failure Recovery", "Aggregation"],
        "workflow": "Core Swarm",
    },
    {
        "id": "planner",
        "name": "Planner Agent",
        "role": "System Architect & Subtask Graph Builder",
        "capabilities": ["Requirements Breakdown", "Execution Scheduling", "Tech Stack Selection"],
        "workflow": "Core Swarm",
    },
    {
        "id": "researcher",
        "name": "Researcher Agent",
        "role": "Technical Research & Architectural Reference Specialist",
        "capabilities": ["Literature Review", "Algorithm Comparison", "Security Standard Verification"],
        "workflow": "Core Swarm",
    },
    {
        "id": "coder",
        "name": "Coding Agent",
        "role": "Lead Software Engineer & Code Synthesizer",
        "capabilities": ["Multi-File Codebase Generation", "Refactoring", "Automated Bug Fixing"],
        "workflow": "Core Swarm",
    },
    {
        "id": "tester",
        "name": "Testing Agent",
        "role": "QA Engineer & Closed-Loop Test Runner",
        "capabilities": ["AST Syntax Validation", "Unit Test Execution", "Defect Isolation", "Failure Traceback"],
        "workflow": "Core Swarm",
    },
    {
        "id": "reviewer",
        "name": "Reviewer Agent",
        "role": "Senior Code Auditor & Security Specialist",
        "capabilities": ["Security Auditing", "Code Quality Scoring", "PEP 8 Conformance", "Architecture Sign-off"],
        "workflow": "Core Swarm",
    },
    {
        "id": "documenter",
        "name": "Documentation Agent",
        "role": "Technical Author & Academic Report Compiler",
        "capabilities": ["22-Section Academic Documentation", "Star UML Synthesis", "Markdown Export"],
        "workflow": "Core Swarm",
    },
    # Transparent Legal AI Agents
    {
        "id": "legal_researcher",
        "name": "Legal Research Agent",
        "role": "Statutory Authority & Precedent Retrieval Specialist",
        "capabilities": ["Verified Citation Retrieval", "Anti-Hallucination Grounding", "Statutory Lookup"],
        "workflow": "Transparent Legal AI",
    },
    {
        "id": "facts_analyzer",
        "name": "Case/Facts Analysis Agent",
        "role": "Factual Decomposition & Issue Framing Specialist",
        "capabilities": ["Fact vs Assumption Isolation", "Missing Information Identification", "Issue Mapping"],
        "workflow": "Transparent Legal AI",
    },
    {
        "id": "risk_analyzer",
        "name": "Legal Risk Analysis Agent",
        "role": "Regulatory Exposure & Risk Matrix Assessor",
        "capabilities": ["Liability Assessment", "Regulatory Flux Tracking", "Uncertainty Quantification"],
        "workflow": "Transparent Legal AI",
    },
    {
        "id": "legal_explainer",
        "name": "Legal Explanation Agent",
        "role": "Plain Language Communicator & Source-to-Conclusion Tracer",
        "capabilities": ["Plain English Translation", "Source Tracing", "Limitation Articulation"],
        "workflow": "Transparent Legal AI",
    },
    {
        "id": "legal_reviewer",
        "name": "Legal Reviewer Agent",
        "role": "Citation Integrity & Ethical Warning Auditor",
        "capabilities": ["Overconfidence Pruning", "Statutory Disclaimer Enforcement", "Audit Trail Verification"],
        "workflow": "Transparent Legal AI",
    },
]


@router.get("")
def list_registered_agents():
    """Retrieve all 12 registered autonomous agents and their capabilities."""
    return {"total": len(REGISTERED_AGENTS), "agents": REGISTERED_AGENTS}


@router.get("/project/{project_id}/runs")
def get_project_agent_runs(project_id: str, db: Session = Depends(get_db)):
    """Retrieve all execution runs and messages for agents involved in a project."""
    runs = db.query(AgentRun).filter(AgentRun.project_id == project_id).all()
    messages = db.query(AgentMessage).filter(AgentMessage.project_id == project_id).all()
    return {"project_id": project_id, "runs": runs, "messages": messages}
