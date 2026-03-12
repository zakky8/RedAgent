"""Organization model — top-level tenant."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Integer, Text, JSON, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
import enum


class PlanTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan_tier: Mapped[str] = mapped_column(String(50), default="pro", nullable=False)
    # NoBilling: all users treated as Pro — no billing fields
    scans_used_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scans_limit: Mapped[int] = mapped_column(Integer, default=999999, nullable=False)
    intel_sharing_opted_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_residency_enforced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_region: Mapped[str] = mapped_column(String(50), default="us-east-1", nullable=False)
    industry_vertical: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    white_label_logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    targets: Mapped[list["Target"]] = relationship("Target", back_populates="organization", cascade="all, delete-orphan")
    scans: Mapped[list["Scan"]] = relationship("Scan", back_populates="organization", cascade="all, delete-orphan")
    api_keys: Mapped[list["APIKey"]] = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")
