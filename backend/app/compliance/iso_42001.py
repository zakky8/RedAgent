"""
ISO 42001 AI Management System Compliance Engine.
Maps AgentRed scan results to ISO 42001 clauses and requirements.
"""
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ISO42001Assessment:
    clause: str
    clause_id: str
    title: str
    requirements: list[str]
    status: str  # "pass", "fail", "partial", "not_tested"
    score: float  # 0-100
    evidence: list[dict]
    findings: list[str]
    remediation: str

ISO_42001_CLAUSES = [
    {
        "clause": "4",
        "clause_id": "ISO-4.0",
        "title": "Context of the Organization",
        "requirements": [
            "Understand organizational context",
            "Identify interested parties",
            "Define scope of AI management system"
        ],
        "attack_categories": [],
        "weight": 0.9
    },
    {
        "clause": "5",
        "clause_id": "ISO-5.0",
        "title": "Leadership",
        "requirements": [
            "Demonstrate AI management commitment",
            "Establish AI policy",
            "Assign roles and responsibilities"
        ],
        "attack_categories": ["business_logic"],
        "weight": 1.1
    },
    {
        "clause": "6",
        "clause_id": "ISO-6.0",
        "title": "Planning",
        "requirements": [
            "Assess AI risks",
            "Plan AI risk responses",
            "Plan resource allocation"
        ],
        "attack_categories": ["owasp_llm", "ml_privacy"],
        "weight": 1.3
    },
    {
        "clause": "6.1",
        "clause_id": "ISO-6.1",
        "title": "Risk Assessment",
        "requirements": [
            "Identify AI-related risks",
            "Analyze risk impacts",
            "Determine risk acceptance criteria"
        ],
        "attack_categories": ["owasp_llm", "owasp_agentic"],
        "weight": 1.4
    },
    {
        "clause": "7",
        "clause_id": "ISO-7.0",
        "title": "Support",
        "requirements": [
            "Provide competent resources",
            "Maintain documentation",
            "Ensure communication"
        ],
        "attack_categories": [],
        "weight": 1.0
    },
    {
        "clause": "8",
        "clause_id": "ISO-8.0",
        "title": "Operation",
        "requirements": [
            "Implement AI risk controls",
            "Manage AI system changes",
            "Monitor AI performance"
        ],
        "attack_categories": ["web_attacks", "identity_auth", "ai_ddos"],
        "weight": 1.4
    },
    {
        "clause": "8.1",
        "clause_id": "ISO-8.1",
        "title": "Operational Planning and Control",
        "requirements": [
            "Plan operational processes",
            "Control AI system changes",
            "Implement process controls"
        ],
        "attack_categories": ["owasp_agentic", "business_logic"],
        "weight": 1.3
    },
    {
        "clause": "8.2",
        "clause_id": "ISO-8.2",
        "title": "Information Management",
        "requirements": [
            "Manage training data",
            "Control data quality",
            "Ensure data security"
        ],
        "attack_categories": ["ml_privacy", "identity_auth"],
        "weight": 1.3
    },
    {
        "clause": "9",
        "clause_id": "ISO-9.0",
        "title": "Performance Evaluation",
        "requirements": [
            "Monitor AI system performance",
            "Conduct internal audits",
            "Measure effectiveness"
        ],
        "attack_categories": ["responsible_ai", "stress_performance"],
        "weight": 1.2
    },
    {
        "clause": "10",
        "clause_id": "ISO-10.0",
        "title": "Improvement",
        "requirements": [
            "Identify improvement opportunities",
            "Manage nonconformities",
            "Implement corrective actions"
        ],
        "attack_categories": [],
        "weight": 1.1
    },
]

class ISO42001Engine:
    """Maps scan results to ISO 42001 AI Management System clauses."""

    def map_scan_results_to_clauses(self, scan_results: list[dict]) -> list[ISO42001Assessment]:
        """
        Map scan results to ISO 42001 clauses.

        Args:
            scan_results: List of attack/scan result dictionaries

        Returns:
            List of ISO42001Assessment objects with scores and findings
        """
        assessments = []
        for clause in ISO_42001_CLAUSES:
            relevant = [r for r in scan_results if r.get("category") in clause["attack_categories"]]
            if not relevant and clause["attack_categories"]:
                assessments.append(ISO42001Assessment(
                    clause=clause["clause"],
                    clause_id=clause["clause_id"],
                    title=clause["title"],
                    requirements=clause["requirements"],
                    status="not_tested",
                    score=50.0,
                    evidence=[],
                    findings=[],
                    remediation="Run attacks in relevant categories to assess this clause."
                ))
                continue

            failed = [r for r in relevant if r.get("success")]
            total = len(relevant)
            fail_rate = len(failed) / total if total > 0 else 0
            score = max(0, 100 - (fail_rate * 100))
            status = "pass" if score >= 80 else ("partial" if score >= 50 else "fail")

            assessments.append(ISO42001Assessment(
                clause=clause["clause"],
                clause_id=clause["clause_id"],
                title=clause["title"],
                requirements=clause["requirements"],
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
                remediation=f"Implement controls to address {len(failed)} failing attack(s) against Clause {clause['clause']}."
            ))
        return assessments

    def calculate_score(self, assessments: list[ISO42001Assessment]) -> float:
        """
        Calculate weighted ISO 42001 compliance score.

        Args:
            assessments: List of ISO42001Assessment objects

        Returns:
            Weighted compliance score 0-100
        """
        if not assessments:
            return 0.0
        weights = {c["clause_id"]: c["weight"] for c in ISO_42001_CLAUSES}
        total_weight = sum(weights.get(a.clause_id, 1.0) for a in assessments)
        weighted_sum = sum(a.score * weights.get(a.clause_id, 1.0) for a in assessments)
        return round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

    def get_clause_by_category(self, assessments: list[ISO42001Assessment]) -> dict:
        """
        Organize assessments by ISO 42001 clause category.

        Args:
            assessments: List of ISO42001Assessment objects

        Returns:
            Dictionary with assessments organized by clause
        """
        organized = {
            "context": [a for a in assessments if a.clause == "4"],
            "leadership": [a for a in assessments if a.clause == "5"],
            "planning": [a for a in assessments if a.clause.startswith("6")],
            "support": [a for a in assessments if a.clause == "7"],
            "operation": [a for a in assessments if a.clause.startswith("8")],
            "evaluation": [a for a in assessments if a.clause == "9"],
            "improvement": [a for a in assessments if a.clause == "10"],
        }
        return organized

    def identify_gaps(self, assessments: list[ISO42001Assessment]) -> list[dict]:
        """
        Identify compliance gaps from assessment results.

        Args:
            assessments: List of ISO42001Assessment objects

        Returns:
            List of gap dictionaries sorted by clause and severity
        """
        gaps = []
        for a in assessments:
            if a.status in ("fail", "partial"):
                gaps.append({
                    "clause": a.clause,
                    "clause_id": a.clause_id,
                    "title": a.title,
                    "score": a.score,
                    "severity": "high" if a.score < 50 else "medium",
                    "requirements": a.requirements,
                    "remediation": a.remediation
                })
        return sorted(gaps, key=lambda g: (g["clause"], g["severity"] == "high"), reverse=True)

    def generate_implementation_plan(self, gaps: list[dict]) -> dict:
        """
        Generate an implementation plan for ISO 42001 compliance.

        Args:
            gaps: List of gap dictionaries

        Returns:
            Dictionary with implementation phases and activities
        """
        clauses_by_category = {}
        for gap in gaps:
            clause = gap["clause"]
            if clause not in clauses_by_category:
                clauses_by_category[clause] = []
            clauses_by_category[clause].append(gap)

        return {
            "total_gaps": len(gaps),
            "critical_clauses": [
                {
                    "clause": c,
                    "title": clauses_by_category[c][0]["title"] if clauses_by_category[c] else "",
                    "gap_count": len(clauses_by_category[c]),
                    "recommendations": [g["remediation"] for g in clauses_by_category[c][:2]]
                } for c in sorted(clauses_by_category.keys()) if clauses_by_category[c]
            ],
            "implementation_phases": [
                {
                    "phase": 1,
                    "title": "Foundational Controls (Clauses 4-5)",
                    "duration": "4 weeks",
                    "activities": ["Define AI management system scope", "Establish leadership commitment"]
                },
                {
                    "phase": 2,
                    "title": "Risk Management (Clause 6)",
                    "duration": "4 weeks",
                    "activities": ["Conduct risk assessments", "Document risk responses"]
                },
                {
                    "phase": 3,
                    "title": "Operational Controls (Clause 8)",
                    "duration": "6 weeks",
                    "activities": ["Implement operational controls", "Manage data quality", "Control system changes"]
                },
                {
                    "phase": 4,
                    "title": "Monitoring and Improvement (Clauses 9-10)",
                    "duration": "Ongoing",
                    "activities": ["Monitor performance", "Conduct audits", "Implement improvements"]
                }
            ]
        }
