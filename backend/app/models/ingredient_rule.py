"""Ingredient statutory rules and safety warning model for YumSure."""

from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Text, Numeric, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

INGREDIENT_RULE_TYPES = (
    'MANDATORY_LABEL_WARNING',
    'MAX_PERMISSIBLE_LIMIT',
    'POPULATION_PROHIBITION',
    'SPECIAL_CONDITIONS',
    'WARNING_MANDATE',
    'MAX_LIMIT'
)


class IngredientRule(Base):
    """
    Statutory ingredient rules governing additive safety limits and mandatory label warnings.
    
    Covers:
    - FSSAI Food Safety and Standards (Food Products Standards and Food Additives) Regulations 2011 (GMP limits).
    - FSSAI Labelling and Display Regulations 2020 Schedule II (e.g. Aspartame phenylketonurics warning,
      polyol laxative warning, caffeine warning).
    - Reconciles both foundational rule types ('WARNING_MANDATE', 'MAX_LIMIT') and enhanced contract types.
    """
    __tablename__ = "ingredient_rules"

    rule_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ingredient_code: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("ingredients.ingredient_code", ondelete="CASCADE"),
        nullable=False
    )
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_food_category: Mapped[str] = mapped_column(String(100), default="ALL", nullable=False)
    max_permitted_ppm: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    warning_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    condition_expression: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    regulatory_reference: Mapped[str] = mapped_column(Text, nullable=False)
    consumer_guidance: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint(
            f"rule_type IN {tuple(INGREDIENT_RULE_TYPES)}",
            name="chk_ingredient_rule_type"
        ),
        Index("idx_ir_ingredient", "ingredient_code"),
        Index("idx_ir_type", "rule_type"),
    )

    # Relationships
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="rules")
