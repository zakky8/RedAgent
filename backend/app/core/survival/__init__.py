"""
AgentRed 6-Year Survival Modules

This package contains long-term operational modules designed to keep the red teaming
platform secure and effective over a 6-year operational lifespan:

- ThreatIntelligenceNetwork: Aggregates AI threat intelligence
- ImmutableAuditLogger: Tamper-proof audit trail with hash-chaining
- RegressionGate: CI/CD security regression detection
- ContinuousEngine: Scheduled continuous red team scanning
- SyntheticAttackGenerator: AI-powered attack variant generation
- DriftDetector: Model behavior drift detection
- OCSFFormatter: OCSF 1.1.0 findings export
- STIXFormatter: STIX 2.1 threat intelligence export
"""

from .threat_intel_network import ThreatIntelligenceNetwork
from .immutable_audit_logger import ImmutableAuditLogger
from .regression_gate import RegressionGate
from .continuous_engine import ContinuousEngine
from .synthetic_attack_generator import SyntheticAttackGenerator
from .drift_detector import DriftDetector
from .ocsf_formatter import OCSFFormatter
from .stix_formatter import STIXFormatter

__all__ = [
    "ThreatIntelligenceNetwork",
    "ImmutableAuditLogger",
    "RegressionGate",
    "ContinuousEngine",
    "SyntheticAttackGenerator",
    "DriftDetector",
    "OCSFFormatter",
    "STIXFormatter",
]
