"""Regulatory claim rules model for YumSure."""

from decimal import Decimal
from sqlalchemy import String, Text, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RegulatoryClaimRule(Base):
    """
    FSSAI (Advertising and Claims) Regulations 2018 - Schedule II conditions.
    Defines statutory criteria required to make nutritional claims (e.g. High Fibre, Source of Protein).
    """
    __tablename__ = "regulatory_claim_rules"

    claim_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    claim_code: Mapped[str] = mapped_column(String(50), nullable=False)
    food_form: Mapped[str] = mapped_column(String(20), nullable=False)
    operator: Mapped[str] = mapped_column(String(10), nullable=False)
    threshold_value: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    fssai_regulation_reference: Mapped[str] = mapped_column(Text, nullable=False)
    consumer_explanation: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint("food_form IN ('solid', 'liquid')", name="chk_claim_food_form"),
        CheckConstraint("operator IN ('LTE', 'GTE', 'EQ')", name="chk_claim_operator"),
    )

