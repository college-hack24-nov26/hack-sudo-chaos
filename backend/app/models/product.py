"""Products model for YumSure."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any
from sqlalchemy import (
    String, Boolean, Numeric, DateTime, ForeignKey,
    CheckConstraint, Index, func, Uuid
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    """
    Central product entity in 3NF schema.
    Barcode is unique; is_verified flag guards against external API overwrites.
    """
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    barcode: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    package_size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serving_size_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    serving_size_unit: Mapped[str] = mapped_column(String(20), default="g", nullable=False)
    food_form: Mapped[str] = mapped_column(String(20), nullable=False)
    food_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    source_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("data_sources.source_id", ondelete="SET NULL"),
        nullable=True
    )
    source_retrieval_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_source_payload: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "food_form IN ('solid', 'liquid')",
            name="chk_product_food_form"
        ),
    )

    # Relationships
    data_source: Mapped[Optional["DataSource"]] = relationship("DataSource", back_populates="products")
    nutrients: Mapped[List["ProductNutrient"]] = relationship(
        "ProductNutrient",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    ingredients: Mapped[List["ProductIngredient"]] = relationship(
        "ProductIngredient",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductIngredient.sequence_order"
    )
    ai_explanations: Mapped[List["AIExplanation"]] = relationship(
        "AIExplanation",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    scan_history: Mapped[List["ScanHistory"]] = relationship(
        "ScanHistory",
        back_populates="product"
    )

