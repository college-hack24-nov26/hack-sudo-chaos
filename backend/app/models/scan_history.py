"""Scan history telemetry and caching log for YumSure."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Index, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ScanHistory(Base):
    """
    Records barcode scan queries anonymously to measure caching efficiency and popular items.
    """
    __tablename__ = "scan_history"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )
    barcode: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    client_ip_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    product: Mapped[Optional["Product"]] = relationship("Product", back_populates="scan_history")

