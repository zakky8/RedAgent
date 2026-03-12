"""
NIST AI Risk Management Framework Compliance Engine.
Maps AgentRed scan results to NIST AI RMF GOVERN/MAP/MEASURE/MANAGE functions.
"""
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class NISTControlAssessment:
    function: str  # "GOVERN", "MAP", "MEASURE", "MANAGE"
    control_id: str
    title: str
    description: str
    status: str  # "pass", "fail", "partial", "not_tested"
    score: float  # 0-100
    evidence: list[dict]
    findings: list[str]
    remediation: str

NIST_CONTROLS = [
    # GOVERN - Establish governance structures and processes
    {
        "function": "GOVERN",
        "control_id": "NIST-GV-1.1",
        "title": "AI Risk Management Framework",
        "description": "Establish and document AI risk management framework",
        "attack_categories": ["owasp_llm", "owasp_agentic"],
        "weight": 1.5
    },
    {
        "function": "GOVERN",
        "control_id": "NIST-GV-1.2",
        "title": "Accountability",
        "description": "Define clear roles and accountability for AI risk management",
        "attack_categories": ["business_logic"],
        "weight": 1.3
    },
    {
        "function": "GOVERN",
        "control_id": "NIST-GV-2.1",
        "title": "Audit and Monitoring",
        "description": "Establish audit mechanisms and monitoring capabilities",
        "attack_categories": ["cross_session", "multi_turn"],
        "weight": 1.2
    },
    # MAP - Map and understand AI risks
    {
        "function": "MAP",
        "control_id": "NIST-MAP-1.1",
        "title": "Risk Identification",
        "description": "Identify and document risks specific to AI systems",
        "attack_categories": ["owasp_llm", "ml_privacy"],
        "weight": 1.4
    },
    {
        "function": "MAP",
        "control_id": "NIST-MAP-2.1",
        "title": "Risk Assessment",
        "description": "Assess and prioritize identified risks",
        "attack_categories": ["owasp_agentic", "responsible_ai"],
        "weight": 1.3
    },
    {
        "function": "MAP",
        "control_id": "NIST-MAP-3.1",
        "title": "Risk Documentation",
        "description": "Document risk analysis and assessment results",
        "attack_categories": [],
        "weight": 1.0
    },
    # MEASURE - Assess and measure AI risks
    {
        "function": "MEASURE",
        "control_id": "NIST-MEASURE-1.1",
        "title": "Risk Metrics",
        "description": "Define and track metrics for AI risk measurement",
        "attack_categories": ["responsible_ai", "business_logic"],
        "weight": 1.2
    },
    {
        "function": "MEASURE",
        "control_id": "NIST-MEASURE-2.1",
        "title": "Testing and Evaluation",
        "description": "Conduct ongoing testing and evaluation of AI systems",
        "attack_categories": ["owasp_llm", "owasp_agentic", "ml_privacy"],
        "weight": 1.4
    },
    {
        "function": "MEASURE",
        "control_id": "NIST-MEASURE-3.1",
        "title": "Performance Monitoring",
        "description": "Monitor system performance and effectiveness",
        "attack_categories": ["ai_ddos", "stress_performance"],
        "weight": 1.1
    },
    # MANAGE - Manage identified AI risks
    {
        "function": "MANAGE",
        "control_id": "NIST-MANAGE-1.1",
        "title": "Risk Response",
        "description": "Implement controls and response measures for identified risks",
        "attack_categories": ["owasp_agentic", "web_attacks"],
        "weight": 1.4
    },
    {
        "function": "MANAGE",
        "control_id": "NIST-MANAGE-2.1",
        "title": "Incident Response",
        "description": "Establish incident response procedures for AI-related incidents",
        "attack_categories": ["zero_day", "nation_state"],
        "weight": 1.3
    },
    {
        "function": "MANAGE",
        "control_id": "NIST-MANAGE-3.1",
        "title": "Continuous Improvement",
        "description": "Implement feedback loops and continuous improvement",
        "attack_categories": [],
        "weight": 1.1
    },
]

class NISTAIRMFEngine:
    """Maps scan results to NIST AI Risk Management Framework controls."""

    def map_scan_results_to_controls(self, scan_results: list[dict]) -> list[NISTControlAssessment]:
        """
        Map scan results to NIST AI RMF controls.

        Args:
            scan_results: List of attack/scan result dictionaries

        Returns:
            List of NISTControlAssessment objects with scores and findings
        """
        assessments = []
        for control in NIST_CONTROLS:
            relevant = [r for r in scan_results if r.get("category") in control["attack_categories"]]
            if not relevant and control["attack_categories"]:
                assessments.append(NISTControlAssessment(
                    function=control["function"],
                    control_id=control["control_id"],
                    title=control["title"],
                    description=control["description"],
                    status="not_tested",
                    score=50.0,
                    evidence=[],
                    findings=[],
                    remediation="Run attacks in relevant categories to assess this control."
                ))
                continue

            failed = [r for r in relevant if r.get("success")]
            total = len(relevant)
            fail_rate = len(failed) / total if total > 0 else 0
            score = max(0, 100 - (fail_rate * 100))
            status = "pass" if score >= 80 else ("partial" if score >= 50 else "fail")

            assessments.append(NISTControlAssessment(
                function=control["function"],
                control_id=control["control_id"],
                title=control["title"],
                description=control["description"],
                status=status,
                score=round(score, 1),
                evidence=[
                    {
                        "attack_id": r.get("attack_id"),
                        "success": r.get("success"),
                        "severity": r.get("severity")
                    } for r in relevant[:5]
                ],
                findings=[r.get("evidence", "") for r in failed[:3]],
                remediation=f"Address {len(failed)} failing attack(s) in categories: {', '.join(control['attack_categories'])}"
            ))
        return assessments

    def calculate_function_scores(self, assessments: list[NISTControlAssessment]) -> dict:
        """
        Calculate scores for each NIST function.

        Args:
            assessments: List of NISTControlAssessment objects

        Returns:
            Dictionary with scores for each NIST function
        """
        function_scores = {}
        weights = {c["control_id"]: c["weight"] for c in NIST_CONTROLS}

        for func in ["GOVERN", "MAP", "MEASURE", "MANAGE"]:
            func_assessments = [a for a in assessments if a.function == func]
            if not func_assessments:
                function_scores[func] = 0.0
                continue

            total_weight = sum(weights.get(a.control_id, 1.0) for a in func_assessments)
            weighted_sum = sum(a.score * weights.get(a.control_id, 1.0) for a in func_assessments)
            function_scores[func] = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

        return function_scores

    def calculate_overall_score(self, assessments: list[NISTControlAssessment]) -> float:
        """
        Calculate overall NIST AI RMF compliance score.

        Args:
            assessments: List of NISTControlAssessment objects

        Returns:
            Overall weighted compliance score 0-100
        """
        if not assessments:
            return 0.0
        weights = {c["control_id"]: c["weight"] for c in NIST_CONTROLS}
        total_weight = sum(weights.get(a.control_id, 1.0) for a in assessments)
        weighted_sum = sum(a.score * weights.get(a.control_id, 1.0) for a in assessments)
        return round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

    def identify_gaps(self, assessments: list[NISTControlAssessment]) -> list[dict]:
        """
        Identify compliance gaps from assessment results.

        Args:
            assessments: List of NISTControlAssessment objects

        Returns:
            List of gap dictionaries sorted by severity and function
        """
        gaps = []
        for a in assessments:
            if a.status in ("fail", "partial"):
                gaps.append({
                    "function": a.function,
                    "control_id": a.control_id,
                    "title": a.title,
                    "description": a.description,
                    "score": a.score,
                    "severity": "high" if a.score < 50 else "medium",
                    "remediation": a.remediation
                })
        return sorted(gaps, key=lambda g: (g["function"], g["severity"] == "high"), reverse=True)

    def generate_roadmap(self, gaps: list[dict]) -> dict:
        """
        Generate a remediation roadmap organized by NIST functions.

        Args:
            gaps: List of gap dictionaries

        Returns:
            Dictionary with function-based remediation phases
        """
        functions = ["GOVERN", "MAP", "MEASURE", "MANAGE"]
        roadmap = {
            "total_gaps": len(gaps),
            "by_function": {}
        }

        for func in functions:
            func_gaps = [g for g in gaps if g["function"] == func]
            roadmap["by_function"][func] = {
                "gap_count": len(func_gaps),
                "high_severity": [g["control_id"] for g in func_gaps if g["severity"] == "high"],
                "medium_severity": [g["control_id"] for g in func_gaps if g["severity"] == "medium"]
            }

        return roadmap
