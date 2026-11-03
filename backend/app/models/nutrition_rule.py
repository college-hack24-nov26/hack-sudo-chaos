"""Nutrition interpretation rules model for YumSure."""

from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Text, Numeric, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NutritionRule(Base):
    """
    Statutory ICMR-NIN 2020 / FSSAI thresholds for evaluating nutrient densities.
    Defines Low, Moderate, and High boundaries per 100g/ml for solids and liquids.
    """
    __tablename__ = "nutrition_interpretation_rules"

    rule_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    nutrient_code: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("nutrients.nutrient_code"),
        nullable=False
    )
    food_form: Mapped[str] = mapped_column(String(20), nullable=False)
    low_threshold_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    moderate_threshold_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    high_threshold_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    concern_level: Mapped[str] = mapped_column(String(20), nullable=False)
    regulatory_citation: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint("food_form IN ('solid', 'liquid')", name="chk_nir_food_form"),
        CheckConstraint(
            "concern_level IN ('POSITIVE', 'NEUTRAL', 'CONCERN')",
            name="chk_nir_concern_level"
        ),
    )

    # Relationships
    nutrient: Mapped["Nutrient"] = relationship("Nutrient", back_populates="interpretation_rules")

