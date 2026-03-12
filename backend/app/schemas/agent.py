"""AI agent registry and monitoring schemas."""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from enum import Enum


class AgentFramework(str, Enum):
    """Supported AI agent framework enumeration."""
    LANGCHAIN = "langchain"
    LANGGRAPH = "langgraph"
    CREWAI = "crewai"
    AUTOGEN = "autogen"
    N8N = "n8n"
    SEMANTIC_KERNEL = "semantic_kernel"
    CUSTOM = "custom"


class MonitoringStatus(str, Enum):
    """Agent monitoring status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ALERTING = "alerting"


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., description="Agent name")
    framework: AgentFramework = Field(..., description="AI framework used by the agent")
    endpoint_url: str = Field(..., description="Agent endpoint URL")
    description: Optional[str] = Field(None, description="Agent description")


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""
    config: dict = Field(default_factory=dict, description="Agent configuration dictionary")
    system_prompt: Optional[str] = Field(None, description="System prompt for the agent")


class AgentOut(BaseModel):
    """Agent output schema for API responses."""
    id: str = Field(..., description="Unique agent identifier")
    org_id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Agent name")
    framework: AgentFramework = Field(..., description="AI framework used")
    monitoring_status: MonitoringStatus = Field(..., description="Current monitoring status")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Current risk score")
    last_scan_id: Optional[str] = Field(None, description="ID of the last completed scan")
    created_at: str = Field(..., description="Agent creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class AgentKillSwitchRequest(BaseModel):
    """Request to activate agent kill switch."""
    agent_id: str = Field(..., description="ID of the agent to disable")
    reason: str = Field(..., description="Reason for killing the agent")


class AgentStats(BaseModel):
    """Agent statistics snapshot."""
    total_requests: int = Field(default=0, description="Total requests handled by agent")
    avg_response_time_ms: float = Field(default=0.0, description="Average response time in milliseconds")
    anomaly_count_7d: int = Field(default=0, description="Anomalies detected in last 7 days")
    kill_switch_triggered: bool = Field(default=False, description="Whether kill switch has been activated")


class AgentListResponse(BaseModel):
    """Paginated list of agents."""
    items: List[AgentOut] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")
