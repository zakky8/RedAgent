"""Scan schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid


class ScanCreate(BaseModel):
    target_id: str
    name: Optional[str] = None
    scan_mode: str = "standard"  # quick | standard | deep | custom | compliance
    test_mode: str = "black_box"  # black_box | gray_box | white_box | assumed_breach
    categories: Optional[List[str]] = None
    attack_ids: Optional[List[str]] = None
    probabilistic_runs: int = Field(default=1, ge=1, le=100)
    concurrent_workers: int = Field(default=4, ge=1, le=10)
    fail_threshold: Optional[float] = None  # Risk score that triggers failure


class ScanResponse(BaseModel):
    id: str
    org_id: str
    target_id: str
    name: Optional[str]
    status: str
    scan_mode: str
    test_mode: str
    risk_score: Optional[float]
    asr: Optional[float]
    total_attacks: int
    successful_attacks: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}


class AttackResultResponse(BaseModel):
    id: str
    attack_id: str
    attack_name: str
    category: str
    severity: str
    success: bool
    confidence: float
    asr_rate: Optional[float]
    payload_used: Optional[str]
    response_received: Optional[str]
    vulnerability_found: Optional[str]
    framework_mapping: Optional[dict]
    cvss_score: Optional[float]
    remediation: Optional[dict]
    healing_suggestion: Optional[dict]
    execution_time_ms: int
    is_false_positive: bool
    created_at: str

    model_config = {"from_attributes": True}
