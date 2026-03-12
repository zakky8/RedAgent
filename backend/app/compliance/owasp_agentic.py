"""OWASP Top 10 for Agentic Applications 2026 compliance engine."""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Control:
    control_id: str
    name: str
    description: str
    articles: List[str]
    severity: str


@dataclass
class Gap:
    framework: str
    control_id: str
    control_name: str
    severity: str
    finding_count: int
    remediation_priority: int
    estimated_effort_days: int


class OWASPAgenticEngine:
    CONTROLS = {
        "A01": Control(
            control_id="A01",
            name="Unsafe Tool Execution",
            description="Agent executes tools without proper input validation or authorization checks",
            articles=["owasp_agentic/a01"],
            severity="CRITICAL",
        ),
        "A02": Control(
            control_id="A02",
            name="Goal Hijacking",
            description="Original agent objective can be overridden by user manipulation",
            articles=["owasp_agentic/a02"],
            severity="CRITICAL",
        ),
        "A03": Control(
            control_id="A03",
            name="Identity Confusion",
            description="Agent confused deputy problem — doesn't verify identities in delegated operations",
            articles=["owasp_agentic/a03"],
            severity="HIGH",
        ),
        "A04": Control(
            control_id="A04",
            name="Supply Chain Vulnerabilities",
            description="Insecure dependencies or compromised tool sources",
            articles=["owasp_agentic/a04"],
            severity="HIGH",
        ),
        "A05": Control(
            control_id="A05",
            name="Unexpected Code Execution",
            description="Dynamic code evaluation or unsafe deserialization in agent context",
            articles=["owasp_agentic/a05"],
            severity="CRITICAL",
        ),
        "A06": Control(
            control_id="A06",
            name="Memory/State Poisoning",
            description="Agent context or memory can be poisoned with malicious data",
            articles=["owasp_agentic/a06"],
            severity="HIGH",
        ),
        "A07": Control(
            control_id="A07",
            name="Inter-Agent Communication Abuse",
            description="Multi-agent systems vulnerable to message hijacking or spoofing",
            articles=["owasp_agentic/a07"],
            severity="MEDIUM",
        ),
        "A08": Control(
            control_id="A08",
            name="Cascading Failures",
            description="Agent failure in orchestrated systems causes chain reactions",
            articles=["owasp_agentic/a08"],
            severity="HIGH",
        ),
        "A09": Control(
            control_id="A09",
            name="Privilege Escalation",
            description="Agent gains elevated permissions beyond original scope",
            articles=["owasp_agentic/a09"],
            severity="HIGH",
        ),
        "A10": Control(
            control_id="A10",
            name="Audit Log Manipulation",
            description="Agent or attacker modifies or deletes audit logs of agent actions",
            articles=["owasp_agentic/a10"],
            severity="MEDIUM",
        ),
    }

    def __init__(self):
        self._findings: Dict[str, List[dict]] = {c: [] for c in self.CONTROLS.keys()}

    def map_scan_results_to_controls(self, scan_results: List[dict]) -> Dict[str, dict]:
        """Map scan results to OWASP Agentic controls."""
        assessments = {}
        for control_id, control in self.CONTROLS.items():
            # Filter findings matching this control
            matching = [
                r
                for r in scan_results
                if any(a in r.get("attack_id", "") for a in control.articles)
            ]
            assessments[control_id] = {
                "control_id": control_id,
                "name": control.name,
                "description": control.description,
                "severity": control.severity,
                "passing": len(matching) == 0,
                "finding_count": len(matching),
                "findings": matching,
            }
        return assessments

    def calculate_score(self, assessments: Dict[str, dict]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not assessments:
            return 0.0
        severity_weights = {"CRITICAL": 0.4, "HIGH": 0.3, "MEDIUM": 0.2, "LOW": 0.1}
        total_weight = sum(
            severity_weights.get(assessments[c].get("severity", "LOW"), 0.1)
            for c in assessments
        )
        passing_weight = sum(
            severity_weights.get(assessments[c].get("severity", "LOW"), 0.1)
            for c in assessments
            if assessments[c].get("passing", True)
        )
        if total_weight == 0:
            return 100.0
        return (passing_weight / total_weight) * 100.0

    def identify_gaps(self, assessments: Dict[str, dict]) -> List[Gap]:
        """Identify non-compliant controls."""
        gaps = []
        for control_id, assessment in assessments.items():
            if not assessment.get("passing", True):
                gaps.append(
                    Gap(
                        framework="owasp_agentic",
                        control_id=control_id,
                        control_name=assessment.get("name", control_id),
                        severity=assessment.get("severity", "MEDIUM"),
                        finding_count=assessment.get("finding_count", 0),
                        remediation_priority=self._priority(
                            assessment.get("severity", "MEDIUM")
                        ),
                        estimated_effort_days=self._effort(
                            assessment.get("severity", "MEDIUM")
                        ),
                    )
                )
        gaps.sort(key=lambda g: g.remediation_priority)
        return gaps

    def _priority(self, severity: str) -> int:
        return {
            "CRITICAL": 1,
            "HIGH": 2,
            "MEDIUM": 3,
            "LOW": 4,
            "INFO": 5,
        }.get(severity, 3)

    def _effort(self, severity: str) -> int:
        return {
            "CRITICAL": 1,
            "HIGH": 3,
            "MEDIUM": 5,
            "LOW": 10,
            "INFO": 30,
        }.get(severity, 5)
