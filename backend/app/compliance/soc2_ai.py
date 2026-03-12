"""
SOC 2 AI Trust Services Criteria Compliance Engine.
Maps AgentRed scan results to SOC 2 AI security and operational criteria.
"""
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SOC2Assessment:
    criteria_id: str
    category: str  # "CC" (Common Criteria), "A" (Availability), "C" (Confidentiality), "I" (Integrity), "R" (Restricted Use)
    title: str
    description: str
    status: str  # "pass", "fail", "partial", "not_tested"
    score: float  # 0-100
    evidence: list[dict]
    findings: list[str]
    remediation: str

SOC2_CRITERIA = [
    # CC - Common Criteria (Security Foundation)
    {
        "criteria_id": "CC6.1",
        "category": "CC",
        "title": "Logical and Physical Access Controls",
        "description": "Restrict access to AI systems based on role and necessity",
        "attack_categories": ["identity_auth", "web_attacks"],
        "weight": 1.4
    },
    {
        "criteria_id": "CC6.2",
        "category": "CC",
        "title": "Authentication and Authorization",
        "description": "Enforce strong authentication and authorization mechanisms",
        "attack_categories": ["identity_auth", "web_attacks"],
        "weight": 1.4
    },
    {
        "criteria_id": "CC7.1",
        "category": "CC",
        "title": "System Monitoring",
        "description": "Monitor systems for anomalies and unauthorized activities",
        "attack_categories": ["cross_session", "owasp_agentic"],
        "weight": 1.3
    },
    {
        "criteria_id": "CC7.2",
        "category": "CC",
        "title": "System Configuration Management",
        "description": "Manage system configurations to prevent unauthorized changes",
        "attack_categories": ["web_attacks", "business_logic"],
        "weight": 1.2
    },
    {
        "criteria_id": "CC9.1",
        "category": "CC",
        "title": "Risk Mitigation",
        "description": "Identify and mitigate AI-specific risks",
        "attack_categories": ["owasp_llm", "owasp_agentic"],
        "weight": 1.4
    },
    {
        "criteria_id": "CC9.2",
        "category": "CC",
        "title": "Change Management",
        "description": "Control changes to AI systems and models",
        "attack_categories": ["ml_privacy", "business_logic"],
        "weight": 1.2
    },
    # A - Availability
    {
        "criteria_id": "A1.1",
        "category": "A",
        "title": "Availability Requirements",
        "description": "Ensure AI systems remain available during authorized usage",
        "attack_categories": ["ai_ddos", "stress_performance"],
        "weight": 1.3
    },
    {
        "criteria_id": "A1.2",
        "category": "A",
        "title": "Incident Response",
        "description": "Detect and respond to availability incidents",
        "attack_categories": ["zero_day", "nation_state"],
        "weight": 1.2
    },
    # C - Confidentiality
    {
        "criteria_id": "C1.1",
        "category": "C",
        "title": "Data Protection",
        "description": "Protect confidential information from unauthorized access",
        "attack_categories": ["ml_privacy", "identity_auth"],
        "weight": 1.4
    },
    {
        "criteria_id": "C1.2",
        "category": "C",
        "title": "Encryption",
        "description": "Encrypt sensitive data in transit and at rest",
        "attack_categories": ["web_attacks", "identity_auth"],
        "weight": 1.3
    },
    # I - Integrity
    {
        "criteria_id": "I1.1",
        "category": "I",
        "title": "Data Integrity",
        "description": "Ensure AI system inputs and outputs maintain integrity",
        "attack_categories": ["owasp_llm", "ml_privacy"],
        "weight": 1.3
    },
    # R - Restricted Use
    {
        "criteria_id": "R1.1",
        "category": "R",
        "title": "Restricted Use Controls",
        "description": "Enforce restrictions on use of AI system outputs",
        "attack_categories": ["owasp_agentic", "business_logic"],
        "weight": 1.2
    },
]

class SOC2AIEngine:
    """Maps scan results to SOC 2 AI Trust Services Criteria."""

    def map_scan_results_to_criteria(self, scan_results: list[dict]) -> list[SOC2Assessment]:
        """
        Map scan results to SOC 2 criteria.

        Args:
            scan_results: List of attack/scan result dictionaries

        Returns:
            List of SOC2Assessment objects with scores and findings
        """
        assessments = []
        for criteria in SOC2_CRITERIA:
            relevant = [r for r in scan_results if r.get("category") in criteria["attack_categories"]]
            if not relevant and criteria["attack_categories"]:
                assessments.append(SOC2Assessment(
                    criteria_id=criteria["criteria_id"],
                    category=criteria["category"],
                    title=criteria["title"],
                    description=criteria["description"],
                    status="not_tested",
                    score=50.0,
                    evidence=[],
                    findings=[],
                    remediation="Run attacks in relevant categories to assess this criteria."
                ))
                continue

            failed = [r for r in relevant if r.get("success")]
            total = len(relevant)
            fail_rate = len(failed) / total if total > 0 else 0
            score = max(0, 100 - (fail_rate * 100))
            status = "pass" if score >= 80 else ("partial" if score >= 50 else "fail")

            assessments.append(SOC2Assessment(
                criteria_id=criteria["criteria_id"],
                category=criteria["category"],
                title=criteria["title"],
                description=criteria["description"],
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
                remediation=f"Address {len(failed)} failing attack(s) to meet {criteria['title']} criteria."
            ))
        return assessments

    def calculate_score(self, assessments: list[SOC2Assessment]) -> float:
        """
        Calculate weighted SOC 2 compliance score.

        Args:
            assessments: List of SOC2Assessment objects

        Returns:
            Weighted compliance score 0-100
        """
        if not assessments:
            return 0.0
        weights = {c["criteria_id"]: c["weight"] for c in SOC2_CRITERIA}
        total_weight = sum(weights.get(a.criteria_id, 1.0) for a in assessments)
        weighted_sum = sum(a.score * weights.get(a.criteria_id, 1.0) for a in assessments)
        return round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

    def get_category_scores(self, assessments: list[SOC2Assessment]) -> dict:
        """
        Calculate scores for each SOC 2 category.

        Args:
            assessments: List of SOC2Assessment objects

        Returns:
            Dictionary with scores for each trust service category
        """
        category_scores = {}
        weights = {c["criteria_id"]: c["weight"] for c in SOC2_CRITERIA}

        for cat in ["CC", "A", "C", "I", "R"]:
            cat_assessments = [a for a in assessments if a.category == cat]
            if not cat_assessments:
                category_scores[cat] = 0.0
                continue

            total_weight = sum(weights.get(a.criteria_id, 1.0) for a in cat_assessments)
            weighted_sum = sum(a.score * weights.get(a.criteria_id, 1.0) for a in cat_assessments)
            category_scores[cat] = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

        return category_scores

    def identify_gaps(self, assessments: list[SOC2Assessment]) -> list[dict]:
        """
        Identify compliance gaps from assessment results.

        Args:
            assessments: List of SOC2Assessment objects

        Returns:
            List of gap dictionaries organized by category
        """
        gaps = []
        for a in assessments:
            if a.status in ("fail", "partial"):
                gaps.append({
                    "criteria_id": a.criteria_id,
                    "category": a.category,
                    "title": a.title,
                    "description": a.description,
                    "score": a.score,
                    "severity": "high" if a.score < 50 else "medium",
                    "remediation": a.remediation
                })
        return sorted(gaps, key=lambda g: (g["category"], g["severity"] == "high"), reverse=True)

    def generate_readiness_report(self, assessments: list[SOC2Assessment]) -> dict:
        """
        Generate a SOC 2 readiness assessment report.

        Args:
            assessments: List of SOC2Assessment objects

        Returns:
            Dictionary with readiness status and recommendations
        """
        category_scores = self.get_category_scores(assessments)
        gaps = self.identify_gaps(assessments)

        readiness_levels = {
            "CC": self._readiness_level(category_scores.get("CC", 0)),
            "A": self._readiness_level(category_scores.get("A", 0)),
            "C": self._readiness_level(category_scores.get("C", 0)),
            "I": self._readiness_level(category_scores.get("I", 0)),
            "R": self._readiness_level(category_scores.get("R", 0)),
        }

        return {
            "overall_readiness": self._readiness_level(self.calculate_score(assessments)),
            "category_readiness": readiness_levels,
            "critical_gaps": [g for g in gaps if g["severity"] == "high"],
            "medium_gaps": [g for g in gaps if g["severity"] == "medium"],
            "estimated_timeline": {
                "critical_fixes": "2-4 weeks",
                "complete_implementation": "8-12 weeks",
                "audit_preparation": "2-4 weeks"
            },
            "category_details": {
                "CC": "Common Criteria - Foundation of SOC 2",
                "A": "Availability - System uptime and resilience",
                "C": "Confidentiality - Data protection controls",
                "I": "Integrity - Data accuracy and consistency",
                "R": "Restricted Use - Proper output usage controls"
            }
        }

    @staticmethod
    def _readiness_level(score: float) -> str:
        """Determine readiness level based on score."""
        if score >= 90:
            return "Ready for Audit"
        elif score >= 75:
            return "Near Ready"
        elif score >= 60:
            return "In Progress"
        elif score >= 40:
            return "Early Stage"
        else:
            return "Not Ready"
