"""Regulatory claim rules model for YumSure."""

from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text, Numeric, Boolean, Date, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.db.base import Base
from app.models.claim_ast_schema import validate_ast_structure


class RegulatoryClaimRule(Base):
    """
    FSSAI (Advertising and Claims) Regulations 2018 (Consolidated Version III, 2022).
    
    Defines statutory criteria required to make nutritional and non-addition claims
    under Schedule I, Schedule II (permitted synonyms), and Regulation 6(1).
    Supports compound AST condition expressions with nested AND/OR logic.
    """
    __tablename__ = "regulatory_claim_rules"

    claim_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    claim_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    claim_title: Mapped[str] = mapped_column(String(150), nullable=False)
    claim_family: Mapped[str] = mapped_column(
        String(50),
        default="NUTRIENT_CONTENT_CLAIM",
        nullable=False,
        index=True
    )
    food_form: Mapped[str] = mapped_column(String(20), nullable=False)
    applicable_category: Mapped[str] = mapped_column(String(100), default="ALL", nullable=False)

    # Structured Expression Tree supporting nested AND/OR logic & multi-base rules.
    # Nullable during data onboarding / legacy record transition; engine returns INSUFFICIENT_DATA when null.
    condition_expression: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Schedule II Authorized Synonyms (stored as JSON array of strings)
    permitted_synonyms_schedule_ii: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False
    )

    # Optional scalar columns retained for backward compatibility with simple rules
    operator: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    threshold_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Provenance, Gazettes & Effective Dates
    fssai_regulation_reference: Mapped[str] = mapped_column(Text, nullable=False)
    official_source_version: Mapped[str] = mapped_column(
        String(50),
        default="Version III (04-10-2022)",
        nullable=False
    )
    effective_from: Mapped[date] = mapped_column(
        Date,
        default=date(2019, 7, 1),
        nullable=False
    )
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    consumer_explanation: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "food_form IN ('solid', 'liquid', 'both')",
            name="chk_claim_food_form"
        ),
        CheckConstraint(
            "operator IS NULL OR operator IN ('LT', 'LTE', 'GT', 'GTE', 'EQ')",
            name="chk_claim_operator"
        ),
        CheckConstraint(
            "claim_family IN ('NUTRIENT_CONTENT_CLAIM', 'NON_ADDITION_CLAIM')",
            name="chk_claim_family"
        ),
        Index("idx_rcr_claim_code", "claim_code"),
        Index("idx_rcr_active", "is_active"),
        Index("idx_rcr_family", "claim_family"),
    )

    @validates("condition_expression")
    def validate_condition_expression(self, key: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Validates condition_expression when present.
        If None, safely permits storage (engine returns INSUFFICIENT_DATA).
        """
        if value is not None:
            validated = validate_ast_structure(value, allow_none=False)
            return validated.model_dump()
        return None
