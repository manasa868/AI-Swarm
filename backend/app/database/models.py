"""SQLAlchemy database models for AI Swarm and Transparent Legal AI."""
import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
    Float,
)
from sqlalchemy.orm import relationship
from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    legal_queries = relationship("LegalQuery", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    project_type = Column(
        String(50), nullable=False
    )  # ml, web, data_analysis, research, legal, general
    technologies = Column(JSON, default=list)
    status = Column(
        String(30), default="PENDING"
    )  # PENDING, QUEUED, RUNNING, COMPLETED, FAILED, RETRYING, CANCELLED
    progress = Column(Float, default=0.0)
    current_agent = Column(String(50), nullable=True)
    retry_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_summary = Column(JSON, default=dict)
    generated_path = Column(String(512), nullable=True)

    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="project", cascade="all, delete-orphan")
    messages = relationship("AgentMessage", back_populates="project", cascade="all, delete-orphan")
    workflow_states = relationship("WorkflowState", back_populates="project", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="project", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    assigned_agent = Column(String(50), nullable=False)
    dependencies = Column(JSON, default=list)
    order_index = Column(Integer, default=0)
    status = Column(
        String(30), default="PENDING"
    )  # PENDING, RUNNING, COMPLETED, FAILED, RETRYING
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result_data = Column(JSON, default=dict)

    project = relationship("Project", back_populates="tasks")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    capabilities = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    agent_id = Column(String(50), nullable=False)
    agent_name = Column(String(100), nullable=False)
    task_description = Column(Text, nullable=True)
    status = Column(
        String(30), default="WAITING"
    )  # WAITING, RUNNING, COMPLETED, FAILED, RETRYING
    input_payload = Column(JSON, default=dict)
    output_payload = Column(JSON, default=dict)
    dependencies = Column(JSON, default=list)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)

    project = relationship("Project", back_populates="agent_runs")


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    from_agent = Column(String(50), nullable=False)
    to_agent = Column(String(50), nullable=False)
    message_type = Column(
        String(50), nullable=False
    )  # TASK_ASSIGNMENT, TASK_RESULT, ERROR, REVIEW, TEST_RESULT, RETRY, FINAL_RESULT
    task_id = Column(String(64), nullable=True)
    content = Column(Text, nullable=False)
    data = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="messages")


class WorkflowState(Base):
    __tablename__ = "workflow_states"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    current_phase = Column(String(50), nullable=False)
    state_snapshot = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="workflow_states")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    test_type = Column(String(50), default="unit")  # unit, integration, syntax, security
    expected_result = Column(Text, nullable=True)


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    iteration = Column(Integer, default=1)
    total_tests = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    skipped = Column(Integer, default=0)
    details = Column(JSON, default=list)  # list of {name, status, error, traceback}
    raw_output = Column(Text, nullable=True)
    passed_all = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="test_results")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    reviewer_agent = Column(String(50), default="Reviewer Agent")
    code_quality_score = Column(Float, default=0.0)  # out of 10
    security_score = Column(Float, default=0.0)
    architecture_score = Column(Float, default=0.0)
    approved = Column(Boolean, default=False)
    summary = Column(Text, nullable=False)
    findings = Column(JSON, default=list)  # list of {severity, category, message}
    recommendations = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="reviews")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content_markdown = Column(Text, nullable=False)
    sections = Column(JSON, default=dict)
    file_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="documents")


class LegalQuery(Base):
    __tablename__ = "legal_queries"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=False)
    jurisdiction = Column(String(100), default="General / Multi-Jurisdictional")
    facts_identified = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)
    missing_info = Column(JSON, default=list)
    relevant_provisions = Column(JSON, default=list)
    analysis = Column(Text, nullable=True)
    possible_issues = Column(JSON, default=list)
    risks_uncertainties = Column(JSON, default=list)
    explanation = Column(Text, nullable=True)
    limitations = Column(JSON, default=list)
    disclaimer = Column(Text, nullable=False)
    status = Column(String(30), default="PENDING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="legal_queries")
    sources = relationship("LegalSource", back_populates="legal_query", cascade="all, delete-orphan")


class LegalSource(Base):
    __tablename__ = "legal_sources"

    id = Column(String(64), primary_key=True, index=True)
    legal_query_id = Column(String(64), ForeignKey("legal_queries.id"), nullable=False)
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # statute, precedent, regulation, treaty
    citation = Column(String(255), nullable=False)
    url_or_ref = Column(String(512), nullable=True)
    excerpt = Column(Text, nullable=False)
    relevance_score = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=True)

    legal_query = relationship("LegalQuery", back_populates="sources")
