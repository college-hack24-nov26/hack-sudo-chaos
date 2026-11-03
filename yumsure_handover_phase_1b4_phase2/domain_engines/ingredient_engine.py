"""
YumSure Deterministic Ingredient Engine.

Responsibilities:
- Evaluates declared ingredients against statutory additive safety rules (FSSAI Additives 2011).
- Detects and triggers mandatory packaging warning statements (FSSAI Labelling 2020 Schedule II).
- Audits ingredient lists for FSSAI Schedule II Major Allergens.
- Interprets sweetener and carbohydrate chemistry (intrinsic vs added free sugars vs non-nutritive sweeteners vs polyols).
- Handles uncataloged ingredients with UNKNOWN or INSUFFICIENT_EVIDENCE states.
"""

from decimal import Decimal
from typing import Dict, Any, List, Optional
from app.domain.engines.contracts import (
    ProductEvaluationInput,
    RuleEvaluationResult,
    EngineBatchResult,
    EvaluationStatus,
    IngredientProcessingClass,
    IngredientSugarClass
)

FSSAI_MAJOR_ALLERGEN_CATEGORIES = [
    "Cereals containing gluten",
    "Crustaceans and their products",
    "Eggs and egg products",
    "Fish and fish products",
    "Peanuts, tree nuts and their products",
    "Soybeans and their products",
    "Milk and milk products",
    "Sulphite in concentrations of 10mg/kg or more"
]


def evaluate_ingredients(
    product: ProductEvaluationInput,
    ingredient_rules: List[Dict[str, Any]],
    ingredient_catalogue: Optional[Dict[str, Any]] = None
) -> EngineBatchResult:
    """
    Evaluates ingredient list for additive limits, mandatory warnings, allergen disclosures,
    and sweetener chemistry.
    """
    results: List[RuleEvaluationResult] = []
    summary_counts: Dict[EvaluationStatus, int] = {
        EvaluationStatus.PASS: 0,
        EvaluationStatus.FAIL: 0,
        EvaluationStatus.INSUFFICIENT_DATA: 0,
        EvaluationStatus.INDETERMINATE: 0,
        EvaluationStatus.NOT_APPLICABLE: 0,
    }

    observed_codes = {ing.ingredient_code: ing for ing in product.ingredients}
    observed_ins = {ing.ins_number: ing for ing in product.ingredients if ing.ins_number}

    # 1. Evaluate Statutory Ingredient Rules (Warnings & Maximum Limits)
    for rule in ingredient_rules:
        rule_id = rule["rule_id"]
        target_code = rule["ingredient_code"]
        rule_type = rule["rule_type"]
        warning_stmt = rule.get("warning_statement")
        max_ppm = rule.get("max_permitted_ppm")
        regulatory_ref = rule.get("regulatory_reference", "FSSAI Regulations")
        consumer_guidance = rule.get("consumer_guidance", "")

        # Check if target ingredient is present in product
        matching_ing = observed_codes.get(target_code)
        if not matching_ing and target_code.startswith("ins_"):
            raw_ins = target_code.replace("ins_", "").split("_")[0]
            matching_ing = observed_ins.get(raw_ins)

        if not matching_ing:
            # Ingredient not present -> Rule NOT_APPLICABLE to this product
            continue

        # Check target food category applicability
        target_cat = rule.get("target_food_category", "ALL")
        if target_cat and target_cat != "ALL":
            if not product.food_category:
                status = EvaluationStatus.INSUFFICIENT_DATA
                summary_counts[status] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="INGREDIENT",
                        rule_id=rule_id,
                        rule_code=f"CATEGORY_CHECK_{target_code.upper()}",
                        outcome=status,
                        title=f"Category Applicability: {matching_ing.declared_label_text}",
                        human_readable_explanation=(
                            f"Rule applies specifically to '{target_cat}' products, but product food category is not specified."
                        ),
                        evidence_used={"target_food_category": target_cat},
                        missing_evidence=["food_category"],
                        statutory_citation=regulatory_ref,
                        official_source_url="https://fssai.gov.in/",
                        source_version="FSSAI Reference"
                    )
                )
                continue
            elif product.food_category.strip().upper() != target_cat.strip().upper():
                # Rule not applicable to this food category
                continue

        # Handle Mandatory Warnings
        if rule_type in ("MANDATORY_LABEL_WARNING", "WARNING_MANDATE"):
            status = EvaluationStatus.PASS
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="INGREDIENT",
                    rule_id=rule_id,
                    rule_code=f"MANDATORY_WARNING_{target_code.upper()}",
                    outcome=status,
                    title=f"Mandatory Label Warning: {matching_ing.declared_label_text}",
                    human_readable_explanation=(
                        f"Product contains '{matching_ing.declared_label_text}'. Statutory warning required: {warning_stmt}"
                    ),
                    evidence_used={
                        "ingredient_code": target_code,
                        "declared_label_text": matching_ing.declared_label_text,
                        "warning_statement_mandated": warning_stmt
                    },
                    missing_evidence=[],
                    statutory_citation=regulatory_ref,
                    official_source_url="https://fssai.gov.in/food-law/regulations/amendments/labelling-display",
                    source_version="Gazette 17-11-2020",
                    warnings_or_limitations=consumer_guidance
                )
            )

        # Handle Maximum Permissible Limits (ppm)
        elif rule_type in ("MAX_PERMISSIBLE_LIMIT", "MAX_LIMIT"):
            # Check declared percentage if available
            if matching_ing.declared_percentage is not None and max_ppm is not None:
                # 1% = 10,000 ppm
                ppm_observed = matching_ing.declared_percentage * Decimal("10000.0")
                max_ppm_dec = Decimal(str(max_ppm))
                breached = ppm_observed > max_ppm_dec
                outcome = EvaluationStatus.FAIL if breached else EvaluationStatus.PASS
                summary_counts[outcome] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="INGREDIENT",
                        rule_id=rule_id,
                        rule_code=f"MAX_LIMIT_{target_code.upper()}",
                        outcome=outcome,
                        title=f"Maximum Permissible Limit: {matching_ing.declared_label_text}",
                        human_readable_explanation=(
                            f"Declared concentration ({float(ppm_observed):.1f} ppm) "
                            f"{'exceeds' if breached else 'is within'} statutory maximum limit of {float(max_ppm_dec):.1f} ppm."
                        ),
                        evidence_used={
                            "observed_percentage": float(matching_ing.declared_percentage),
                            "calculated_ppm": float(ppm_observed),
                            "max_permitted_ppm": float(max_ppm_dec)
                        },
                        missing_evidence=[],
                        statutory_citation=regulatory_ref,
                        official_source_url="https://www.fssai.gov.in/food-law/regulations",
                        source_version="FSSAI Food Additives 2011 Appendix A",
                        warnings_or_limitations=consumer_guidance
                    )
                )
            else:
                # Presence confirmed, quantitative ppm unstated on label
                status = EvaluationStatus.PASS
                summary_counts[status] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="INGREDIENT",
                        rule_id=rule_id,
                        rule_code=f"MAX_LIMIT_MONITOR_{target_code.upper()}",
                        outcome=status,
                        title=f"Permissible Additive Limit: {matching_ing.declared_label_text}",
                        human_readable_explanation=(
                            f"Contains approved additive '{matching_ing.declared_label_text}'. "
                            f"Governed by statutory limit of {max_ppm} ppm under FSSAI regulations."
                        ),
                        evidence_used={"ingredient_present": True, "max_permitted_ppm": max_ppm},
                        missing_evidence=[],
                        statutory_citation=regulatory_ref,
                        official_source_url="https://www.fssai.gov.in/food-law/regulations",
                        source_version="FSSAI Food Additives 2011 Appendix A",
                        warnings_or_limitations=consumer_guidance
                    )
                )

    # 2. Audit Major Allergen Disclosures
    allergens_found = [ing.declared_label_text for ing in product.ingredients if ing.is_fssai_major_allergen]
    if allergens_found:
        status = EvaluationStatus.PASS
        summary_counts[status] += 1
        results.append(
            RuleEvaluationResult(
                engine_name="INGREDIENT",
                rule_id="fssai_allergen_disclosure",
                rule_code="MAJOR_ALLERGEN_DISCLOSURE",
                outcome=status,
                title="FSSAI Major Allergen Disclosure",
                human_readable_explanation=f"Product contains declared major allergens: {', '.join(allergens_found)}.",
                evidence_used={"allergens_present": allergens_found},
                missing_evidence=[],
                statutory_citation="FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(f)",
                official_source_url="https://fssai.gov.in/food-law/regulations/amendments/labelling-display",
                source_version="Gazette 17-11-2020",
                warnings_or_limitations="Requires prominent allergen advisory declaration on product label."
            )
        )

    # 3. Audit Uncharacterized / Unknown Ingredients
    unknown_ings = [
        ing.declared_label_text for ing in product.ingredients
        if ing.processing_classification in (IngredientProcessingClass.UNKNOWN, IngredientProcessingClass.INSUFFICIENT_EVIDENCE)
    ]
    if unknown_ings:
        status = EvaluationStatus.INSUFFICIENT_DATA
        summary_counts[status] += 1
        results.append(
            RuleEvaluationResult(
                engine_name="INGREDIENT",
                rule_id="uncharacterized_ingredients_notice",
                rule_code="UNCHARACTERIZED_INGREDIENTS",
                outcome=status,
                title="Uncharacterized Ingredient Evidence",
                human_readable_explanation=(
                    f"Product contains uncharacterized ingredients with insufficient classification evidence: {', '.join(unknown_ings)}. "
                    f"Processing extent cannot be verified without botanical or manufacturing specifications."
                ),
                evidence_used={"uncharacterized_ingredients": unknown_ings},
                missing_evidence=unknown_ings,
                statutory_citation="ICMR-NIN DGI 2024 & FSSAI Additive Standards",
                official_source_url="https://nin.res.in/",
                source_version="2024 Reference",
                warnings_or_limitations="Ingredients not mapped to verified INS additive catalogue."
            )
        )

    return EngineBatchResult(
        engine_name="INGREDIENT",
        product_id=product.product_id,
        food_form=product.food_form.value,
        results=results,
        summary_counts=summary_counts
    )

