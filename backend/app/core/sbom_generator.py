"""SBOM Generator — Software Bill of Materials for AI systems."""
import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class AIComponent:
    name: str
    version: str
    component_type: str  # model, library, dataset, tool
    supplier: str
    license: str = "Unknown"
    purl: str = ""  # Package URL
    vulnerabilities: list[dict] = field(default_factory=list)
    risk_level: str = "unknown"


KNOWN_VULNERABILITIES = {
    "langchain": [{"cve": "CVE-2023-38896", "severity": "high", "description": "Arbitrary code execution via LLMChain"}],
    "transformers": [{"cve": "CVE-2023-7018", "severity": "medium", "description": "Deserialization vulnerability"}],
}


class SBOMGenerator:
    """Generates CycloneDX and SPDX SBOMs for AI systems."""

    def __init__(self, ai_system_name: str, version: str = "1.0.0"):
        self.system_name = ai_system_name
        self.version = version
        self.components: list[AIComponent] = []

    def add_component(self, component: AIComponent):
        """Add component and enrich with known vulnerabilities."""
        name_lower = component.name.lower()
        if name_lower in KNOWN_VULNERABILITIES:
            component.vulnerabilities = KNOWN_VULNERABILITIES[name_lower]
            severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            max_severity = max(
                (severity_map.get(v["severity"], 0) for v in component.vulnerabilities),
                default=0
            )
            severity_names = {4: "critical", 3: "high", 2: "medium", 1: "low", 0: "unknown"}
            component.risk_level = severity_names.get(max_severity, "unknown")
        self.components.append(component)

    def from_requirements(self, requirements_content: str) -> list[AIComponent]:
        """Parse requirements.txt and create components."""
        AI_PACKAGES = {
            "openai": ("OpenAI", "openai"), "anthropic": ("Anthropic", "anthropic"),
            "langchain": ("LangChain AI", "python:langchain"),
            "langchain-core": ("LangChain AI", "python:langchain-core"),
            "transformers": ("HuggingFace", "python:transformers"),
            "torch": ("Meta", "python:torch"), "tensorflow": ("Google", "python:tensorflow"),
            "sentence-transformers": ("HuggingFace", "python:sentence-transformers"),
            "crewai": ("CrewAI", "python:crewai"), "autogen": ("Microsoft", "python:autogen"),
        }
        components = []
        for line in requirements_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.replace("==", "=").replace(">=", "=").split("=")
            name = parts[0].lower().strip()
            version = parts[1].strip() if len(parts) > 1 else "unknown"
            if name in AI_PACKAGES:
                supplier, purl_prefix = AI_PACKAGES[name]
                comp = AIComponent(
                    name=name, version=version, component_type="library",
                    supplier=supplier, purl=f"pkg:{purl_prefix}@{version}"
                )
                self.add_component(comp)
                components.append(comp)
        return components

    def to_cyclonedx(self) -> dict:
        """Export as CycloneDX 1.5 JSON."""
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tools": [{"vendor": "AgentRed", "name": "SBOM Generator", "version": "1.0.0"}],
                "component": {
                    "type": "application", "name": self.system_name,
                    "version": self.version, "bom-ref": str(uuid.uuid4())
                }
            },
            "components": [
                {
                    "type": "library",
                    "bom-ref": str(uuid.uuid4()),
                    "name": c.name,
                    "version": c.version,
                    "supplier": {"name": c.supplier},
                    "purl": c.purl,
                    "licenses": [{"license": {"name": c.license}}],
                    "vulnerabilities": c.vulnerabilities,
                } for c in self.components
            ]
        }

    def to_spdx(self) -> dict:
        """Export as SPDX 2.3 JSON."""
        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": f"{self.system_name}-sbom",
            "documentNamespace": f"https://agentred.io/sbom/{uuid.uuid4()}",
            "creationInfo": {
                "created": datetime.now(timezone.utc).isoformat(),
                "creators": ["Tool: AgentRed SBOM Generator 1.0.0"]
            },
            "packages": [
                {
                    "SPDXID": f"SPDXRef-{c.name}-{i}",
                    "name": c.name, "versionInfo": c.version,
                    "supplier": f"Organization: {c.supplier}",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "licenseConcluded": c.license,
                    "licenseDeclared": c.license,
                    "copyrightText": "NOASSERTION"
                } for i, c in enumerate(self.components)
            ]
        }

    def get_risk_summary(self) -> dict:
        """Get vulnerability risk summary."""
        all_vulns = [v for c in self.components for v in c.vulnerabilities]
        return {
            "total_components": len(self.components),
            "total_vulnerabilities": len(all_vulns),
            "critical": sum(1 for v in all_vulns if v.get("severity") == "critical"),
            "high": sum(1 for v in all_vulns if v.get("severity") == "high"),
            "medium": sum(1 for v in all_vulns if v.get("severity") == "medium"),
            "low": sum(1 for v in all_vulns if v.get("severity") == "low"),
            "risk_level": "critical" if any(v.get("severity") == "critical" for v in all_vulns) else
                         "high" if any(v.get("severity") == "high" for v in all_vulns) else "medium"
        }
