"""Shadow AI Asset model."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ShadowAIAsset(Base):
    __tablename__ = "shadow_ai_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    discovered_via: Mapped[str] = mapped_column(String(100), nullable=False)
    is_authorized: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    authorized_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    authorized_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
