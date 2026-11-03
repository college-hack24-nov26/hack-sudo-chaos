"""Nutrients master catalog model for YumSure."""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Nutrient(Base):
    """
    Standard nutrient definitions aligned with ICMR-NIN 2020 and FSSAI 2020 labelling mandates.
    Primary key is standard canonical slug (e.g. 'protein', 'added_sugars', 'sodium').
    """
    __tablename__ = "nutrients"

    nutrient_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    standard_unit: Mapped[str] = mapped_column(String(20), nullable=False)
    is_fssai_mandatory: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    icmr_nin_rda_adult: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Relationships
    product_nutrients: Mapped[List["ProductNutrient"]] = relationship(
        "ProductNutrient", back_populates="nutrient"
    )
    interpretation_rules: Mapped[List["NutritionRule"]] = relationship(
        "NutritionRule", back_populates="nutrient"
    )

