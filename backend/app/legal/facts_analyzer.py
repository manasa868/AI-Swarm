"""Case / Facts Analysis Agent: Dissects user scenario into facts, assumptions, and legal issues."""
from typing import Dict, Any, List
from app.agents.base import BaseAgent


class FactsAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="facts_analyzer",
            name="Case/Facts Analysis Agent",
            role="Factual Decomposition & Issue Framing Specialist",
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state.get("question", "")
        self.start("Extracting explicit facts, isolating assumptions, and flagging information gaps")

        # Analytical extraction based on textual patterns
        facts = []
        assumptions = []
        missing_info = []
        mapped_issues = []

        q_lower = question.lower()

        # Employment / Non-compete context
        if "non-compete" in q_lower or "contract" in q_lower or "employee" in q_lower:
            facts.append("The subject is party to an employment agreement containing a restrictive covenant or non-compete clause.")
            if "without" in q_lower or "no money" in q_lower or "consideration" in q_lower:
                facts.append("No separate independent monetary consideration or promotion was provided at the time of signing.")
            else:
                assumptions.append("Presumed that the covenant was executed either at inception of employment or during tenure without distinct consideration.")
            
            missing_info.append("Specific jurisdiction/state governing law clause in the agreement.")
            missing_info.append("Exact geographic radius and temporal duration (e.g. 6 months vs 2 years) of the restriction.")
            missing_info.append("Employee's role level (e.g., senior executive with trade secrets vs general staff).")

            mapped_issues.append("Adequacy of consideration under general contract law principles.")
            mapped_issues.append("Reasonableness of covenant scope and legitimate protectable employer interests.")
            mapped_issues.append("Enforceability under recent federal and state regulatory non-compete shifts.")

        # IP / AI copyright context
        elif "ai" in q_lower or "copyright" in q_lower or "code" in q_lower or "intellectual property" in q_lower:
            facts.append("User is evaluating intellectual property ownership and copyrightability for software or content generated using AI tools.")
            assumptions.append("Assumed that the AI model utilized is a commercial or open-weight generative foundation model.")
            missing_info.append("Degree and nature of human creative input, prompt curation, and post-editing.")
            missing_info.append("Terms of Service of the specific generative AI tool (e.g., commercial rights assignment).")
            
            mapped_issues.append("Human authorship prerequisite under U.S. Copyright Office Compendium § 313.2.")
            mapped_issues.append("Contractual assignment of generative outputs under SaaS terms of service.")

        # Consumer / Refund dispute context
        elif "refund" in q_lower or "merchant" in q_lower or "purchase" in q_lower or "consumer" in q_lower:
            facts.append("Consumer transaction involving delayed shipment, defective goods, or refund refusal.")
            assumptions.append("Assumed purchase occurred through an online e-commerce platform.")
            missing_info.append("Original merchant disclosure of delivery timeframes and written return policy at point of sale.")
            missing_info.append("Payment processor or credit card chargeback window.")

            mapped_issues.append("Compliance with FTC 30-day mail and internet order merchandise rules.")
            mapped_issues.append("Express warranty and consumer dispute rights.")

        else:
            facts.append(f"Inquiry submitted: '{question}'")
            assumptions.append("Standard common-law jurisdiction applicable unless otherwise specified.")
            missing_info.append("Jurisdictional nexus, signed contractual instruments, and monetary damages threshold.")
            mapped_issues.append("General statutory compliance and contractual liability.")

        output = {
            "facts_identified": facts,
            "assumptions": assumptions,
            "missing_information": missing_info,
            "mapped_legal_issues": mapped_issues,
            "summary": f"Identified {len(facts)} factual claims, isolated {len(assumptions)} unverified assumptions, and mapped {len(mapped_issues)} core legal issues.",
        }

        self.complete()
        return output
