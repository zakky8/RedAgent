"""Compliance assessment and framework schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks enumeration."""
    EU_AI_ACT = "eu_ai_act"
    NIST_AI_RMF = "nist_ai_rmf"
    OWASP_LLM = "owasp_llm"
    OWASP_AGENTIC = "owasp_agentic"
    OWASP_MCP = "owasp_mcp"
    ISO_42001 = "iso_42001"
    SOC2_AI = "soc2_ai"


class ControlStatus(str, Enum):
    """Control assessment status enumeration."""
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    NOT_ASSESSED = "not_assessed"


class ControlAssessment(BaseModel):
    """Individual control assessment result."""
    control_id: str = Field(..., description="Unique control identifier")
    control_name: str = Field(..., description="Human-readable control name")
    status: ControlStatus = Field(..., description="Current control status")
    score: float = Field(..., ge=0.0, le=100.0, description="Control compliance score")
    findings_count: int = Field(default=0, description="Number of findings for this control")
    evidence: Optional[List[str]] = Field(None, description="Evidence supporting the assessment")


class FrameworkScore(BaseModel):
    """Overall framework compliance score."""
    framework: ComplianceFramework = Field(..., description="Compliance framework")
    score: float = Field(..., ge=0.0, le=100.0, description="Overall framework compliance score")
    controls_total: int = Field(..., description="Total number of controls in framework")
    controls_passing: int = Field(..., description="Number of passing controls")
    last_assessed: str = Field(..., description="Last assessment timestamp")


class GapItem(BaseModel):
    """Compliance gap or finding."""
    control_id: str = Field(..., description="Associated control ID")
    description: str = Field(..., description="Description of the gap or finding")
    severity: str = Field(..., description="Severity level (critical, high, medium, low)")
    remediation_steps: List[str] = Field(..., description="Recommended remediation steps")


class ComplianceAssessmentOut(BaseModel):
    """Compliance assessment output schema."""
    framework: ComplianceFramework = Field(..., description="Assessed framework")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall compliance score")
    controls: List[ControlAssessment] = Field(..., description="Individual control assessments")
    gaps: List[GapItem] = Field(default_factory=list, description="Identified compliance gaps")
    generated_at: str = Field(..., description="Assessment generation timestamp")


class ComplianceAssessRequest(BaseModel):
    """Request to perform compliance assessment."""
    scan_id: str = Field(..., description="ID of the scan to assess")
    frameworks: List[ComplianceFramework] = Field(..., description="Frameworks to assess against")
