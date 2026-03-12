"""Attack Result model."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Text, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class AttackResult(Base):
    __tablename__ = "attack_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=True, index=True)
    attack_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    attack_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    asr_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payload_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_received: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vulnerability_found: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    framework_mapping: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    cvss_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    remediation: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    healing_suggestion: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_continuous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_false_positive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    scan: Mapped[Optional["Scan"]] = relationship("Scan", back_populates="results")
