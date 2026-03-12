"""AgentRed SDK Type Definitions."""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ScanStatus(str, Enum):
    """Scan execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Severity(str, Enum):
    """Vulnerability severity level."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    """A single attack result/finding."""
    attack_id: str
    attack_name: str
    category: str
    severity: Severity
    success: bool
    payload_used: str
    response_received: str
    vulnerability_found: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    asr_rate: Optional[float] = None
    framework_mapping: Dict[str, str] = {}
    cvss_score: Optional[float] = None
    remediation: Dict[str, Any] = {}
    execution_time_ms: int


class Scan(BaseModel):
    """Scan object with metadata and status."""
    id: str
    target_id: str
    status: ScanStatus
    mode: str
    categories: List[str] = []
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    risk_score: Optional[float] = None
    findings_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0


class Target(BaseModel):
    """Target configuration."""
    id: str
    name: str
    target_type: str
    endpoint: str
    created_at: datetime
    last_scan_at: Optional[datetime] = None
    last_scan_id: Optional[str] = None
    is_active: bool = True


class CreateScanRequest(BaseModel):
    """Request to create a new scan."""
    target_id: str
    mode: str = "standard"
    categories: List[str] = []
    timeout_seconds: Optional[int] = 3600


class Report(BaseModel):
    """Generated report."""
    id: str
    scan_id: str
    report_type: str
    title: str
    frameworks: List[str] = []
    generated_at: datetime
    download_url: Optional[str] = None
    status: str = "ready"


class ComplianceAssessment(BaseModel):
    """Compliance assessment result."""
    scan_id: str
    framework: str
    score: float = Field(ge=0.0, le=100.0)
    controls_passed: int
    controls_failed: int
    gaps: List[str] = []
    recommendations: List[str] = []
    assessed_at: datetime


class AttackSummary(BaseModel):
    """Summary of available attack."""
    attack_id: str
    name: str
    description: str
    category: str
    severity: Severity
    framework_mapping: Dict[str, str] = {}


class ScanStats(BaseModel):
    """Statistics for a scan."""
    total_findings: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    risk_score: float
    success_rate: float
