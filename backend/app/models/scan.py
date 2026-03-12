"""Scan model."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Text, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("targets.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    # pending | running | completed | failed | cancelled
    scan_mode: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
    # quick | standard | deep | custom | compliance
    test_mode: Mapped[str] = mapped_column(String(50), default="black_box", nullable=False)
    # black_box | gray_box | white_box | assumed_breach
    categories: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    attack_ids: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    probabilistic_runs: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    concurrent_workers: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    asr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # attack success rate
    total_attacks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_attacks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    high_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medium_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="scans")
    target: Mapped["Target"] = relationship("Target", back_populates="scans")
    results: Mapped[list["AttackResult"]] = relationship("AttackResult", back_populates="scan", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="scan", cascade="all, delete-orphan")
