"""
AgentRed Compliance Engines Package.
Provides compliance mapping engines for multiple regulatory frameworks.
"""
from app.compliance.eu_ai_act import EUAIActEngine
from app.compliance.nist_ai_rmf import NISTAIRMFEngine
from app.compliance.owasp_llm import OWASPLLMEngine
from app.compliance.iso_42001 import ISO42001Engine
from app.compliance.soc2_ai import SOC2AIEngine
from app.compliance.owasp_agentic import OWASPAgenticEngine
from app.compliance.owasp_mcp import OWASPMCPEngine
from app.compliance.mitre_atlas import MITREATLASEngine
from app.compliance.gap_analyzer import GapAnalyzer
from app.compliance.evidence_collector import EvidenceCollector
from app.compliance.remediation import RemediationRoadmap

__all__ = [
    "EUAIActEngine",
    "NISTAIRMFEngine",
    "OWASPLLMEngine",
    "ISO42001Engine",
    "SOC2AIEngine",
    "OWASPAgenticEngine",
    "OWASPMCPEngine",
    "MITREATLASEngine",
    "GapAnalyzer",
    "EvidenceCollector",
    "RemediationRoadmap",
    "SUPPORTED_FRAMEWORKS",
]

SUPPORTED_FRAMEWORKS = {
    "EU_AI_ACT": EUAIActEngine,
    "NIST_AI_RMF": NISTAIRMFEngine,
    "OWASP_LLM_TOP10": OWASPLLMEngine,
    "ISO_42001": ISO42001Engine,
    "SOC2_AI": SOC2AIEngine,
    "OWASP_AGENTIC": OWASPAgenticEngine,
    "OWASP_MCP": OWASPMCPEngine,
    "MITRE_ATLAS": MITREATLASEngine,
}
