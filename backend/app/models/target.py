"""Target model — the AI system being tested."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)  # openai, langchain, crewai, etc.
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    model_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # gpt-4o, claude-sonnet, etc.
    framework: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    auth_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # encrypted headers/keys
    tools: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    memory_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_multi_agent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_scan_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="targets")
    scans: Mapped[list["Scan"]] = relationship("Scan", back_populates="target", cascade="all, delete-orphan")
