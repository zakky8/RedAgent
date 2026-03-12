"""Remediation roadmap generator."""
from dataclasses import dataclass
from typing import List


@dataclass
class Gap:
    framework: str
    control_id: str
    control_name: str
    severity: str
    finding_count: int
    remediation_priority: int
    estimated_effort_days: int


@dataclass
class RemediationAction:
    priority: int
    gap: Gap
    action: str
    code_example: str
    sprint_week: int


class RemediationRoadmap:
    def generate(self, gaps: List[Gap]) -> List[RemediationAction]:
        actions = []
        week = 1
        for i, gap in enumerate(gaps[:20]):
            actions.append(
                RemediationAction(
                    priority=i + 1,
                    gap=gap,
                    action=self._action_for(gap),
                    code_example=self._code_for(gap),
                    sprint_week=week if i % 3 == 0 and i > 0 else week,
                )
            )
            if (i + 1) % 3 == 0:
                week += 1
        return actions

    def _action_for(self, gap: Gap) -> str:
        actions = {
            "CRITICAL": f"Immediately fix {gap.control_name} — block deployment until resolved",
            "HIGH": f"Fix {gap.control_name} within current sprint",
            "MEDIUM": f"Schedule {gap.control_name} remediation in next sprint",
            "LOW": f"Add {gap.control_name} to tech debt backlog",
        }
        return actions.get(gap.severity, f"Review {gap.control_name}")

    def _code_for(self, gap: Gap) -> str:
        return f"# Fix for {gap.control_id}: {gap.control_name}\n# See AgentRed remediation guide"
