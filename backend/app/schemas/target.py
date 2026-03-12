"""Target schemas."""
from pydantic import BaseModel, HttpUrl
from typing import Optional, Any
import uuid


class TargetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_type: str
    endpoint_url: Optional[str] = None
    model_type: Optional[str] = None
    framework: Optional[str] = None
    system_prompt: Optional[str] = None
    auth_config: Optional[dict] = None
    tools: Optional[list] = None
    memory_enabled: bool = False
    is_multi_agent: bool = False


class TargetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    endpoint_url: Optional[str] = None
    model_type: Optional[str] = None
    system_prompt: Optional[str] = None
    auth_config: Optional[dict] = None
    is_active: Optional[bool] = None


class TargetResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str]
    target_type: str
    endpoint_url: Optional[str]
    model_type: Optional[str]
    framework: Optional[str]
    memory_enabled: bool
    is_multi_agent: bool
    risk_score: Optional[float]
    is_active: bool
    last_scan_at: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}


class TargetTestResponse(BaseModel):
    success: bool
    latency_ms: int
    error: Optional[str] = None
    detected_framework: Optional[str] = None
