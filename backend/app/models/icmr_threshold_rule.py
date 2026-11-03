"""ICMR-NIN Table 15.1 Nutrient Threshold Rules model for YumSure."""

from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Text, Numeric, Boolean, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IcmrNutrientThresholdRule(Base):
    """
    ICMR-NIN Dietary Guidelines for Indians (DGI) 2024 - Guideline 15, Table 15.1.
    
    Product-level thresholds of concern per 100g (solids) or per 100ml (liquids)
    for Added Sugar, Added Fat, Salt, and Energy.
    
    IMPORTANT STATUTORY DEMARCATION:
    These are public health advisory thresholds and MUST NOT be conflated with
    FSSAI statutory advertising claims or mandatory front-of-pack labelling rules.
    """
    __tablename__ = "icmr_nutrient_threshold_rules"

    rule_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    rule_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    nutrient_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("nutrients.nutrient_code"),
        nullable=False
    )
    food_form: Mapped[str] = mapped_column(String(20), nullable=False)
    threshold_value: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    operator: Mapped[str] = mapped_column(String(10), default="GT", nullable=False)
    measurement_basis: Mapped[str] = mapped_column(String(30), nullable=False)

    guideline_reference: Mapped[str] = mapped_column(
        Text,
        default="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    __table_args__ = (
        CheckConstraint(
            "food_form IN ('solid', 'liquid')",
            name="chk_icmr_thresh_food_form"
        ),
        CheckConstraint(
            "operator IN ('GT', 'GTE')",
            name="chk_icmr_thresh_operator"
        ),
        CheckConstraint(
            "measurement_basis IN ('PER_100G', 'PER_100ML')",
            name="chk_icmr_thresh_basis"
        ),
        Index("idx_icmr_thresh_nutrient", "nutrient_code"),
        Index("idx_icmr_thresh_active", "is_active"),
    )

    # Relationships
    nutrient: Mapped["Nutrient"] = relationship(
        "Nutrient",
        back_populates="icmr_threshold_rules"
    )

