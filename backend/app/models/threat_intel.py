"""Threat Intelligence Contribution model."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ThreatIntelContribution(Base):
    __tablename__ = "threat_intel_contributions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # No org_id — fully anonymized
    attack_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    model_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    industry_vertical: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    asr_sample: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    system_prompt_length_bucket: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tools_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    memory_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    multi_agent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False, index=True)
