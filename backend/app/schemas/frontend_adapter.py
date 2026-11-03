"""
Frontend Data Adapter for YumSure Mobile & Web Clients.

Maps deterministic engine batch results, nutrient observations, and ingredient
breakdowns into the exact JSON schema expected by the Flutter client:
- ProductIdentity
- NutritionalInterpretation
- RegulatoryClaimsValidation
- IngredientAnalysis
- KeyFindingItem
- AiExplanation
"""

from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.domain.engines.contracts import (
    ProductEvaluationInput,
    NutrientObservationInput,
    IngredientObservationInput,
    EngineBatchResult,
    EvaluationStatus,
    FoodForm,
    NutrientDataStatus,
)


class NutrientItemModel(BaseModel):
    nutrient_code: str
    display_name: str
    value_per_100g: Optional[float] = None
    value_per_serving: Optional[float] = None
    unit: str = "g"
    rda_percentage: Optional[float] = None
    classification: Optional[str] = None  # 'Low', 'Moderate', 'High', 'Not classifiable', 'Insufficient data'
    concern_level: Optional[str] = None  # 'POSITIVE', 'NEUTRAL', 'CONCERN'
    status: str = "PRESENT"  # 'PRESENT', 'EXPLICITLY_ZERO', 'NOT_DECLARED', 'UNKNOWN'
    explanation: Optional[str] = None
    low_threshold_max: Optional[float] = None
    moderate_threshold_max: Optional[float] = None
    high_threshold_min: Optional[float] = None


class NutritionalInterpretationModel(BaseModel):
    basis: str = "per_100g"
    reference_standard: str = "ICMR-NIN 2020 RDA & FSSAI 2020"
    nutrients: List[NutrientItemModel] = Field(default_factory=list)


class RegulatoryClaimItemModel(BaseModel):
    claim_code: str
    claim_name: str
    status: str  # 'COMPLIANT', 'NOT_COMPLIANT', 'INSUFFICIENT_DATA', 'NOT_EVALUATED'
    actual_value: Optional[float] = None
    required_threshold: Optional[float] = None
    unit: Optional[str] = None
    regulatory_reference: Optional[str] = None
    explanation: Optional[str] = None


class RegulatoryClaimsValidationModel(BaseModel):
    applicable_regulation: str = "FSSAI (Advertising and Claims) Regulations, 2018 - Schedule II"
    is_fssai_compliant: Optional[bool] = None
    claims: List[RegulatoryClaimItemModel] = Field(default_factory=list)


class IngredientCategoryModel(BaseModel):
    category: str
    category_name: str
    count: int = 0
    items: List[str] = Field(default_factory=list)


class IngredientAnalysisModel(BaseModel):
    total_ingredients_count: int = 0
    ingredients_summary: Optional[str] = None
    declared_allergens: List[str] = Field(default_factory=list)
    may_contain_allergens: List[str] = Field(default_factory=list)
    categories: List[IngredientCategoryModel] = Field(default_factory=list)


class KeyFindingItemModel(BaseModel):
    nutrient_code: str
    title: str
    value_text: str
    severity: str  # 'HIGH', 'MODERATE', 'POSITIVE'
    explanation: Optional[str] = None


class AiExplanationModel(BaseModel):
    provider: Optional[str] = "local_deterministic_explainer"
    is_fallback: bool = True
    text: str


# Display names for canonical nutrients
NUTRIENT_DISPLAY_NAMES = {
    "energy": "Energy",
    "protein": "Protein",
    "carbohydrates": "Carbohydrates",
    "total_sugars": "Total Sugars",
    "added_sugars": "Added Sugars",
    "total_fat": "Total Fat",
    "saturated_fat": "Saturated Fat",
    "trans_fat": "Trans Fat",
    "sodium": "Sodium",
    "dietary_fibre": "Dietary Fibre",
}

# Standard statutory thresholds for threshold bars (per 100g)
NUTRIENT_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "added_sugars": {"low_max": 5.0, "mod_max": 10.0, "high_min": 10.0},
    "total_fat": {"low_max": 3.0, "mod_max": 17.5, "high_min": 17.5},
    "saturated_fat": {"low_max": 1.5, "mod_max": 5.0, "high_min": 5.0},
    "sodium": {"low_max": 120.0, "mod_max": 600.0, "high_min": 600.0},
    "protein": {"low_max": 5.0, "mod_max": 10.0, "high_min": 10.0},
    "dietary_fibre": {"low_max": 3.0, "mod_max": 6.0, "high_min": 6.0},
}


def build_frontend_sections(
    domain_product: ProductEvaluationInput,
    nutrition_eval: Optional[EngineBatchResult],
    icmr_eval: Optional[EngineBatchResult],
    claims_eval: Optional[EngineBatchResult],
    ingredient_eval: Optional[EngineBatchResult],
    include_ai_explanation: bool = True,
) -> Dict[str, Any]:
    """
    Transforms deterministic engine evaluation batches and domain product
    into Flutter-compatible section models.
    """
    # 1. Build Nutritional Interpretation
    basis_str = "per_100ml" if domain_product.food_form == FoodForm.LIQUID else "per_100g"
    nutrients_list: List[NutrientItemModel] = []

    # Map daily value % from nutrition_eval results
    rdi_percentages: Dict[str, float] = {}
    if nutrition_eval and nutrition_eval.results:
        for r in nutrition_eval.results:
            if "pct_daily_value" in r.evidence_used:
                code = r.evidence_used.get("nutrient") or r.rule_id.replace("fssai_daily_val_", "")
                try:
                    rdi_percentages[code] = float(r.evidence_used["pct_daily_value"])
                except (ValueError, TypeError):
                    pass

    # Map ICMR HFSS breaches
    icmr_breaches: Dict[str, bool] = {}
    if icmr_eval and icmr_eval.results:
        for r in icmr_eval.results:
            if r.outcome == EvaluationStatus.FAIL:
                for k in ("added_sugar", "added_sugars", "sodium", "added_fat", "saturated_fat", "energy"):
                    if k in r.rule_id or k in r.rule_code.lower():
                        icmr_breaches[k] = True

    for slug, obs in domain_product.nutrients.items():
        disp_name = NUTRIENT_DISPLAY_NAMES.get(slug, slug.replace("_", " ").title())
        val_100 = float(obs.per_100g_value) if obs.per_100g_value is not None else None
        val_serving = float(obs.per_serving_value) if obs.per_serving_value is not None else None
        rda_pct = rdi_percentages.get(slug)

        # Classification and concern level
        classification = "Moderate"
        concern = "NEUTRAL"

        if obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
            classification = "Insufficient data"
            concern = "NEUTRAL"
        elif slug in ("added_sugars", "sodium", "saturated_fat", "trans_fat"):
            if icmr_breaches.get(slug) or (val_100 is not None and val_100 > NUTRIENT_THRESHOLDS.get(slug, {}).get("high_min", 999)):
                classification = "High"
                concern = "CONCERN"
            elif val_100 is not None and val_100 <= NUTRIENT_THRESHOLDS.get(slug, {}).get("low_max", 0):
                classification = "Low"
                concern = "POSITIVE"
            else:
                classification = "Moderate"
                concern = "NEUTRAL"
        elif slug in ("protein", "dietary_fibre"):
            if val_100 is not None and val_100 >= NUTRIENT_THRESHOLDS.get(slug, {}).get("high_min", 10):
                classification = "High"
                concern = "POSITIVE"
            elif val_100 is not None and val_100 >= NUTRIENT_THRESHOLDS.get(slug, {}).get("low_max", 3):
                classification = "Moderate"
                concern = "POSITIVE"
            else:
                classification = "Low"
                concern = "NEUTRAL"

        thresh = NUTRIENT_THRESHOLDS.get(slug, {})

        nutrients_list.append(
            NutrientItemModel(
                nutrient_code=slug,
                display_name=disp_name,
                value_per_100g=val_100,
                value_per_serving=val_serving,
                unit=obs.unit,
                rda_percentage=round(rda_pct, 1) if rda_pct is not None else None,
                classification=classification,
                concern_level=concern,
                status=obs.data_status.value,
                explanation=f"{disp_name} declaration per {basis_str}.",
                low_threshold_max=thresh.get("low_max"),
                moderate_threshold_max=thresh.get("mod_max"),
                high_threshold_min=thresh.get("high_min"),
            )
        )

    nutritional_interpretation = NutritionalInterpretationModel(
        basis=basis_str,
        reference_standard="ICMR-NIN 2020 RDA & FSSAI 2020",
        nutrients=nutrients_list,
    )

    # 2. Build Regulatory Claims Validation
    claims_list: List[RegulatoryClaimItemModel] = []
    has_claim_fail = False
    has_claim_pass = False

    if claims_eval and claims_eval.results:
        for r in claims_eval.results:
            # Map EvaluationStatus to Flutter status
            if r.outcome == EvaluationStatus.PASS:
                status_str = "COMPLIANT"
                has_claim_pass = True
            elif r.outcome == EvaluationStatus.FAIL:
                status_str = "NOT_COMPLIANT"
                has_claim_fail = True
            elif r.outcome == EvaluationStatus.INSUFFICIENT_DATA:
                status_str = "INSUFFICIENT_DATA"
            else:
                status_str = "NOT_EVALUATED"

            obs_val = r.evidence_used.get("observed_value")
            req_thresh = r.evidence_used.get("threshold_value")
            unit_str = r.evidence_used.get("unit") or "g"

            claims_list.append(
                RegulatoryClaimItemModel(
                    claim_code=r.rule_code,
                    claim_name=r.title,
                    status=status_str,
                    actual_value=float(obs_val) if obs_val is not None else None,
                    required_threshold=float(req_thresh) if req_thresh is not None else None,
                    unit=unit_str,
                    regulatory_reference=r.statutory_citation,
                    explanation=r.human_readable_explanation,
                )
            )

    is_compliant = None
    if has_claim_fail:
        is_compliant = False
    elif has_claim_pass:
        is_compliant = True

    regulatory_claims_validation = RegulatoryClaimsValidationModel(
        applicable_regulation="FSSAI (Advertising and Claims) Regulations, 2018 - Schedule II",
        is_fssai_compliant=is_compliant,
        claims=claims_list,
    )

    # 3. Build Ingredient Analysis
    declared_allergens: List[str] = []
    refined_carbs: List[str] = []
    fats_oils: List[str] = []
    sweeteners: List[str] = []
    additives: List[str] = []
    whole_foods: List[str] = []

    for ing in domain_product.ingredients:
        text = ing.declared_label_text
        code_lower = ing.ingredient_code.lower()
        text_lower = text.lower()

        # Allergen detection
        if ing.is_fssai_major_allergen:
            declared_allergens.append(text)
        elif any(a in text_lower for a in ("wheat", "milk", "gluten", "soya", "peanut", "egg", "fish", "almond", "cashew")):
            declared_allergens.append(text)

        # Categorization
        if ing.ins_number or "ins" in text_lower or any(k in text_lower for k in ("preservative", "emulsifier", "acidity regulator", "color", "flavor")):
            additives.append(text)
        elif any(k in text_lower for k in ("sugar", "syrup", "glucose", "fructose", "sucrose", "dextrose", "jaggery", "honey")):
            sweeteners.append(text)
        elif any(k in text_lower for k in ("oil", "fat", "butter", "ghee", "margarine", "shortening")):
            fats_oils.append(text)
        elif any(k in text_lower for k in ("maida", "flour", "starch", "maltodextrin", "semolina", "suji")):
            refined_carbs.append(text)
        else:
            whole_foods.append(text)

    # De-duplicate allergens
    unique_allergens = list(dict.fromkeys(declared_allergens))

    categories_list: List[IngredientCategoryModel] = []
    if refined_carbs:
        categories_list.append(IngredientCategoryModel(category="REFINED_CARBS", category_name="Refined Grains & Flours", count=len(refined_carbs), items=refined_carbs))
    if fats_oils:
        categories_list.append(IngredientCategoryModel(category="FATS_OILS", category_name="Fats & Vegetable Oils", count=len(fats_oils), items=fats_oils))
    if sweeteners:
        categories_list.append(IngredientCategoryModel(category="SWEETENERS", category_name="Added Sugars & Sweeteners", count=len(sweeteners), items=sweeteners))
    if additives:
        categories_list.append(IngredientCategoryModel(category="ADDITIVES", category_name="Food Additives & Preservatives", count=len(additives), items=additives))
    if whole_foods:
        categories_list.append(IngredientCategoryModel(category="WHOLE_FOODS", category_name="Whole Foods & Pulses", count=len(whole_foods), items=whole_foods))

    ingredients_summary = ", ".join(ing.declared_label_text for ing in domain_product.ingredients) if domain_product.ingredients else None

    ingredient_analysis = IngredientAnalysisModel(
        total_ingredients_count=len(domain_product.ingredients),
        ingredients_summary=ingredients_summary,
        declared_allergens=unique_allergens,
        may_contain_allergens=[],
        categories=categories_list,
    )

    # 4. Build Key Findings (3-4 top consumer insights)
    key_findings: List[KeyFindingItemModel] = []

    # Check Added Sugar
    obs_sugar = domain_product.nutrients.get("added_sugars") or domain_product.nutrients.get("total_sugars")
    if obs_sugar and obs_sugar.per_100g_value is not None:
        sugar_val = float(obs_sugar.per_100g_value)
        if sugar_val > 10.0:
            key_findings.append(
                KeyFindingItemModel(
                    nutrient_code="added_sugars",
                    title="High Added Sugar",
                    value_text=f"{sugar_val:.1f}g per 100g",
                    severity="HIGH",
                    explanation="Exceeds the ICMR dietary threshold of concern (10g/100g).",
                )
            )
        elif sugar_val == 0.0:
            key_findings.append(
                KeyFindingItemModel(
                    nutrient_code="added_sugars",
                    title="Zero Added Sugar",
                    value_text="0g per 100g",
                    severity="POSITIVE",
                    explanation="Contains no declared added sugar.",
                )
            )

    # Check Sodium
    obs_sod = domain_product.nutrients.get("sodium")
    if obs_sod and obs_sod.per_100g_value is not None:
        sod_val = float(obs_sod.per_100g_value)
        if sod_val > 600.0:
            key_findings.append(
                KeyFindingItemModel(
                    nutrient_code="sodium",
                    title="High Sodium / Salt",
                    value_text=f"{sod_val:.0f}mg per 100g",
                    severity="HIGH",
                    explanation="High sodium content exceeding ICMR threshold (600mg/100g).",
                )
            )

    # Check Trans Fat
    obs_trans = domain_product.nutrients.get("trans_fat")
    if obs_trans and obs_trans.per_100g_value is not None:
        trans_val = float(obs_trans.per_100g_value)
        if trans_val == 0.0 or trans_val <= 0.2:
            key_findings.append(
                KeyFindingItemModel(
                    nutrient_code="trans_fat",
                    title="Trans Fat Free",
                    value_text=f"{trans_val:.1f}g per 100g",
                    severity="POSITIVE",
                    explanation="Complies with FSSAI regulations for trans-fat free declaration (<= 0.2g).",
                )
            )

    # Check Protein
    obs_prot = domain_product.nutrients.get("protein")
    if obs_prot and obs_prot.per_100g_value is not None:
        prot_val = float(obs_prot.per_100g_value)
        if prot_val >= 10.0:
            key_findings.append(
                KeyFindingItemModel(
                    nutrient_code="protein",
                    title="High Protein",
                    value_text=f"{prot_val:.1f}g per 100g",
                    severity="POSITIVE",
                    explanation="Rich in protein fulfilling statutory criteria for High Protein.",
                )
            )
        elif prot_val >= 5.4:
            key_findings.append(
                KeyFindingItemModel(
                    nutrient_code="protein",
                    title="Source of Protein",
                    value_text=f"{prot_val:.1f}g per 100g",
                    severity="POSITIVE",
                    explanation="Fulfills FSSAI 10% daily adult RDA requirement (5.4g).",
                )
            )

    # Check Allergens
    if unique_allergens:
        key_findings.append(
            KeyFindingItemModel(
                nutrient_code="allergens",
                title="Declared Allergens",
                value_text=", ".join(unique_allergens[:2]),
                severity="HIGH" if len(unique_allergens) > 1 else "MODERATE",
                explanation=f"Contains declared allergens: {', '.join(unique_allergens)}.",
            )
        )

    # 5. Build AI Explanation (Deterministic Fallback)
    ai_explanation: Optional[AiExplanationModel] = None
    if include_ai_explanation:
        summary_sentences: List[str] = []
        name_str = domain_product.product_name or "This product"
        summary_sentences.append(f"{name_str} provides nutritional facts evaluated under Indian regulatory frameworks.")

        if obs_prot and obs_prot.per_100g_value:
            summary_sentences.append(f"It contains {float(obs_prot.per_100g_value):.1f}g of protein per 100g.")
        if obs_sugar and obs_sugar.per_100g_value:
            s_val = float(obs_sugar.per_100g_value)
            if s_val > 10.0:
                summary_sentences.append(f"Added sugar content is elevated at {s_val:.1f}g/100g, exceeding the ICMR dietary threshold.")
            else:
                summary_sentences.append(f"Sugar content is within moderate dietary thresholds at {s_val:.1f}g/100g.")

        if unique_allergens:
            summary_sentences.append(f"Declared allergens to note: {', '.join(unique_allergens)}.")

        ai_explanation = AiExplanationModel(
            provider="local_deterministic_explainer",
            is_fallback=True,
            text=" ".join(summary_sentences),
        )

    return {
        "nutritional_interpretation": nutritional_interpretation,
        "regulatory_claims_validation": regulatory_claims_validation,
        "ingredient_analysis": ingredient_analysis,
        "key_findings": key_findings,
        "ai_explanation": ai_explanation,
    }
