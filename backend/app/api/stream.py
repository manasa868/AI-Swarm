"""Server-Sent Events (SSE) Streaming Endpoints for Live Swarm Telemetry."""
import json
import asyncio
import logging
import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.session import get_db, SessionLocal
from app.database.models import AgentRun, Project
from app.workflows.engine import SwarmWorkflowEngine

router = APIRouter(prefix="/projects", tags=["streaming"])
logger = logging.getLogger(__name__)


@router.get("/{project_id}/stream")
async def stream_project_execution(project_id: str):
    """Real-time SSE event stream for multi-agent swarm execution."""
    # Create an independent DB session for streaming lifecycle
    db: Session = SessionLocal()
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        db.close()
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "PENDING":
        db.close()
        raise HTTPException(
            status_code=409,
            detail=f"Project execution cannot start from status {project.status}.",
        )

    async def event_generator():
        try:
            engine = SwarmWorkflowEngine(db)
            async for event in engine.execute_swarm(project_id):
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0.05)
        except Exception as e:
            logger.exception("Swarm execution failed for project %s", project_id)
            db.rollback()
            failed_project = db.query(Project).filter(Project.id == project_id).first()
            if failed_project and failed_project.status != "CANCELLED":
                failed_project.status = "FAILED"
                failed_project.current_agent = None
                failed_project.error_message = str(e)
                failed_project.completed_at = datetime.datetime.utcnow()
                for run in db.query(AgentRun).filter(
                    AgentRun.project_id == project_id,
                    AgentRun.status == "RUNNING",
                ):
                    run.status = "FAILED"
                    run.error_message = str(e)
                    run.completed_at = failed_project.completed_at
                db.commit()
            err_data = {"type": "error", "message": f"Execution error: {str(e)}"}
            yield f"data: {json.dumps(err_data)}\n\n"
        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
