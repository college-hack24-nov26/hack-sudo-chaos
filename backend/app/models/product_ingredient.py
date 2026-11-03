"""Product ingredients bridge model for YumSure."""

import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Integer, Numeric, Boolean, ForeignKey,
    UniqueConstraint, Index, Uuid
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductIngredient(Base):
    """
    Bridge entity capturing ingredients listed on a specific product label.
    Preserves descending weight order (sequence_order) mandated by FSSAI regulations.
    """
    __tablename__ = "product_ingredients"

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
    ingredient_code: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("ingredients.ingredient_code"),
        nullable=False
    )
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    declared_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    is_allergen_declared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    declared_label_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("product_id", "sequence_order", name="uq_product_ingredient"),
        Index("idx_product_ingredients_pid", "product_id"),
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="product_ingredients")

