"""Pydantic schemas for Project and Execution APIs."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., example="Fake News Detection System")
    description: str = Field(..., example="Build a machine learning system to classify real and fake news.")
    project_type: str = Field(..., example="ml")  # ml, web, data_analysis, research, legal, general
    technologies: List[str] = Field(default_factory=list, example=["Python", "Scikit-Learn", "FastAPI"])
    files: Optional[List[str]] = Field(default_factory=list)


class TaskResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    assigned_agent: str
    dependencies: List[str]
    order_index: int
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class AgentRunResponse(BaseModel):
    id: str
    project_id: str
    agent_id: str
    agent_name: str
    task_description: Optional[str]
    status: str
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    output_payload: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    error_message: Optional[str]
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: float

    class Config:
        from_attributes = True


class AgentMessageResponse(BaseModel):
    id: str
    project_id: str
    from_agent: str
    to_agent: str
    message_type: str
    task_id: Optional[str]
    content: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime

    class Config:
        from_attributes = True


class TestResultResponse(BaseModel):
    id: str
    project_id: str
    iteration: int
    total_tests: int
    passed: int
    failed: int
    skipped: int
    details: List[Dict[str, Any]]
    passed_all: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: str
    project_id: str
    reviewer_agent: str
    code_quality_score: float
    security_score: float
    architecture_score: float
    approved: bool
    summary: str
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    project_id: str
    title: str
    content_markdown: str
    sections: Dict[str, Any]
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    project_type: str
    technologies: List[str]
    status: str
    progress: float
    current_agent: Optional[str]
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    execution_summary: Dict[str, Any] = Field(default_factory=dict)
    generated_path: Optional[str]
    tasks: List[TaskResponse] = Field(default_factory=list)
    agent_runs: List[AgentRunResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
