"""
YumSure Deterministic Nutrition Engine.

Responsibilities:
- Nutrient-specific interpretation against official statutory reference values.
- Evaluates FSSAI 2,000 kcal Standard Adult Daily Reference Intakes (Reg 5(3)(b)).
- Calculates percentage daily contribution per serving and per 100g/ml.
- Handles solid vs liquid measurement bases.
- Detects missing mandatory FSSAI 2020 nutrient declarations (INSUFFICIENT_DATA).
- STRICT PROHIBITION: Never produces an aggregate product health score or traffic light rating.
"""

from decimal import Decimal
from typing import Dict, Any, List, Optional
from app.engines.contracts import (
    ProductEvaluationInput,
    RuleEvaluationResult,
    EngineBatchResult,
    EvaluationStatus,
    NutrientDataStatus
)

# FSSAI Standard Adult Daily Reference Values (2,000 kcal diet reference)
# Source: FSSAI (Labelling and Display) Regulations, 2020, Reg 5(3)(b)
FSSAI_STANDARD_DAILY_RDI: Dict[str, Dict[str, Any]] = {
    "energy": {"value": Decimal("2000.0"), "unit": "kcal", "display_name": "Energy"},
    "protein": {"value": Decimal("54.0"), "unit": "g", "display_name": "Protein"},
    "carbohydrates": {"value": Decimal("300.0"), "unit": "g", "display_name": "Carbohydrates"},
    "added_sugars": {"value": Decimal("50.0"), "unit": "g", "display_name": "Added Sugars"},
    "total_fat": {"value": Decimal("67.0"), "unit": "g", "display_name": "Total Fat"},
    "saturated_fat": {"value": Decimal("22.0"), "unit": "g", "display_name": "Saturated Fat"},
    "trans_fat": {"value": Decimal("2.0"), "unit": "g", "display_name": "Trans Fat"},
    "sodium": {"value": Decimal("2000.0"), "unit": "mg", "display_name": "Sodium"},
    "dietary_fibre": {"value": Decimal("30.0"), "unit": "g", "display_name": "Dietary Fibre"}
}

FSSAI_MANDATORY_NUTRIENTS = [
    "energy", "protein", "carbohydrates", "total_sugars",
    "added_sugars", "total_fat", "saturated_fat", "trans_fat", "sodium"
]


def evaluate_nutrition(
    product: ProductEvaluationInput,
    custom_reference_catalogue: Optional[Dict[str, Any]] = None
) -> EngineBatchResult:
    """
    Evaluates product nutrient declarations against FSSAI standard reference values.
    Returns per-nutrient daily contribution percentages and missing-declaration notices.
    """
    reference_rdi = custom_reference_catalogue or FSSAI_STANDARD_DAILY_RDI
    results: List[RuleEvaluationResult] = []
    summary_counts: Dict[EvaluationStatus, int] = {
        EvaluationStatus.PASS: 0,
        EvaluationStatus.FAIL: 0,
        EvaluationStatus.INSUFFICIENT_DATA: 0,
        EvaluationStatus.INDETERMINATE: 0,
        EvaluationStatus.NOT_APPLICABLE: 0,
    }

    # 1. Audit Mandatory FSSAI 2020 Nutrient Declarations
    for nutrient_code in FSSAI_MANDATORY_NUTRIENTS:
        obs = product.nutrients.get(nutrient_code)
        ref = reference_rdi.get(nutrient_code)
        display_name = ref["display_name"] if ref else nutrient_code.replace("_", " ").title()

        if not obs or obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
            status = EvaluationStatus.INSUFFICIENT_DATA
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="NUTRITION",
                    rule_id=f"fssai_mandatory_{nutrient_code}",
                    rule_code=f"MANDATORY_DECLARATION_{nutrient_code.upper()}",
                    outcome=status,
                    title=f"Mandatory Declaration: {display_name}",
                    human_readable_explanation=(
                        f"Mandatory nutrient declaration for '{display_name}' is missing or unreadable "
                        f"on the product label."
                    ),
                    evidence_used={"declared_status": obs.data_status.value if obs else "ABSENT"},
                    missing_evidence=[nutrient_code],
                    statutory_citation="FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)",
                    official_source_url="https://fssai.gov.in/food-law/regulations/amendments/labelling-display",
                    source_version="Gazette 17-11-2020",
                    warnings_or_limitations="Mandatory for all packaged food products under Indian law."
                )
            )
            continue

        # If reference RDI exists and value is present, calculate % contribution
        if ref and obs.per_100g_value is not None:
            rdi_val = ref["value"]
            val_100 = obs.per_100g_value
            pct_100 = (val_100 / rdi_val) * Decimal("100.0")

            evidence: Dict[str, Any] = {
                "per_100_value": float(val_100),
                "standard_daily_rdi": float(rdi_val),
                "unit": obs.unit,
                "pct_rdi_per_100": round(float(pct_100), 2)
            }

            serving_text = ""
            if obs.per_serving_value is not None:
                val_serv = obs.per_serving_value
                pct_serv = (val_serv / rdi_val) * Decimal("100.0")
                evidence["per_serving_value"] = float(val_serv)
                evidence["pct_rdi_per_serving"] = round(float(pct_serv), 2)
                serving_text = f" One serving provides {float(val_serv):.2f}{obs.unit} ({evidence['pct_rdi_per_serving']}% of adult daily RDI)."

            status = EvaluationStatus.PASS
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="NUTRITION",
                    rule_id=f"fssai_rdi_contrib_{nutrient_code}",
                    rule_code=f"RDI_CONTRIBUTION_{nutrient_code.upper()}",
                    outcome=status,
                    title=f"{display_name} Daily Contribution",
                    human_readable_explanation=(
                        f"100{'g' if product.food_form.value == 'solid' else 'ml'} provides {float(val_100):.2f}{obs.unit} "
                        f"of {display_name}, contributing {evidence['pct_rdi_per_100']}% of the FSSAI standard adult daily reference intake ({float(rdi_val):.1f}{ref['unit']})."
                        f"{serving_text}"
                    ),
                    evidence_used=evidence,
                    missing_evidence=[],
                    statutory_citation="FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)",
                    official_source_url="https://fssai.gov.in/food-law/regulations/amendments/labelling-display",
                    source_version="Gazette 17-11-2020",
                    warnings_or_limitations="Calculated against 2,000 kcal standard adult daily intake reference."
                )
            )

    return EngineBatchResult(
        engine_name="NUTRITION",
        product_id=product.product_id,
        food_form=product.food_form.value,
        results=results,
        summary_counts=summary_counts
    )

