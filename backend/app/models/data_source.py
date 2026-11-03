"""Data source provenance model for YumSure."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DataSource(Base):
    """
    Tracks data origin and licensing (e.g. Open Food Facts ODbL, FSSAI Official, User Upload).
    Guarantees legal attribution and provenance integrity.
    """
    __tablename__ = "data_sources"

    source_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    license_type: Mapped[str] = mapped_column(String(100), nullable=False)
    license_url: Mapped[str] = mapped_column(Text, nullable=False)
    attribution_text: Mapped[str] = mapped_column(Text, nullable=False)
    permits_redistribution: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="data_source")

