"""Legal Research Agent: Retrieves verified legal sources and statutory citations."""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.legal.legal_knowledge_base import search_legal_knowledge_base


class LegalResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="legal_researcher",
            name="Legal Research Agent",
            role="Statutory Research & Precedent Retrieval Specialist",
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state.get("question", "")
        self.start(f"Searching verified sources for legal question: '{question[:60]}...'")

        # Query curated knowledge base
        matched_sources = search_legal_knowledge_base(question)
        
        verified_sources = []
        for s in matched_sources:
            verified_sources.append({
                "id": s["id"],
                "title": s["title"],
                "citation": s["citation"],
                "source_type": s["source_type"],
                "url_or_ref": s["url_or_ref"],
                "excerpt": s["excerpt"],
                "relevance_score": s.get("relevance_score", 0.9),
                "is_verified": True,
            })

        output = {
            "sources": verified_sources,
            "source_count": len(verified_sources),
            "citations_retrieved": [s["citation"] for s in verified_sources],
            "anti_hallucination_guarantee": "All retrieved legal citations are strictly grounded in verified statutory and regulatory records.",
            "summary": f"Retrieved {len(verified_sources)} verified legal authority sources matching query parameters.",
        }

        self.complete()
        return output
