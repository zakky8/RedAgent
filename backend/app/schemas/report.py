"""Report generation and management schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ReportType(str, Enum):
    """Report type enumeration."""
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    EU_AI_ACT = "eu_ai_act"
    REMEDIATION = "remediation"


class ReportStatus(str, Enum):
    """Report generation status enumeration."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportBase(BaseModel):
    """Base report schema."""
    report_type: ReportType
    scan_id: str = Field(..., description="ID of the scan this report is for")


class ReportCreate(ReportBase):
    """Schema for creating a new report."""
    include_frameworks: Optional[List[str]] = None
    custom_branding: Optional[dict] = None


class ReportOut(BaseModel):
    """Report output schema for API responses."""
    id: str = Field(..., description="Unique report identifier")
    org_id: str = Field(..., description="Organization ID")
    scan_id: str = Field(..., description="Associated scan ID")
    report_type: ReportType = Field(..., description="Type of report")
    status: ReportStatus = Field(..., description="Current generation status")
    file_url: Optional[str] = Field(None, description="URL to download the generated report")
    created_at: str = Field(..., description="Report creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class ReportGenerateRequest(BaseModel):
    """Request to generate a new report."""
    scan_id: str = Field(..., description="ID of the scan to report on")
    report_type: ReportType = Field(..., description="Type of report to generate")
    include_frameworks: Optional[List[str]] = Field(None, description="Compliance frameworks to include")
    custom_branding: Optional[dict] = Field(None, description="Custom branding configuration")


class ReportListResponse(BaseModel):
    """Paginated list of reports."""
    items: List[ReportOut] = Field(..., description="List of reports")
    total: int = Field(..., description="Total number of reports")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
