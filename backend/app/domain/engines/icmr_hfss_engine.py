"""
YumSure Deterministic ICMR-NIN HFSS Engine.

Responsibilities:
- Evaluates ICMR-NIN Dietary Guidelines for Indians (DGI) 2024, Guideline 15.
- Evaluates Table 15.1 Thresholds of Concern for Added Sugar, Added Fat, Salt, and Energy.
- Evaluates Table 15.2 2D Matrix (Groups A, B, C x Categories 1, 2, 3).
- Strictly preserves UPF processing extent vs HFSS calorific density independence (Cell C1 = Non-HFSS UPF).
- Table 15.2 matrix evaluates as NOT_APPLICABLE for liquid beverages (solid foods only per guideline).
- Strictly NEVER infers added fat from total fat (returns INSUFFICIENT_DATA).
- Emits INDETERMINATE when ingredient evidence is ambiguous between Group B and Group C.
"""

from decimal import Decimal
from typing import Dict, Any, List, Optional
from app.domain.engines.contracts import (
    ProductEvaluationInput,
    RuleEvaluationResult,
    EngineBatchResult,
    EvaluationStatus,
    NutrientDataStatus,
    IngredientProcessingClass,
    MeasurementBasis,
)


def evaluate_icmr_hfss(
    product: ProductEvaluationInput,
    threshold_rules: List[Dict[str, Any]],
    matrix_rules: List[Dict[str, Any]]
) -> EngineBatchResult:
    """
    Evaluates product against ICMR-NIN DGI 2024 Guideline 15 (Tables 15.1 and 15.2).
    """
    results: List[RuleEvaluationResult] = []
    summary_counts: Dict[EvaluationStatus, int] = {
        EvaluationStatus.PASS: 0,
        EvaluationStatus.FAIL: 0,
        EvaluationStatus.INSUFFICIENT_DATA: 0,
        EvaluationStatus.INDETERMINATE: 0,
        EvaluationStatus.NOT_APPLICABLE: 0,
    }

    # =========================================================================
    # Part 1: Table 15.1 Nutrient Thresholds of Concern
    # =========================================================================
    for rule in threshold_rules:
        rule_id = rule["rule_id"]
        rule_code = rule["rule_code"]
        nutrient_code = rule["nutrient_code"]
        rule_food_form = rule.get("food_form", "solid")
        threshold = Decimal(str(rule["threshold_value"]))

        # Check solid vs liquid applicability
        if rule_food_form not in ("both", "any", product.food_form.value):
            continue

        # Determine permitted measurement bases from the applicable rule:
        # Measurement basis is determined from the applicable rule definition, not inferred from food form.
        permitted_bases: List[MeasurementBasis] = []
        if "permitted_measurement_bases" in rule and rule["permitted_measurement_bases"]:
            for b in rule["permitted_measurement_bases"]:
                permitted_bases.append(b if isinstance(b, MeasurementBasis) else MeasurementBasis(b))
        elif "measurement_basis" in rule and rule["measurement_basis"]:
            mb = rule["measurement_basis"]
            if isinstance(mb, list):
                for b in mb:
                    permitted_bases.append(b if isinstance(b, MeasurementBasis) else MeasurementBasis(b))
            else:
                permitted_bases.append(mb if isinstance(mb, MeasurementBasis) else MeasurementBasis(mb))
        else:
            permitted_bases.append(
                MeasurementBasis.PER_100G
                if rule_food_form == "solid"
                else MeasurementBasis.PER_100ML
            )
        permitted_str = ", ".join(b.value for b in permitted_bases)

        # Handle Salt vs Sodium mapping
        if nutrient_code == "sodium":
            obs = product.nutrients.get("sodium")
            if not obs or obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
                status = EvaluationStatus.INSUFFICIENT_DATA
                summary_counts[status] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="ICMR_HFSS",
                        rule_id=rule_id,
                        rule_code=rule_code,
                        outcome=status,
                        title="ICMR Salt Threshold of Concern",
                        human_readable_explanation="Sodium declaration is missing; cannot evaluate salt threshold of concern.",
                        evidence_used={},
                        missing_evidence=["sodium"],
                        statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                        official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                        source_version="May 2024"
                    )
                )
                continue

            if obs.per_100g_value is None:
                status = EvaluationStatus.INSUFFICIENT_DATA
                summary_counts[status] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="ICMR_HFSS",
                        rule_id=rule_id,
                        rule_code=rule_code,
                        outcome=status,
                        title="ICMR Salt Threshold of Concern",
                        human_readable_explanation="Sodium declared numeric value is missing (null); cannot evaluate salt threshold.",
                        evidence_used={},
                        missing_evidence=["sodium"],
                        statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                        official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                        source_version="May 2024"
                    )
                )
                continue

            if obs.measurement_basis is None or obs.measurement_basis not in permitted_bases:
                status = EvaluationStatus.INSUFFICIENT_DATA
                summary_counts[status] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="ICMR_HFSS",
                        rule_id=rule_id,
                        rule_code=rule_code,
                        outcome=status,
                        title="ICMR Salt Threshold of Concern",
                        human_readable_explanation=(
                            f"Sodium measurement basis is "
                            f"{'unresolved (None)' if obs.measurement_basis is None else f'incompatible ({obs.measurement_basis.value})'}; "
                            f"rule requires '{permitted_str}'. Cannot evaluate salt threshold of concern."
                        ),
                        evidence_used={"measurement_basis": obs.measurement_basis.value if obs.measurement_basis else None},
                        missing_evidence=["sodium_measurement_basis"],
                        statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                        official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                        source_version="May 2024"
                    )
                )
                continue

            sodium_mg = obs.per_100g_value
            salt_mg = sodium_mg * Decimal("2.5")  # Conversion factor: Salt (mg) = Sodium (mg) * 2.5
            breached = salt_mg > threshold
            outcome = EvaluationStatus.FAIL if breached else EvaluationStatus.PASS
            summary_counts[outcome] += 1
            basis_unit = "g" if obs.measurement_basis == MeasurementBasis.PER_100G else "ml"
            results.append(
                RuleEvaluationResult(
                    engine_name="ICMR_HFSS",
                    rule_id=rule_id,
                    rule_code=rule_code,
                    outcome=outcome,
                    title="ICMR Salt Threshold of Concern",
                    human_readable_explanation=(
                        f"Salt content is {float(salt_mg):.1f}mg/100{basis_unit} "
                        f"({float(sodium_mg):.1f}mg sodium * 2.5), {'exceeding' if breached else 'within'} the "
                        f"ICMR threshold of concern ({float(threshold):.1f}mg)."
                    ),
                    evidence_used={
                        "sodium_mg": float(sodium_mg),
                        "salt_calculated_mg": float(salt_mg),
                        "threshold_mg": float(threshold)
                    },
                    missing_evidence=[],
                    statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                    official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                    source_version="May 2024"
                )
            )
            continue

        # Handle Added Fat: NEVER INFER FROM TOTAL FAT!
        if nutrient_code == "added_fat":
            obs = product.nutrients.get("added_fat")
            if not obs or obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
                status = EvaluationStatus.INSUFFICIENT_DATA
                summary_counts[status] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="ICMR_HFSS",
                        rule_id=rule_id,
                        rule_code=rule_code,
                        outcome=status,
                        title="ICMR Added Fat Threshold of Concern",
                        human_readable_explanation=(
                            "Added fat declaration is not present on product label. Under Indian labelling law, "
                            "added fat is voluntary. Cannot infer added fat from total fat."
                        ),
                        evidence_used={},
                        missing_evidence=["added_fat"],
                        statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                        official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                        source_version="May 2024",
                        warnings_or_limitations="Added fat is not inferred from total fat to avoid false positive alerts on natural oils."
                    )
                )
                continue

            if obs.per_100g_value is None:
                status = EvaluationStatus.INSUFFICIENT_DATA
                summary_counts[status] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="ICMR_HFSS",
                        rule_id=rule_id,
                        rule_code=rule_code,
                        outcome=status,
                        title="ICMR Added Fat Threshold of Concern",
                        human_readable_explanation="Added fat declared numeric value is missing (null); cannot evaluate threshold.",
                        evidence_used={},
                        missing_evidence=["added_fat"],
                        statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                        official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                        source_version="May 2024"
                    )
                )
                continue

            if obs.measurement_basis is None or obs.measurement_basis not in permitted_bases:
                status = EvaluationStatus.INSUFFICIENT_DATA
                summary_counts[status] += 1
                results.append(
                    RuleEvaluationResult(
                        engine_name="ICMR_HFSS",
                        rule_id=rule_id,
                        rule_code=rule_code,
                        outcome=status,
                        title="ICMR Added Fat Threshold of Concern",
                        human_readable_explanation=(
                            f"Added fat measurement basis is "
                            f"{'unresolved (None)' if obs.measurement_basis is None else f'incompatible ({obs.measurement_basis.value})'}; "
                            f"rule requires '{permitted_str}'."
                        ),
                        evidence_used={"measurement_basis": obs.measurement_basis.value if obs.measurement_basis else None},
                        missing_evidence=["added_fat_measurement_basis"],
                        statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                        official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                        source_version="May 2024"
                    )
                )
                continue

            val = obs.per_100g_value
            breached = val > threshold
            outcome = EvaluationStatus.FAIL if breached else EvaluationStatus.PASS
            summary_counts[outcome] += 1
            basis_unit = "g" if obs.measurement_basis == MeasurementBasis.PER_100G else "ml"
            results.append(
                RuleEvaluationResult(
                    engine_name="ICMR_HFSS",
                    rule_id=rule_id,
                    rule_code=rule_code,
                    outcome=outcome,
                    title="ICMR Added Fat Threshold of Concern",
                    human_readable_explanation=(
                        f"Added fat content is {float(val):.2f}g/100{basis_unit}, "
                        f"{'exceeding' if breached else 'within'} the ICMR threshold of concern ({float(threshold):.1f}g)."
                    ),
                    evidence_used={"added_fat_observed": float(val), "threshold": float(threshold)},
                    missing_evidence=[],
                    statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                    official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                    source_version="May 2024"
                )
            )
            continue

        # Standard nutrient threshold (Added Sugar, Energy)
        obs = product.nutrients.get(nutrient_code)
        if not obs or obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
            status = EvaluationStatus.INSUFFICIENT_DATA
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="ICMR_HFSS",
                    rule_id=rule_id,
                    rule_code=rule_code,
                    outcome=status,
                    title=f"ICMR {nutrient_code.replace('_', ' ').title()} Threshold of Concern",
                    human_readable_explanation=f"Nutrient '{nutrient_code}' declaration is missing from label.",
                    evidence_used={},
                    missing_evidence=[nutrient_code],
                    statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                    official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                    source_version="May 2024"
                )
            )
            continue

        if obs.per_100g_value is None:
            status = EvaluationStatus.INSUFFICIENT_DATA
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="ICMR_HFSS",
                    rule_id=rule_id,
                    rule_code=rule_code,
                    outcome=status,
                    title=f"ICMR {nutrient_code.replace('_', ' ').title()} Threshold of Concern",
                    human_readable_explanation=f"Nutrient '{nutrient_code}' declared numeric value is missing (null).",
                    evidence_used={},
                    missing_evidence=[nutrient_code],
                    statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                    official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                    source_version="May 2024"
                )
            )
            continue

        if obs.measurement_basis is None or obs.measurement_basis not in permitted_bases:
            status = EvaluationStatus.INSUFFICIENT_DATA
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="ICMR_HFSS",
                    rule_id=rule_id,
                    rule_code=rule_code,
                    outcome=status,
                    title=f"ICMR {nutrient_code.replace('_', ' ').title()} Threshold of Concern",
                    human_readable_explanation=(
                        f"Nutrient '{nutrient_code}' measurement basis is "
                        f"{'unresolved (None)' if obs.measurement_basis is None else f'incompatible ({obs.measurement_basis.value})'}; "
                        f"rule requires '{permitted_str}'."
                    ),
                    evidence_used={"measurement_basis": obs.measurement_basis.value if obs.measurement_basis else None},
                    missing_evidence=[f"{nutrient_code}_measurement_basis"],
                    statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                    official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                    source_version="May 2024"
                )
            )
            continue

        val = obs.per_100g_value
        breached = val > threshold
        outcome = EvaluationStatus.FAIL if breached else EvaluationStatus.PASS
        summary_counts[outcome] += 1
        basis_unit = "g" if obs.measurement_basis == MeasurementBasis.PER_100G else "ml"
        results.append(
            RuleEvaluationResult(
                engine_name="ICMR_HFSS",
                rule_id=rule_id,
                rule_code=rule_code,
                outcome=outcome,
                title=f"ICMR {nutrient_code.replace('_', ' ').title()} Threshold of Concern",
                human_readable_explanation=(
                    f"Observed {float(val):.2f}{obs.unit}/100{basis_unit} "
                    f"{'exceeds' if breached else 'is within'} the ICMR threshold of concern ({float(threshold):.1f}{obs.unit})."
                ),
                evidence_used={"observed": float(val), "threshold": float(threshold), "unit": obs.unit},
                missing_evidence=[],
                statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
                official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                source_version="May 2024"
            )
        )

    # =========================================================================
    # Part 2: Table 15.2 Food Classification Matrix (9 Cells A1-C3)
    # =========================================================================
    # Table 15.2 strictly applies to SOLID foods only
    if product.food_form.value == "liquid":
        status = EvaluationStatus.NOT_APPLICABLE
        summary_counts[status] += 1
        results.append(
            RuleEvaluationResult(
                engine_name="ICMR_HFSS",
                rule_id="icmr_table_15_2_matrix_liquid_na",
                rule_code="ICMR_TABLE_15_2_MATRIX",
                outcome=status,
                title="ICMR Table 15.2 Matrix Applicability",
                human_readable_explanation=(
                    "Table 15.2 Category 1-3 matrix applies strictly to solid foods. "
                    "ICMR-NIN DGI 2024 does not define Category 1-3 energy bands for beverages."
                ),
                evidence_used={"food_form": "liquid"},
                missing_evidence=[],
                statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97",
                official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                source_version="May 2024"
            )
        )
        return EngineBatchResult(
            engine_name="ICMR_HFSS",
            product_id=product.product_id,
            food_form=product.food_form.value,
            results=results,
            summary_counts=summary_counts
        )

    # 1. Determine Processing Group (A, B, C)
    processing_classes = [ing.processing_classification for ing in product.ingredients]
    has_cosmetic = any(pc == IngredientProcessingClass.COSMETIC_ADDITIVE for pc in processing_classes)
    has_industrial_fraction = any(pc == IngredientProcessingClass.INDUSTRIAL_FRACTION for pc in processing_classes)
    has_functional = any(pc == IngredientProcessingClass.FUNCTIONAL_ADDITIVE for pc in processing_classes)
    all_whole = all(pc in (IngredientProcessingClass.WHOLE_FOOD, IngredientProcessingClass.CULINARY_PROCESSED) for pc in processing_classes) if processing_classes else False

    determined_group: Optional[str] = None
    group_indeterminate = False

    if has_cosmetic or has_industrial_fraction:
        determined_group = "GROUP_C"
    elif all_whole:
        has_culinary = any(pc == IngredientProcessingClass.CULINARY_PROCESSED for pc in processing_classes)
        determined_group = "GROUP_B" if has_culinary else "GROUP_A"
    elif has_functional and not (has_cosmetic or has_industrial_fraction):
        # Ambiguous edge case: simple functional additive in whole food base
        group_indeterminate = True
    else:
        group_indeterminate = True

    # 2. Determine Nutritional Category (1, 2, 3) from Energy
    energy_obs = product.nutrients.get("energy")
    determined_cat: Optional[str] = None

    if (
        not energy_obs
        or energy_obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN)
        or energy_obs.per_100g_value is None
        or energy_obs.measurement_basis is None
        or energy_obs.measurement_basis != MeasurementBasis.PER_100G
    ):
        status = EvaluationStatus.INSUFFICIENT_DATA
        summary_counts[status] += 1
        results.append(
            RuleEvaluationResult(
                engine_name="ICMR_HFSS",
                rule_id="icmr_table_15_2_energy_missing",
                rule_code="ICMR_TABLE_15_2_MATRIX",
                outcome=status,
                title="ICMR Table 15.2 Matrix Evaluation",
                human_readable_explanation=(
                    "Total energy declaration is missing, null, or has an incompatible/unresolved measurement basis "
                    "(must be PER_100G); cannot determine Table 15.2 nutritional category."
                ),
                evidence_used={
                    "energy_status": energy_obs.data_status.value if energy_obs else "ABSENT",
                    "measurement_basis": energy_obs.measurement_basis.value if (energy_obs and energy_obs.measurement_basis) else None
                },
                missing_evidence=["energy"],
                statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97",
                official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                source_version="May 2024"
            )
        )
        return EngineBatchResult(
            engine_name="ICMR_HFSS",
            product_id=product.product_id,
            food_form=product.food_form.value,
            results=results,
            summary_counts=summary_counts
        )

    energy_kcal = energy_obs.per_100g_value
    if energy_kcal <= Decimal("250.0"):
        determined_cat = "CAT_1"
    elif energy_kcal <= Decimal("500.0"):
        determined_cat = "CAT_2"
    else:
        determined_cat = "CAT_3"

    # If processing group is indeterminate, emit INDETERMINATE result
    if group_indeterminate or not determined_group:
        status = EvaluationStatus.INDETERMINATE
        summary_counts[status] += 1
        results.append(
            RuleEvaluationResult(
                engine_name="ICMR_HFSS",
                rule_id="icmr_table_15_2_indeterminate",
                rule_code="ICMR_TABLE_15_2_MATRIX",
                outcome=status,
                title="ICMR Table 15.2 Processing Classification Indeterminate",
                human_readable_explanation=(
                    f"Product has energy density {float(energy_kcal):.1f} kcal/100g ({determined_cat}), but contains functional "
                    f"additives without conclusive evidence of cosmetic formulation or matrix deconstruction. Ambiguous between "
                    f"Group B (Culinary processed) and Group C (Ultra-processed). Requires recipe audit."
                ),
                evidence_used={"energy_kcal": float(energy_kcal), "nutritional_category": determined_cat},
                missing_evidence=[],
                statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97",
                official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
                source_version="May 2024"
            )
        )
        return EngineBatchResult(
            engine_name="ICMR_HFSS",
            product_id=product.product_id,
            food_form=product.food_form.value,
            results=results,
            summary_counts=summary_counts
        )

    # 3. Match Cell Code (A1 through C3)
    group_letter = determined_group.replace("GROUP_", "")
    cat_number = determined_cat.replace("CAT_", "")
    cell_code = f"{group_letter}{cat_number}"

    # Lookup rule in matrix_rules
    matched_matrix_rule = next((r for r in matrix_rules if r.get("cell_code") == cell_code), None)
    is_upf = (determined_group == "GROUP_C")
    is_hfss = (determined_cat in ("CAT_2", "CAT_3"))

    guidance = matched_matrix_rule.get("consumer_guidance", "") if matched_matrix_rule else ""
    status = EvaluationStatus.PASS
    summary_counts[status] += 1
    results.append(
        RuleEvaluationResult(
            engine_name="ICMR_HFSS",
            rule_id=f"icmr_matrix_cell_{cell_code.lower()}",
            rule_code=f"ICMR_MATRIX_CELL_{cell_code}",
            outcome=status,
            title=f"ICMR Table 15.2 Matrix: Cell {cell_code}",
            human_readable_explanation=(
                f"Classified into Matrix Cell {cell_code}: Processing {determined_group} with Nutritional Category {determined_cat} "
                f"({float(energy_kcal):.1f} kcal/100g). UPF: {is_upf}, HFSS: {is_hfss}. {guidance}"
            ),
            evidence_used={
                "cell_code": cell_code,
                "processing_group": determined_group,
                "nutritional_category": determined_cat,
                "is_upf": is_upf,
                "is_hfss": is_hfss,
                "energy_kcal": float(energy_kcal)
            },
            missing_evidence=[],
            statutory_citation="ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97-98",
            official_source_url="https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
            source_version="May 2024"
        )
    )

    return EngineBatchResult(
        engine_name="ICMR_HFSS",
        product_id=product.product_id,
        food_form=product.food_form.value,
        results=results,
        summary_counts=summary_counts
    )
