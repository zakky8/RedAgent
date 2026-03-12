"""Compliance API resource."""
from typing import Optional, List


class ComplianceResource:
    """Compliance assessment and framework mapping."""

    def __init__(self, client):
        self._c = client

    def assess(
        self,
        scan_id: str,
        frameworks: Optional[List[str]] = None
    ) -> dict:
        """Run compliance assessment against frameworks."""
        payload = {
            "scan_id": scan_id,
            "frameworks": frameworks or ["eu_ai_act", "owasp_llm", "nist_ai_rmf"]
        }
        return self._c._request("POST", "/compliance/assess", json=payload)

    def posture(self) -> dict:
        """Get overall compliance posture."""
        return self._c._request("GET", "/compliance/posture")

    def list_frameworks(self) -> list:
        """List available compliance frameworks."""
        result = self._c._request("GET", "/compliance/frameworks")
        return result.get("items", []) if isinstance(result, dict) else result

    def get_framework(self, framework_id: str) -> dict:
        """Get framework details."""
        return self._c._request("GET", f"/compliance/frameworks/{framework_id}")

    def remediation_plan(self, assessment_id: str) -> dict:
        """Generate remediation plan from assessment."""
        return self._c._request("GET", f"/compliance/assessments/{assessment_id}/remediation")
