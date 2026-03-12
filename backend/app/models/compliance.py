"""Compliance Record model."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    framework: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # eu_ai_act | nist_ai_rmf | owasp_llm | mitre_atlas | iso_42001 | soc2_ai
    overall_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    controls_passed: Mapped[int] = mapped_column(default=0, nullable=False)
    controls_failed: Mapped[int] = mapped_column(default=0, nullable=False)
    controls_na: Mapped[int] = mapped_column(default=0, nullable=False)
    control_results: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    evidence: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    gap_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    remediation_roadmap: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
