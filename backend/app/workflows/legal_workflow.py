"""Transparent Legal AI Workflow Engine."""
import asyncio
import datetime
import uuid
from typing import Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session
from app.legal.legal_researcher import LegalResearchAgent
from app.legal.facts_analyzer import FactsAnalysisAgent
from app.legal.risk_analyzer import LegalRiskAnalysisAgent
from app.legal.legal_explainer import LegalExplanationAgent
from app.legal.legal_reviewer import LegalReviewerAgent
from app.database.models import LegalQuery, LegalSource


class LegalWorkflowEngine:
    def __init__(self, db: Session):
        self.db = db
        self.researcher = LegalResearchAgent()
        self.facts_analyzer = FactsAnalysisAgent()
        self.risk_analyzer = LegalRiskAnalysisAgent()
        self.explainer = LegalExplanationAgent()
        self.reviewer = LegalReviewerAgent()

    async def run_legal_analysis(
        self, query_id: str, question: str, jurisdiction: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute transparent legal research workflow, yielding real-time events."""
        # Find query record
        query_record = self.db.query(LegalQuery).filter(LegalQuery.id == query_id).first()
        if not query_record:
            query_record = LegalQuery(
                id=query_id,
                question=question,
                jurisdiction=jurisdiction,
                status="RUNNING",
                disclaimer="Initializing analysis...",
            )
            self.db.add(query_record)
            self.db.commit()

        query_record.status = "RUNNING"
        self.db.commit()

        yield {
            "type": "workflow_started",
            "query_id": query_id,
            "stage": "COORDINATOR",
            "message": "Coordinator initialized Transparent Legal AI Workflow.",
        }
        await asyncio.sleep(0.5)

        state = {
            "query_id": query_id,
            "question": question,
            "jurisdiction": jurisdiction,
        }

        # Step 1: Legal Research
        yield {
            "type": "agent_started",
            "agent": "Legal Research Agent",
            "message": "Querying verified statutory databases and legal authorities...",
        }
        research_out = await self.researcher.execute(state)
        state.update(research_out)
        
        # Persist sources
        for s in research_out.get("sources", []):
            db_source = LegalSource(
                id=f"src_{uuid.uuid4().hex[:10]}",
                legal_query_id=query_id,
                title=s["title"],
                source_type=s["source_type"],
                citation=s["citation"],
                url_or_ref=s.get("url_or_ref"),
                excerpt=s["excerpt"],
                relevance_score=s.get("relevance_score", 1.0),
                is_verified=True,
            )
            self.db.add(db_source)
        self.db.commit()

        yield {
            "type": "agent_completed",
            "agent": "Legal Research Agent",
            "data": research_out,
        }
        await asyncio.sleep(0.5)

        # Step 2: Facts Analysis
        yield {
            "type": "agent_started",
            "agent": "Case/Facts Analysis Agent",
            "message": "Extracting facts, isolating assumptions, and framing legal issues...",
        }
        facts_out = await self.facts_analyzer.execute(state)
        state.update(facts_out)
        yield {
            "type": "agent_completed",
            "agent": "Case/Facts Analysis Agent",
            "data": facts_out,
        }
        await asyncio.sleep(0.5)

        # Step 3: Legal Risk Analysis
        yield {
            "type": "agent_started",
            "agent": "Legal Risk Analysis Agent",
            "message": "Synthesizing exposure matrix and assessing regulatory flux...",
        }
        risk_out = await self.risk_analyzer.execute(state)
        state.update(risk_out)
        yield {
            "type": "agent_completed",
            "agent": "Legal Risk Analysis Agent",
            "data": risk_out,
        }
        await asyncio.sleep(0.5)

        # Step 4: Legal Explanation
        yield {
            "type": "agent_started",
            "agent": "Legal Explanation Agent",
            "message": "Drafting transparent plain-language summary with source tracing...",
        }
        explain_out = await self.explainer.execute(state)
        state.update(explain_out)
        yield {
            "type": "agent_completed",
            "agent": "Legal Explanation Agent",
            "data": explain_out,
        }
        await asyncio.sleep(0.5)

        # Step 5: Legal Reviewer
        yield {
            "type": "agent_started",
            "agent": "Legal Reviewer Agent",
            "message": "Verifying anti-hallucination policies and applying statutory disclaimer...",
        }
        review_out = await self.reviewer.execute(state)
        state.update(review_out)
        yield {
            "type": "agent_completed",
            "agent": "Legal Reviewer Agent",
            "data": review_out,
        }

        # Finalize DB Record
        query_record.facts_identified = state.get("facts_identified", [])
        query_record.assumptions = state.get("assumptions", [])
        query_record.missing_info = state.get("missing_information", [])
        query_record.relevant_provisions = state.get("citations_retrieved", [])
        query_record.analysis = state.get("overall_explanation", "")
        query_record.possible_issues = state.get("mapped_legal_issues", [])
        query_record.risks_uncertainties = state.get("risks", [])
        query_record.explanation = state.get("overall_explanation", "")
        query_record.limitations = state.get("limitations", [])
        query_record.disclaimer = review_out.get("mandatory_disclaimer", "")
        query_record.status = "COMPLETED"
        query_record.completed_at = datetime.datetime.utcnow()
        self.db.commit()

        yield {
            "type": "workflow_completed",
            "query_id": query_id,
            "message": "Transparent Legal AI analysis successfully compiled and verified.",
            "final_data": {
                "question": question,
                "facts": state.get("facts_identified", []),
                "assumptions": state.get("assumptions", []),
                "sources": state.get("sources", []),
                "provisions": state.get("citations_retrieved", []),
                "analysis": state.get("overall_explanation", ""),
                "risks": state.get("risks", []),
                "uncertainties": state.get("uncertainties", []),
                "explanation": state.get("overall_explanation", ""),
                "limitations": state.get("limitations", []),
                "disclaimer": review_out.get("mandatory_disclaimer", ""),
            },
        }
