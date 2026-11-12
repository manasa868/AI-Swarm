"""Transparent Legal AI API Endpoints."""
import json
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db, SessionLocal
from app.database.models import LegalQuery, LegalSource
from app.schemas.legal import LegalQueryCreate, LegalQueryResponse, LegalSourceSchema
from app.legal.legal_knowledge_base import VERIFIED_LEGAL_DATABASE
from app.workflows.legal_workflow import LegalWorkflowEngine

router = APIRouter(prefix="/legal", tags=["transparent_legal_ai"])


@router.post("/analyze", response_model=LegalQueryResponse)
def create_legal_analysis(data: LegalQueryCreate, db: Session = Depends(get_db)):
    """Initialize a Transparent Legal AI analysis query."""
    query_id = f"legal_{uuid.uuid4().hex[:10]}"
    query_record = LegalQuery(
        id=query_id,
        question=data.question,
        jurisdiction=data.jurisdiction or "United States / General Common Law",
        status="PENDING",
        facts_identified=[],
        assumptions=[],
        missing_info=[],
        relevant_provisions=[],
        possible_issues=[],
        risks_uncertainties=[],
        limitations=[],
        disclaimer="Pending review by Legal Reviewer Agent.",
        created_at=datetime.datetime.utcnow(),
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)
    return query_record


@router.get("/{query_id}", response_model=LegalQueryResponse)
def get_legal_analysis(query_id: str, db: Session = Depends(get_db)):
    """Retrieve complete Transparent Legal AI analysis results."""
    record = db.query(LegalQuery).filter(LegalQuery.id == query_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Legal analysis record not found")
    return record


@router.get("/{query_id}/stream")
async def stream_legal_analysis(query_id: str):
    """Real-time SSE event stream for live Transparent Legal AI workflow."""
    db: Session = SessionLocal()
    query_record = db.query(LegalQuery).filter(LegalQuery.id == query_id).first()
    if not query_record:
        db.close()
        raise HTTPException(status_code=404, detail="Legal analysis record not found")

    async def event_generator():
        try:
            engine = LegalWorkflowEngine(db)
            async for event in engine.run_legal_analysis(
                query_id, query_record.question, query_record.jurisdiction
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            err = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(err)}\n\n"
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


@router.get("/sources/curated", response_model=List[LegalSourceSchema])
def list_curated_sources():
    """Retrieve curated verified statutory citations and case principles."""
    results = []
    for item in VERIFIED_LEGAL_DATABASE:
        results.append(
            LegalSourceSchema(
                id=item["id"],
                title=item["title"],
                source_type=item["source_type"],
                citation=item["citation"],
                url_or_ref=item.get("url_or_ref"),
                excerpt=item["excerpt"],
                relevance_score=1.0,
                is_verified=True,
            )
        )
    return results
