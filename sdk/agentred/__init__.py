"""AgentRed Python SDK — AI Red Teaming for every AI system."""
from .client import AgentRedClient
from .exceptions import (
    AgentRedError,
    AuthError,
    RateLimitError,
    ScanError,
    NotFoundError,
    ValidationError,
)
from .types import (
    ScanStatus,
    Severity,
    Finding,
    Scan,
    Target,
    CreateScanRequest,
    Report,
    ComplianceAssessment,
    AttackSummary,
    ScanStats,
)

__version__ = "1.0.0"
__all__ = [
    "AgentRedClient",
    "AgentRedError",
    "AuthError",
    "RateLimitError",
    "ScanError",
    "NotFoundError",
    "ValidationError",
    "ScanStatus",
    "Severity",
    "Finding",
    "Scan",
    "Target",
    "CreateScanRequest",
    "Report",
    "ComplianceAssessment",
    "AttackSummary",
    "ScanStats",
]
