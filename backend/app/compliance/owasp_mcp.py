"""OWASP MCP Top 10 compliance engine."""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class MCPControl:
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


class OWASPMCPEngine:
    CONTROLS = {
        "MCP01": MCPControl(
            control_id="MCP01",
            name="Token Mismanagement",
            description="Improper handling of MCP authentication tokens and credentials",
            articles=["owasp_mcp/mcp01"],
            severity="CRITICAL",
        ),
        "MCP02": MCPControl(
            control_id="MCP02",
            name="Excessive Permissions",
            description="Tools granted permissions beyond principle of least privilege",
            articles=["owasp_mcp/mcp02"],
            severity="HIGH",
        ),
        "MCP03": MCPControl(
            control_id="MCP03",
            name="Tool Poisoning",
            description="Malicious or compromised tools in MCP ecosystem",
            articles=["owasp_mcp/mcp03"],
            severity="CRITICAL",
        ),
        "MCP04": MCPControl(
            control_id="MCP04",
            name="Supply Chain Tampering",
            description="Tool dependencies vulnerable to tampering or version substitution",
            articles=["owasp_mcp/mcp04"],
            severity="HIGH",
        ),
        "MCP05": MCPControl(
            control_id="MCP05",
            name="Prompt Injection via Tools",
            description="Tools accepting untrusted inputs that reach LLM context",
            articles=["owasp_mcp/mcp05"],
            severity="CRITICAL",
        ),
        "MCP06": MCPControl(
            control_id="MCP06",
            name="Insecure Data Handling",
            description="Tools exposing sensitive data without encryption or access controls",
            articles=["owasp_mcp/mcp06"],
            severity="HIGH",
        ),
        "MCP07": MCPControl(
            control_id="MCP07",
            name="Inadequate Audit",
            description="Missing or insufficient logging of tool invocations and data access",
            articles=["owasp_mcp/mcp07"],
            severity="MEDIUM",
        ),
        "MCP08": MCPControl(
            control_id="MCP08",
            name="Unsafe Multi-Server Orchestration",
            description="Orchestrating MCP servers without proper isolation or validation",
            articles=["owasp_mcp/mcp08"],
            severity="HIGH",
        ),
        "MCP09": MCPControl(
            control_id="MCP09",
            name="Authentication Bypass",
            description="Flaws allowing unauthorized access to MCP servers or tools",
            articles=["owasp_mcp/mcp09"],
            severity="CRITICAL",
        ),
        "MCP10": MCPControl(
            control_id="MCP10",
            name="Rug Pull / Version Substitution",
            description="Malicious tool maintainers removing or modifying tools unexpectedly",
            articles=["owasp_mcp/mcp10"],
            severity="MEDIUM",
        ),
    }

    def __init__(self):
        self._findings: Dict[str, List[dict]] = {c: [] for c in self.CONTROLS.keys()}

    def map_scan_results_to_controls(self, scan_results: List[dict]) -> Dict[str, dict]:
        """Map scan results to OWASP MCP controls."""
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
                        framework="owasp_mcp",
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
