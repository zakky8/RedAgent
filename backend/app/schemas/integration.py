"""SIEM/ticketing integration schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class IntegrationType(str, Enum):
    """Supported integration type enumeration."""
    SPLUNK = "splunk"
    SENTINEL = "sentinel"
    ELASTIC = "elastic"
    JIRA = "jira"
    GITHUB = "github"
    GITLAB = "gitlab"
    WEBHOOK = "webhook"


class IntegrationStatus(str, Enum):
    """Integration status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class IntegrationBase(BaseModel):
    """Base integration schema."""
    name: str = Field(..., description="Integration name")
    integration_type: IntegrationType = Field(..., description="Type of integration")


class IntegrationCreate(IntegrationBase):
    """Schema for creating a new integration."""
    config: dict = Field(..., description="Integration configuration (contains host/url/tokens)")


class IntegrationOut(BaseModel):
    """Integration output schema for API responses."""
    id: str = Field(..., description="Unique integration identifier")
    org_id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Integration name")
    integration_type: IntegrationType = Field(..., description="Type of integration")
    status: IntegrationStatus = Field(..., description="Current integration status")
    last_sync_at: Optional[str] = Field(None, description="Last successful sync timestamp")
    error_message: Optional[str] = Field(None, description="Latest error message if status is ERROR")
    created_at: str = Field(..., description="Integration creation timestamp")

    model_config = {"from_attributes": True}


class IntegrationTestResult(BaseModel):
    """Result of integration connectivity test."""
    success: bool = Field(..., description="Whether test was successful")
    latency_ms: int = Field(..., description="Response latency in milliseconds")
    error: Optional[str] = Field(None, description="Error message if test failed")
    details: dict = Field(default_factory=dict, description="Additional test details")


class IntegrationListResponse(BaseModel):
    """Paginated list of integrations."""
    items: List[IntegrationOut] = Field(..., description="List of integrations")
    total: int = Field(..., description="Total number of integrations")
