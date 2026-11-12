"""Legal Risk Analysis Agent: Identifies legal exposure, uncertainties, and liability vectors."""
from typing import Dict, Any, List
from app.agents.base import BaseAgent


class LegalRiskAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="risk_analyzer",
            name="Legal Risk Analysis Agent",
            role="Regulatory Exposure & Risk Matrix Assessor",
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.start("Evaluating regulatory exposure, litigation risk, and legal uncertainties")

        facts = state.get("facts_identified", [])
        mapped_issues = state.get("mapped_legal_issues", [])
        question = state.get("question", "").lower()

        risks = []
        uncertainties = []

        if "non-compete" in question or "contract" in question or "employee" in question:
            risks.append({
                "risk_area": "Unenforceability of Restrictive Covenant",
                "severity": "HIGH",
                "probability": "HIGH",
                "description": "If signed mid-tenure without fresh consideration (e.g. bonus, raise), courts in numerous jurisdictions decline enforcement for lack of consideration.",
                "mitigation": "Review state-specific precedent; consider whether reasonable non-solicitation or confidentiality clauses survive as alternatives."
            })
            risks.append({
                "risk_area": "Regulatory Invalidation & FTC Scrutiny",
                "severity": "MEDIUM",
                "probability": "MEDIUM",
                "description": "Federal and state legal landscapes are rapidly shifting toward categorical bans or strict compensation thresholds on non-compete agreements.",
                "mitigation": "Audit all employment contracts for severability clauses."
            })
            uncertainties.append("Pending appellate litigation regarding federal agency rulemaking authority creates nationwide uncertainty.")
            uncertainties.append("Choice-of-law provisions may invoke laws of a state hostile to non-competes (e.g., California Business and Professions Code § 16600).")

        elif "ai" in question or "copyright" in question:
            risks.append({
                "risk_area": "Inability to Secure Copyright Protection",
                "severity": "HIGH",
                "probability": "HIGH",
                "description": "Outputs produced solely by generative AI algorithms are ineligible for statutory copyright registration due to absence of human authorship.",
                "mitigation": "Maintain contemporaneous documentation demonstrating substantial human selection, arrangement, and creative modification."
            })
            risks.append({
                "risk_area": "Third-Party Training Data Infringement",
                "severity": "MEDIUM",
                "probability": "MEDIUM",
                "description": "Downstream risks regarding whether AI training inputs or synthesized outputs infringe preexisting protected works.",
                "mitigation": "Utilize enterprise AI models backed by vendor copyright indemnification clauses."
            })
            uncertainties.append("The boundary between 'assisted creation' and 'unprotectable machine generation' is actively evolving in district courts.")

        else:
            risks.append({
                "risk_area": "Breach of Statutory Duty or Contract",
                "severity": "MEDIUM",
                "probability": "MEDIUM",
                "description": "Failure to satisfy contractual representations or regulatory consumer protection obligations.",
                "mitigation": "Audit disclosures, communications, and terms of service."
            })
            uncertainties.append("Resolution hinges heavily upon extrinsic parol evidence and jurisdictional precedent.")

        output = {
            "risks": risks,
            "uncertainties": uncertainties,
            "overall_risk_level": "MODERATE TO ELEVATED",
            "summary": f"Identified {len(risks)} primary exposure vectors and {len(uncertainties)} regulatory uncertainties.",
        }

        self.complete()
        return output
