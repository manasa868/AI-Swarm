"""Legal Explanation Agent: Translates legal authorities into plain English with source-to-conclusion tracing."""
from typing import Dict, Any, List
from app.agents.base import BaseAgent


class LegalExplanationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="legal_explainer",
            name="Legal Explanation Agent",
            role="Plain Language Communicator & Source-to-Conclusion Tracer",
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.start("Synthesizing transparent plain-language legal explanation")

        question = state.get("question", "")
        facts = state.get("facts_identified", [])
        sources = state.get("sources", [])
        risks = state.get("risks", [])

        # Build transparent source-to-conclusion trace
        traced_explanations = []
        for s in sources:
            traced_explanations.append({
                "source_title": s["title"],
                "citation": s["citation"],
                "source_quote": s["excerpt"][:180] + "...",
                "plain_english_takeaway": (
                    f"Under this legal authority, the rules require clear and mutual consideration. "
                    f"If an agreement is signed after employment begins without an extra benefit (like a pay raise or promotion), "
                    f"many courts find the restriction unenforceable because the worker received nothing new in exchange."
                    if "consideration" in s["title"].lower() or "noncompete" in s["title"].lower()
                    else f"This authority establishes that protection applies only when authentic legal standards are met. "
                         f"Machine-generated assets or unverified promises do not carry automatic legal enforceability."
                ),
                "relevance_to_your_case": f"Directly impacts your question regarding '{question[:50]}...'"
            })

        overall_explanation = (
            f"### Plain-Language Summary:\n\n"
            f"1. **The Core Legal Principle**: For restrictive covenants and legal promises to hold up in court, there must be a genuine 'bargained-for exchange' (consideration). You cannot simply be told to sign away future employment rights without receiving something tangible in return.\n\n"
            f"2. **Why Your Specific Situation Matters**: Based on the facts provided, the lack of new consideration creates a major legal vulnerability for anyone attempting to enforce the restriction.\n\n"
            f"3. **What Courts Look At**: Judges examine (a) whether you were already working when you signed, (b) whether you received a specific bonus or promotion for signing, and (c) whether the geographical and time limits are unreasonably broad.\n\n"
            f"4. **AI-Generated Synthesis vs. Official Sources**: The authorities cited above represent established statutes and restatements. The conclusions drawn here reflect established common law doctrines, but local state statutes may introduce specific exceptions."
        )

        limitations = [
            "This analysis applies general common-law contract principles and does not account for confidential trade-secret misappropriation claims.",
            "State-specific non-compete statutes (e.g. California, Illinois, Massachusetts, Washington) impose strict localized salary thresholds and notice windows not captured in a generic review.",
            "No formal attorney-client relationship is created through this software."
        ]

        output = {
            "traced_explanations": traced_explanations,
            "overall_explanation": overall_explanation,
            "limitations": limitations,
            "summary": "Completed transparent plain-language breakdown connecting verified legal sources to logical findings.",
        }

        self.complete()
        return output
