"""Auto-collect compliance evidence from scan results."""
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import json


@dataclass
class Evidence:
    control_id: str
    evidence_type: str  # "scan_result" | "manual" | "automated_test"
    description: str
    data: dict
    collected_at: str
    scan_id: str


class EvidenceCollector:
    def collect_from_scan(self, scan_id: str, scan_results: List[dict]) -> List[Evidence]:
        """Auto-collect evidence from scan results for compliance reporting."""
        evidence = []
        now = datetime.utcnow().isoformat()

        for result in scan_results:
            attack_id = result.get("attack_id", "")
            # Map attack_id to control_id
            control_id = self._map_attack_to_control(attack_id)
            if control_id:
                evidence.append(
                    Evidence(
                        control_id=control_id,
                        evidence_type="scan_result",
                        description=f"Automated test: {result.get('attack_name', attack_id)}",
                        data={
                            "passed": not result.get("vulnerable", False),
                            "severity": result.get("severity", "INFO"),
                            "confidence": result.get("confidence", 0),
                        },
                        collected_at=now,
                        scan_id=scan_id,
                    )
                )
        return evidence

    def _map_attack_to_control(self, attack_id: str) -> str:
        mappings = {
            "llm01": "EU-AI-9.4",
            "llm02": "EU-AI-13.1",
            "llm06": "EU-AI-14.1",
            "owasp-a01": "OWASP-A01",
            "owasp-a02": "OWASP-A02",
        }
        for prefix, control in mappings.items():
            if attack_id.startswith(prefix):
                return control
        return ""

    def package_for_audit(self, evidence: List[Evidence]) -> dict:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_evidence": len(evidence),
            "evidence": [
                {
                    "control_id": e.control_id,
                    "evidence_type": e.evidence_type,
                    "description": e.description,
                    "data": e.data,
                    "collected_at": e.collected_at,
                    "scan_id": e.scan_id,
                }
                for e in evidence
            ],
        }
