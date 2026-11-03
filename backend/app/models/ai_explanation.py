"""AI explanation audit and caching model for YumSure."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Index, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIExplanation(Base):
    """
    Caches and audits AI-generated consumer explanations (Grok, NVIDIA NIM, or local template).
    Tracks latency and fallback state to verify offline resilience.
    """
    __tablename__ = "ai_explanations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    is_fallback: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index("idx_ai_explanations_pid", "product_id"),
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="ai_explanations")

