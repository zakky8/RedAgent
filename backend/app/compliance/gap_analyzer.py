"""Cross-framework gap analysis engine."""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Gap:
    framework: str
    control_id: str
    control_name: str
    severity: str
    finding_count: int
    remediation_priority: int
    estimated_effort_days: int


class GapAnalyzer:
    def analyze(self, all_assessments: Dict[str, dict]) -> List[Gap]:
        """Cross-framework gap analysis — returns prioritized gaps."""
        gaps = []
        for framework, assessment in all_assessments.items():
            for control_id, result in assessment.get("controls", {}).items():
                if not result.get("passing", True):
                    gaps.append(
                        Gap(
                            framework=framework,
                            control_id=control_id,
                            control_name=result.get("name", control_id),
                            severity=result.get("severity", "MEDIUM"),
                            finding_count=result.get("finding_count", 0),
                            remediation_priority=self._priority(
                                result.get("severity", "MEDIUM")
                            ),
                            estimated_effort_days=self._effort(
                                result.get("severity", "MEDIUM")
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
