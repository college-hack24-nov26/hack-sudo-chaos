"""
[DEPRECATED] Nutrition interpretation rules model for YumSure.

NOTE FOR DEVELOPERS & ARCHITECTS:
This model and table (`nutrition_interpretation_rules`) are DEPRECATED.
They previously represented an unverified Low/Moderate/High tripartite classification.
Per the Phase 1A & Phase 1B audit, Indian statutory law contains no tripartite thresholds.
This model is superseded by `IcmrHfssRule` (`icmr_hfss_rules`) which strictly models
the ICMR-NIN Dietary Guidelines for Indians 2024 (Tables 15.1 and 15.2) matrix.

This class is retained strictly for backward compatibility and safe migration rollbacks.
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Text, Numeric, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NutritionRule(Base):
    """
    [DEPRECATED]: Superseded by `IcmrHfssRule`. Retained for migration backward compatibility.
    """
    __tablename__ = "nutrition_interpretation_rules"
    __deprecated__ = True

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
