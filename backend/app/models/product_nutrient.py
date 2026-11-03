"""Product nutrient values bridge model preserving four-state nutrient semantics."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Numeric, DateTime, ForeignKey,
    CheckConstraint, UniqueConstraint, Index, func, Uuid
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Strict 4-State Nutrient Semantics
NUTRIENT_DATA_STATUSES = ('PRESENT', 'UNKNOWN', 'EXPLICITLY_ZERO', 'NOT_DECLARED')


class ProductNutrient(Base):
    """
    Normalized 3NF nutrient values per product.
    
    CRITICAL: Preserves strict four-state nutrient semantics:
    - PRESENT: Fact extracted explicitly from label (e.g. Protein: 8.0g).
    - EXPLICITLY_ZERO: Declared explicitly as zero (e.g. Trans fat: 0g).
    - NOT_DECLARED: Omitted from product label. Never conflated with zero.
    - UNKNOWN: Data corrupted or unparsable from source.
    """
    __tablename__ = "product_nutrients"

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
    nutrient_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("nutrients.nutrient_code"),
        nullable=False
    )
    per_100g_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    per_serving_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    data_status: Mapped[str] = mapped_column(String(30), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("product_id", "nutrient_code", name="uq_product_nutrient"),
        Index("idx_product_nutrients_lookup", "product_id", "nutrient_code"),
        CheckConstraint(
            f"data_status IN {tuple(NUTRIENT_DATA_STATUSES)}",
            name="chk_product_nutrient_status"
        ),
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="nutrients")
    nutrient: Mapped["Nutrient"] = relationship("Nutrient", back_populates="product_nutrients")

