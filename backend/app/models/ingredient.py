"""Ingredients master catalog model for YumSure."""

from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import (
    String, Text, Boolean, DateTime, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Allowed functional categories per FSSAI / INS standards
INGREDIENT_CATEGORIES = (
    'SWEETENER', 'PRESERVATIVE', 'EMULSIFIER', 'FLAVOUR_ENHANCER',
    'REFINED_CARB', 'FAT_OIL', 'PROTEIN', 'FIBRE', 'COLOUR', 'FORTIFICATION', 'OTHER'
)

# Scientific processing classifications for ICMR-NIN DGI 2024 UPF matrix
INGREDIENT_PROCESSING_CLASSES = (
    'WHOLE_FOOD',
    'CULINARY_PROCESSED',
    'FUNCTIONAL_ADDITIVE',
    'COSMETIC_ADDITIVE',
    'INDUSTRIAL_FRACTION',
    'INSUFFICIENT_EVIDENCE',
    'UNKNOWN'
)

# Chemical sugar classifications for FSSAI claims & ICMR HFSS evaluation
INGREDIENT_SUGAR_CLASSES = (
    'NOT_SUGAR',
    'INTRINSIC_SUGAR',
    'ADDED_FREE_SUGAR',
    'SUGAR_SUBSTITUTE_SWEETENER',
    'NON_NUTRITIVE_SWEETENER',
    'POLYOL',
    'INSUFFICIENT_EVIDENCE',
    'UNKNOWN'
)


class Ingredient(Base):
    """
    Standard ingredient master record including INS numbers, FSSAI allergen flags,
    and scientific classifications for processing extent and sweetener chemistry.
    Defaults strictly to 'UNKNOWN' to prevent false-positive additive or sugar labeling.
    """
    __tablename__ = "ingredients"

    ingredient_code: Mapped[str] = mapped_column(String(100), primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ins_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    is_fssai_major_allergen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    functional_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Scientific Processing & Sugar Classifications (Phase 1B Contract)
    # Default is strictly UNKNOWN - never assumes functional additive or added sugar without evidence
    processing_classification: Mapped[str] = mapped_column(
        String(30),
        default="UNKNOWN",
        server_default="UNKNOWN",
        nullable=False
    )
    sugar_classification: Mapped[str] = mapped_column(
        String(30),
        default="UNKNOWN",
        server_default="UNKNOWN",
        nullable=False
    )
    classification_evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
        CheckConstraint(
            f"processing_classification IN {tuple(INGREDIENT_PROCESSING_CLASSES)}",
            name="chk_ingredient_proc_class"
        ),
        CheckConstraint(
            f"sugar_classification IN {tuple(INGREDIENT_SUGAR_CLASSES)}",
            name="chk_ingredient_sugar_class"
        ),
    )

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("processing_classification", "UNKNOWN")
        kwargs.setdefault("sugar_classification", "UNKNOWN")
        super().__init__(**kwargs)

    # Relationships
    product_ingredients: Mapped[List["ProductIngredient"]] = relationship(
        "ProductIngredient", back_populates="ingredient"
    )
    rules: Mapped[List["IngredientRule"]] = relationship(
        "IngredientRule",
        back_populates="ingredient",
        cascade="all, delete-orphan"
    )
