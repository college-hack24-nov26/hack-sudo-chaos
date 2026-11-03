"""Ingredients master catalog model for YumSure."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Allowed functional categories per FSSAI / INS standards
INGREDIENT_CATEGORIES = (
    'SWEETENER', 'PRESERVATIVE', 'EMULSIFIER', 'FLAVOUR_ENHANCER',
    'REFINED_CARB', 'FAT_OIL', 'PROTEIN', 'FIBRE', 'COLOUR', 'FORTIFICATION', 'OTHER'
)


class Ingredient(Base):
    """
    Standard ingredient master record including INS numbers and FSSAI allergen flags.
    """
    __tablename__ = "ingredients"

    ingredient_code: Mapped[str] = mapped_column(String(100), primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ins_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    is_fssai_major_allergen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    functional_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            f"category IN {tuple(INGREDIENT_CATEGORIES)}",
            name="chk_ingredient_category"
        ),
    )

    # Relationships
    product_ingredients: Mapped[List["ProductIngredient"]] = relationship(
        "ProductIngredient", back_populates="ingredient"
    )

