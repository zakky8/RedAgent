"""MITRE ATLAS compliance mapping."""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ATLASControl:
    tactic_id: str
    tactic_name: str
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


class MITREATLASEngine:
    TACTICS = {
        "TA01": ATLASControl(
            tactic_id="TA01",
            tactic_name="Reconnaissance",
            description="Gathering information about target ML systems and data",
            articles=["mitre_atlas/ta01"],
            severity="MEDIUM",
        ),
        "TA02": ATLASControl(
            tactic_id="TA02",
            tactic_name="Resource Development",
            description="Acquiring resources for attacking ML systems",
            articles=["mitre_atlas/ta02"],
            severity="MEDIUM",
        ),
        "TA03": ATLASControl(
            tactic_id="TA03",
            tactic_name="Initial Access",
            description="Gaining access to ML system or its training data",
            articles=["mitre_atlas/ta03"],
            severity="HIGH",
        ),
        "TA04": ATLASControl(
            tactic_id="TA04",
            tactic_name="Execution",
            description="Running code or commands in ML system context",
            articles=["mitre_atlas/ta04"],
            severity="CRITICAL",
        ),
        "TA05": ATLASControl(
            tactic_id="TA05",
            tactic_name="Persistence",
            description="Maintaining long-term access to ML system",
            articles=["mitre_atlas/ta05"],
            severity="HIGH",
        ),
        "TA06": ATLASControl(
            tactic_id="TA06",
            tactic_name="Privilege Escalation",
            description="Gaining elevated permissions in ML system",
            articles=["mitre_atlas/ta06"],
            severity="HIGH",
        ),
        "TA07": ATLASControl(
            tactic_id="TA07",
            tactic_name="Defense Evasion",
            description="Avoiding detection while attacking ML system",
            articles=["mitre_atlas/ta07"],
            severity="MEDIUM",
        ),
        "TA08": ATLASControl(
            tactic_id="TA08",
            tactic_name="Credential Access",
            description="Stealing credentials for ML system access",
            articles=["mitre_atlas/ta08"],
            severity="HIGH",
        ),
        "TA09": ATLASControl(
            tactic_id="TA09",
            tactic_name="Discovery",
            description="Exploring ML system environment and capabilities",
            articles=["mitre_atlas/ta09"],
            severity="MEDIUM",
        ),
        "TA10": ATLASControl(
            tactic_id="TA10",
            tactic_name="Collection",
            description="Gathering data from ML system or environment",
            articles=["mitre_atlas/ta10"],
            severity="HIGH",
        ),
        "TA11": ATLASControl(
            tactic_id="TA11",
            tactic_name="ML Model Access",
            description="Unauthorized access or extraction of ML models",
            articles=["mitre_atlas/ta11"],
            severity="CRITICAL",
        ),
        "TA12": ATLASControl(
            tactic_id="TA12",
            tactic_name="Exfiltration",
            description="Exfiltrating data from ML system",
            articles=["mitre_atlas/ta12"],
            severity="HIGH",
        ),
        "TA13": ATLASControl(
            tactic_id="TA13",
            tactic_name="Impact",
            description="Degrading or manipulating ML system integrity",
            articles=["mitre_atlas/ta13"],
            severity="CRITICAL",
        ),
        "TA14": ATLASControl(
            tactic_id="TA14",
            tactic_name="Supply Chain Compromise",
            description="Attacking ML system through supply chain",
            articles=["mitre_atlas/ta14"],
            severity="HIGH",
        ),
        "TA15": ATLASControl(
            tactic_id="TA15",
            tactic_name="Staging",
            description="Preparing infrastructure for ML system attack",
            articles=["mitre_atlas/ta15"],
            severity="MEDIUM",
        ),
    }

    def __init__(self):
        self._findings: Dict[str, List[dict]] = {t: [] for t in self.TACTICS.keys()}

    def map_scan_results_to_controls(self, scan_results: List[dict]) -> Dict[str, dict]:
        """Map scan results to MITRE ATLAS tactics."""
        assessments = {}
        for tactic_id, tactic in self.TACTICS.items():
            # Filter findings matching this tactic
            matching = [
                r
                for r in scan_results
                if any(a in r.get("attack_id", "") for a in tactic.articles)
            ]
            assessments[tactic_id] = {
                "tactic_id": tactic_id,
                "tactic_name": tactic.tactic_name,
                "description": tactic.description,
                "severity": tactic.severity,
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
            severity_weights.get(assessments[t].get("severity", "LOW"), 0.1)
            for t in assessments
        )
        passing_weight = sum(
            severity_weights.get(assessments[t].get("severity", "LOW"), 0.1)
            for t in assessments
            if assessments[t].get("passing", True)
        )
        if total_weight == 0:
            return 100.0
        return (passing_weight / total_weight) * 100.0

    def identify_gaps(self, assessments: Dict[str, dict]) -> List[Gap]:
        """Identify tactics where findings exist."""
        gaps = []
        for tactic_id, assessment in assessments.items():
            if not assessment.get("passing", True):
                gaps.append(
                    Gap(
                        framework="mitre_atlas",
                        control_id=tactic_id,
                        control_name=assessment.get("tactic_name", tactic_id),
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
