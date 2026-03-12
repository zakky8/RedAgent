"""ASR Trend model for dashboard trend charts and benchmarking."""
import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, ForeignKey, Float, Integer, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ASRTrend(Base):
    __tablename__ = "asr_trends"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), nullable=True)
    date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    overall_asr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    asr_by_category: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    severity_distribution: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    coverage_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    attacks_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attacks_successful: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
