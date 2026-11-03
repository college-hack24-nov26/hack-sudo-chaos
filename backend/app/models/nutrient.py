"""Nutrients master catalog model for YumSure."""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Boolean, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Nutrient(Base):
    """
    Standard nutrient definitions aligned with FSSAI 2020 labelling mandates
    and ICMR-NIN 2020/2024 reference values.
    
    Primary key is standard canonical slug (e.g. 'protein', 'added_sugars', 'sodium').
    Holds the standardized 2,000 kcal adult daily reference intake (fssai_standard_daily_rdi)
    mandated for percentage daily contribution calculations on packaged food labels.
    """
    __tablename__ = "nutrients"

    nutrient_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    standard_unit: Mapped[str] = mapped_column(String(20), nullable=False)
    is_fssai_mandatory: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # FSSAI Standard Daily Reference Intake (2,000 kcal adult diet basis)
    fssai_standard_daily_rdi: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    rdi_citation: Mapped[Optional[str]] = mapped_column(
        Text,
        default="FSSAI Labelling and Display Regulations 2020, Reg 5(3)(b)",
        nullable=True
    )

    # [DEPRECATED]: Retained for backward compatibility. Use fssai_standard_daily_rdi for labelling RDI.
    icmr_nin_rda_adult: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Relationships
    product_nutrients: Mapped[List["ProductNutrient"]] = relationship(
        "ProductNutrient", back_populates="nutrient"
    )
    icmr_threshold_rules: Mapped[List["IcmrNutrientThresholdRule"]] = relationship(
        "IcmrNutrientThresholdRule", back_populates="nutrient"
    )
    # Retained for backward compatibility during phased transition
    interpretation_rules: Mapped[List["NutritionRule"]] = relationship(
        "NutritionRule", back_populates="nutrient"
    )
