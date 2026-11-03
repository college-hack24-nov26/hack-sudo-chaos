"""
Ingredient rules model for YumSure.

NOTE FOR COORDINATION WITH ABHISHEK:
In DATABASE_DESIGN.md, category classifications and FSSAI allergen flags are
stored directly within the `ingredients` table. This model provides an extensible
entity for statutory additive thresholds, maximum permissible limits (GMP), and
special labelling warning mandates (e.g., Aspartame PKU warnings under FSSAI 2020).
"""

from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IngredientRule(Base):
    """
    Statutory ingredient rules governing additive limits and mandatory label warnings.
    Awaiting final schema confirmation with Abhishek before locking migration.
    """
    __tablename__ = "ingredient_rules"

    rule_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ingredient_code: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("ingredients.ingredient_code"),
        nullable=False
    )
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'WARNING_MANDATE', 'MAX_LIMIT'
    condition_expression: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    regulatory_reference: Mapped[str] = mapped_column(Text, nullable=False)
    consumer_guidance: Mapped[str] = mapped_column(Text, nullable=False)

