"""Schema package exports."""

# Auth schemas
from .auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserResponse,
    APIKeyCreateRequest,
    APIKeyResponse,
)

# Scan schemas
from .scan import (
    ScanCreate,
    ScanResponse,
    AttackResultResponse,
)

# Target schemas
from .target import (
    TargetCreate,
    TargetUpdate,
    TargetResponse,
    TargetTestResponse,
)

# Report schemas
from .report import (
    ReportType,
    ReportStatus,
    ReportBase,
    ReportCreate,
    ReportOut,
    ReportGenerateRequest,
    ReportListResponse,
)

# Compliance schemas
from .compliance import (
    ComplianceFramework,
    ControlStatus,
    ControlAssessment,
    FrameworkScore,
    GapItem,
    ComplianceAssessmentOut,
    ComplianceAssessRequest,
)

# Agent schemas
from .agent import (
    AgentFramework,
    MonitoringStatus,
    AgentBase,
    AgentCreate,
    AgentOut,
    AgentKillSwitchRequest,
    AgentStats,
    AgentListResponse,
)

# Integration schemas
from .integration import (
    IntegrationType,
    IntegrationStatus,
    IntegrationBase,
    IntegrationCreate,
    IntegrationOut,
    IntegrationTestResult,
    IntegrationListResponse,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "UserResponse",
    "APIKeyCreateRequest",
    "APIKeyResponse",
    # Scan
    "ScanCreate",
    "ScanResponse",
    "AttackResultResponse",
    # Target
    "TargetCreate",
    "TargetUpdate",
    "TargetResponse",
    "TargetTestResponse",
    # Report
    "ReportType",
    "ReportStatus",
    "ReportBase",
    "ReportCreate",
    "ReportOut",
    "ReportGenerateRequest",
    "ReportListResponse",
    # Compliance
    "ComplianceFramework",
    "ControlStatus",
    "ControlAssessment",
    "FrameworkScore",
    "GapItem",
    "ComplianceAssessmentOut",
    "ComplianceAssessRequest",
    # Agent
    "AgentFramework",
    "MonitoringStatus",
    "AgentBase",
    "AgentCreate",
    "AgentOut",
    "AgentKillSwitchRequest",
    "AgentStats",
    "AgentListResponse",
    # Integration
    "IntegrationType",
    "IntegrationStatus",
    "IntegrationBase",
    "IntegrationCreate",
    "IntegrationOut",
    "IntegrationTestResult",
    "IntegrationListResponse",
]
