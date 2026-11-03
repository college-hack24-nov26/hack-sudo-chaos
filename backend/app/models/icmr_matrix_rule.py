"""ICMR-NIN Table 15.2 Food Classification Matrix Rules model for YumSure."""

from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Text, Numeric, Boolean, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

ICMR_PROCESSING_GROUPS = ('GROUP_A', 'GROUP_B', 'GROUP_C')
ICMR_NUTRITIONAL_CATEGORIES = ('CAT_1', 'CAT_2', 'CAT_3')
ICMR_MATRIX_CELLS = ('A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3')


class IcmrMatrixRule(Base):
    """
    ICMR-NIN Dietary Guidelines for Indians (DGI) 2024 - Guideline 15, Table 15.2.
    
    Represents the 2D Classification Matrix combining:
    - Dimension 1: Food Processing Extent (Group A: Minimally Processed, Group B: Culinary/Traditional, Group C: Ultra-Processed).
    - Dimension 2: Nutritional Quality (Category 1: Low Calorie / Non-HFSS, Category 2: Moderate Calorie, Category 3: High Calorie).
    
    CRITICAL ARCHITECTURAL DESIGN:
    - This model does NOT depend on a single nutrient foreign key.
    - Preserves independence of UPF processing status and HFSS nutritional status (e.g. Cell C1 = Non-HFSS UPF).
    - Table 15.2 applies strictly to solid foods (applicable_food_form='solid').
    """
    __tablename__ = "icmr_matrix_rules"

    matrix_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    cell_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    processing_group: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    nutritional_category: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    applicable_food_form: Mapped[str] = mapped_column(String(20), default="solid", nullable=False)

    # Independent Dimensions
    is_upf: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_hfss: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Energy density bands for solid foods (Table 15.2)
    energy_min_kcal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    energy_max_kcal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Guideline Text & Consumer Intelligence
    processing_description: Mapped[str] = mapped_column(Text, nullable=False)
    nutritional_description: Mapped[str] = mapped_column(Text, nullable=False)
    consumer_guidance: Mapped[str] = mapped_column(Text, nullable=False)

    guideline_reference: Mapped[str] = mapped_column(
        Text,
        default="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2",
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    __table_args__ = (
        CheckConstraint(
            f"cell_code IN {tuple(ICMR_MATRIX_CELLS)}",
            name="chk_icmr_matrix_cell"
        ),
        CheckConstraint(
            f"processing_group IN {tuple(ICMR_PROCESSING_GROUPS)}",
            name="chk_icmr_matrix_group"
        ),
        CheckConstraint(
            f"nutritional_category IN {tuple(ICMR_NUTRITIONAL_CATEGORIES)}",
            name="chk_icmr_matrix_cat"
        ),
        CheckConstraint(
            "applicable_food_form IN ('solid', 'liquid')",
            name="chk_icmr_matrix_food_form"
        ),
        Index("idx_icmr_matrix_group_cat", "processing_group", "nutritional_category"),
    )

