"""
YumSure Deterministic FSSAI Claims Engine.

Responsibilities:
- Evaluates voluntary marketing claims against FSSAI (Advertising and Claims) Regulations 2018 (Consolidated 2022).
- Executes compound AST condition expressions (nested AND/OR logic) with allowlisted operators (LT, LTE, GT, GTE, EQ).
- Evaluates Schedule II authorized synonyms.
- Handles ingredient-dependent claims (e.g. Regulation 6(1) No Added Sugar).
- Pure deterministic execution: zero eval(), zero exec(), zero dynamic code execution.
"""

from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from app.domain.engines.contracts import (
    ProductEvaluationInput,
    RuleEvaluationResult,
    EngineBatchResult,
    EvaluationStatus,
    NutrientDataStatus,
    IngredientSugarClass,
    MeasurementBasis
)


def _compare(val: Decimal, op: str, threshold: Decimal) -> bool:
    """Executes safe scalar comparison without eval()."""
    if op == "LT":
        return val < threshold
    elif op == "LTE":
        return val <= threshold
    elif op == "GT":
        return val > threshold
    elif op == "GTE":
        return val >= threshold
    elif op == "EQ":
        return val == threshold
    raise ValueError(f"Unsupported comparison operator: {op}")


def _evaluate_node(
    node: Dict[str, Any],
    product: ProductEvaluationInput
) -> Tuple[EvaluationStatus, Dict[str, Any], List[str], str]:
    """
    Evaluates a single condition node in the claim AST tree.
    Returns: (status, evidence_dict, missing_fields, explanation)
    """
    node_type = node.get("type")

    # 1. Nutrient Threshold Evaluation
    if node_type == "NUTRIENT_THRESHOLD":
        nutrient_code = node["nutrient_code"]
        op = node["operator"]
        threshold = Decimal(str(node["threshold_value"]))
        basis = node.get("measurement_basis")
        if not basis:
            return (
                EvaluationStatus.INSUFFICIENT_DATA,
                {},
                [],
                f"Rule condition for '{nutrient_code}' does not specify a measurement basis."
            )
        req_form = node.get("food_form", "both")

        # Check food form applicability
        if req_form != "both" and req_form != product.food_form.value:
            return (
                EvaluationStatus.NOT_APPLICABLE,
                {"food_form": product.food_form.value, "required_form": req_form},
                [],
                f"Condition applies only to {req_form} products."
            )

        obs = product.nutrients.get(nutrient_code)
        if not obs or obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
            return (
                EvaluationStatus.INSUFFICIENT_DATA,
                {},
                [nutrient_code],
                f"Nutrient '{nutrient_code}' is not declared on product packaging."
            )

        val = obs.per_100g_value
        if val is None:
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, [nutrient_code], f"Nutrient '{nutrient_code}' has null value.")

        if obs.measurement_basis is None:
            return (
                EvaluationStatus.INSUFFICIENT_DATA,
                {},
                [f"{nutrient_code}_measurement_basis"],
                f"Nutrient '{nutrient_code}' has unresolved measurement basis (None)."
            )

        # Handle PER_100G and PER_100ML basis
        if basis in ("PER_100G", "PER_100ML"):
            if obs.measurement_basis.value != basis:
                return (
                    EvaluationStatus.INSUFFICIENT_DATA,
                    {"required_basis": basis, "observed_basis": obs.measurement_basis.value},
                    [f"{nutrient_code}_measurement_basis"],
                    f"Nutrient '{nutrient_code}' basis '{obs.measurement_basis.value}' is incompatible with rule required basis '{basis}'."
                )
            val = obs.per_100g_value

        # Handle PER_100KCAL basis
        elif basis == "PER_100KCAL":
            if obs.measurement_basis not in (MeasurementBasis.PER_100G, MeasurementBasis.PER_100ML):
                return (
                    EvaluationStatus.INSUFFICIENT_DATA,
                    {"observed_basis": obs.measurement_basis.value},
                    [f"{nutrient_code}_measurement_basis"],
                    f"Nutrient '{nutrient_code}' basis '{obs.measurement_basis.value}' cannot be converted to PER_100KCAL without compatible reference."
                )
            energy_obs = product.nutrients.get("energy")
            if not energy_obs or energy_obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
                return (
                    EvaluationStatus.INSUFFICIENT_DATA,
                    {},
                    ["energy"],
                    "Total energy declaration required to evaluate per-100 kcal basis."
                )
            if energy_obs.per_100g_value is None or energy_obs.per_100g_value <= Decimal("0"):
                return (
                    EvaluationStatus.INSUFFICIENT_DATA,
                    {},
                    ["energy"],
                    "Total energy declaration required to evaluate per-100 kcal basis."
                )
            if energy_obs.measurement_basis is None:
                return (
                    EvaluationStatus.INSUFFICIENT_DATA,
                    {},
                    ["energy_measurement_basis"],
                    "Energy declaration has unresolved measurement basis."
                )
            if obs.measurement_basis != energy_obs.measurement_basis:
                return (
                    EvaluationStatus.INSUFFICIENT_DATA,
                    {"nutrient_basis": obs.measurement_basis.value, "energy_basis": energy_obs.measurement_basis.value},
                    ["measurement_basis"],
                    f"Nutrient '{nutrient_code}' basis '{obs.measurement_basis.value}' is incompatible with energy basis '{energy_obs.measurement_basis.value}'."
                )
            energy_val = energy_obs.per_100g_value
            val = (obs.per_100g_value / energy_val) * Decimal("100.0")

        else:
            return (
                EvaluationStatus.INSUFFICIENT_DATA,
                {"required_basis": basis},
                [],
                f"Unsupported rule measurement basis '{basis}'."
            )

        try:
            satisfied = _compare(val, op, threshold)
        except ValueError as e:
            return (EvaluationStatus.INDETERMINATE, {}, [], str(e))
        status = EvaluationStatus.PASS if satisfied else EvaluationStatus.FAIL
        evidence = {
            "nutrient": nutrient_code,
            "observed_value": float(val),
            "operator": op,
            "threshold": float(threshold),
            "basis": basis
        }
        op_symbol = "<" if op == "LT" else ("<=" if op == "LTE" else (">=" if op == "GTE" else (">" if op == "GT" else "==")))
        explanation = f"Observed {float(val):.2f}{obs.unit if basis != 'PER_100KCAL' else 'g/100kcal'} {op_symbol} required {float(threshold):.2f}."
        return (status, evidence, [], explanation)

    # 2. Percentage of Total Energy Evaluation
    elif node_type == "ENERGY_PERCENTAGE":
        nutrient_code = node["nutrient_code"]
        op = node["operator"]
        threshold = Decimal(str(node["threshold_value"]))

        obs = product.nutrients.get(nutrient_code)
        energy_obs = product.nutrients.get("energy")

        if not obs or obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, [nutrient_code], f"Nutrient '{nutrient_code}' is not declared.")
        if obs.per_100g_value is None:
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, [nutrient_code], f"Nutrient '{nutrient_code}' has null value.")
        if obs.measurement_basis is None:
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, [f"{nutrient_code}_measurement_basis"], f"Nutrient '{nutrient_code}' has unresolved measurement basis.")

        if not energy_obs or energy_obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN):
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, ["energy"], "Total energy declaration required for % energy calculation.")
        if energy_obs.per_100g_value is None or energy_obs.per_100g_value <= Decimal("0"):
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, ["energy"], "Total energy declaration required for % energy calculation.")
        if energy_obs.measurement_basis is None:
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, ["energy_measurement_basis"], "Energy declaration has unresolved measurement basis.")

        if obs.measurement_basis != energy_obs.measurement_basis:
            return (
                EvaluationStatus.INSUFFICIENT_DATA,
                {"nutrient_basis": obs.measurement_basis.value, "energy_basis": energy_obs.measurement_basis.value},
                ["measurement_basis"],
                f"Nutrient '{nutrient_code}' basis '{obs.measurement_basis.value}' is incompatible with energy basis '{energy_obs.measurement_basis.value}'."
            )

        val_g = obs.per_100g_value
        energy_kcal = energy_obs.per_100g_value

        # Saturated fat factor is 9.0 kcal/g
        nutrient_energy = val_g * Decimal("9.0")
        pct_energy = (nutrient_energy / energy_kcal) * Decimal("100.0")

        try:
            satisfied = _compare(pct_energy, op, threshold)
        except ValueError as e:
            return (EvaluationStatus.INDETERMINATE, {}, [], str(e))
        status = EvaluationStatus.PASS if satisfied else EvaluationStatus.FAIL
        evidence = {
            "nutrient": nutrient_code,
            "pct_total_energy": round(float(pct_energy), 2),
            "operator": op,
            "threshold_pct": float(threshold)
        }
        explanation = f"Provides {float(pct_energy):.1f}% of total energy from {nutrient_code} (statutory threshold: {op} {float(threshold):.1f}%)."
        return (status, evidence, [], explanation)

    # 3. Ingredient Check (e.g. FSSAI Reg 6(1) No Added Sugar)
    elif node_type == "INGREDIENT_CHECK":
        criteria = node.get("ingredient_criteria", {})
        disallowed_classes = criteria.get("disallowed_sugar_classes", [])
        disallowed_codes = criteria.get("disallowed_ingredient_codes", [])

        violating_ingredients: List[str] = []
        for ing in product.ingredients:
            if ing.sugar_classification.value in disallowed_classes:
                violating_ingredients.append(f"{ing.declared_label_text} ({ing.sugar_classification.value})")
            elif ing.ingredient_code in disallowed_codes:
                violating_ingredients.append(f"{ing.declared_label_text} ({ing.ingredient_code})")

        if violating_ingredients:
            return (
                EvaluationStatus.FAIL,
                {"disallowed_ingredients_found": violating_ingredients},
                [],
                f"Contains ingredients that impart sweetness or replace added sugar: {', '.join(violating_ingredients)}."
            )
        return (EvaluationStatus.PASS, {"ingredients_audited": len(product.ingredients)}, [], "No disallowed ingredients found.")

    # 4. Nested Expression Group
    elif node_type == "EXPRESSION_GROUP":
        nested = node.get("nested_expression")
        if not nested:
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, [], "Empty nested expression group.")
        return _evaluate_group(nested, product)

    return (EvaluationStatus.INDETERMINATE, {}, [], f"Unknown node type: {node_type}")


def _evaluate_group(
    group_node: Dict[str, Any],
    product: ProductEvaluationInput,
    depth: int = 0
) -> Tuple[EvaluationStatus, Dict[str, Any], List[str], str]:
    """
    Evaluates a composite boolean AST node (AND / OR).
    Recursion depth limit: 5 levels.
    """
    if depth > 5:
        return (
            EvaluationStatus.INDETERMINATE,
            {},
            [],
            f"AST recursion depth limit exceeded (max 5, current {depth})"
        )

    log_op = group_node.get("logical_operator", "AND").upper()
    conditions = group_node.get("conditions", [])

    if not conditions:
        return (EvaluationStatus.INDETERMINATE, {}, [], "Empty condition group")

    sub_results = []
    for cond in conditions:
        if "logical_operator" in cond:
            res = _evaluate_group(cond, product, depth=depth + 1)
        else:
            res = _evaluate_node(cond, product)
        sub_results.append(res)

    all_evidence = {}
    all_missing = []
    explanations = []

    for i, (st, ev, miss, exp) in enumerate(sub_results):
        all_evidence[f"condition_{i+1}"] = ev
        all_missing.extend(miss)
        if exp:
            explanations.append(exp)

    # Boolean Evaluation Logic
    if log_op == "AND":
        # Any FAIL -> Overall FAIL
        if any(st == EvaluationStatus.FAIL for st, _, _, _ in sub_results):
            final_status = EvaluationStatus.FAIL
        elif any(st == EvaluationStatus.INSUFFICIENT_DATA for st, _, _, _ in sub_results):
            final_status = EvaluationStatus.INSUFFICIENT_DATA
        elif any(st == EvaluationStatus.INDETERMINATE for st, _, _, _ in sub_results):
            final_status = EvaluationStatus.INDETERMINATE
        elif all(st == EvaluationStatus.PASS for st, _, _, _ in sub_results):
            final_status = EvaluationStatus.PASS
        elif any(st == EvaluationStatus.NOT_APPLICABLE for st, _, _, _ in sub_results):
            final_status = EvaluationStatus.NOT_APPLICABLE
        else:
            final_status = EvaluationStatus.INDETERMINATE
        combined_exp = " AND ".join(explanations)
        return (final_status, all_evidence, list(set(all_missing)), combined_exp)

    elif log_op == "OR":
        # Any PASS -> Overall PASS
        if any(st == EvaluationStatus.PASS for st, _, _, _ in sub_results):
            final_status = EvaluationStatus.PASS
        elif all(st == EvaluationStatus.FAIL for st, _, _, _ in sub_results):
            final_status = EvaluationStatus.FAIL
        elif any(st == EvaluationStatus.INSUFFICIENT_DATA for st, _, _, _ in sub_results):
            final_status = EvaluationStatus.INSUFFICIENT_DATA
        else:
            final_status = EvaluationStatus.INDETERMINATE
        combined_exp = " OR ".join(explanations)
        return (final_status, all_evidence, list(set(all_missing)), combined_exp)

    return (EvaluationStatus.INDETERMINATE, {}, [], f"Unknown logical operator: {log_op}")


def evaluate_claims(
    product: ProductEvaluationInput,
    rules: List[Dict[str, Any]],
    synonym_registry: Optional[Dict[str, List[str]]] = None
) -> EngineBatchResult:
    """
    Evaluates voluntary marketing claims against statutory FSSAI Schedule I & Schedule II conditions.
    """
    synonyms_map = synonym_registry or {}
    results: List[RuleEvaluationResult] = []
    summary_counts: Dict[EvaluationStatus, int] = {
        EvaluationStatus.PASS: 0,
        EvaluationStatus.FAIL: 0,
        EvaluationStatus.INSUFFICIENT_DATA: 0,
        EvaluationStatus.INDETERMINATE: 0,
        EvaluationStatus.NOT_APPLICABLE: 0,
    }

    for rule in rules:
        rule_id = rule["claim_id"]
        claim_code = rule["claim_code"]
        claim_title = rule.get("claim_title", claim_code)
        rule_food_form = rule.get("food_form", "both")

        # Scope check: solid / liquid
        if rule_food_form != "both" and rule_food_form != product.food_form.value:
            status = EvaluationStatus.NOT_APPLICABLE
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="CLAIMS",
                    rule_id=rule_id,
                    rule_code=claim_code,
                    outcome=status,
                    title=claim_title,
                    human_readable_explanation=f"Rule applies to {rule_food_form} foods only.",
                    evidence_used={"product_food_form": product.food_form.value},
                    missing_evidence=[],
                    statutory_citation=rule.get("fssai_regulation_reference", "FSSAI Regulations 2018"),
                    official_source_url=rule.get("official_url", "https://fssai.gov.in/food-law/regulations/amendments/advertising-claims"),
                    source_version=rule.get("official_source_version", "Version III (04-10-2022)")
                )
            )
            continue

        expr = rule.get("condition_expression")
        if not expr:
            status = EvaluationStatus.INSUFFICIENT_DATA
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="CLAIMS",
                    rule_id=rule_id,
                    rule_code=claim_code,
                    outcome=status,
                    title=claim_title,
                    human_readable_explanation="Regulatory claim condition expression is pending definition.",
                    evidence_used={},
                    missing_evidence=["condition_expression"],
                    statutory_citation=rule.get("fssai_regulation_reference", "FSSAI Regulations 2018"),
                    official_source_url=rule.get("official_url", "https://fssai.gov.in/food-law/regulations/amendments/advertising-claims"),
                    source_version=rule.get("official_source_version", "Version III (04-10-2022)")
                )
            )
            continue

        # Check AST depth limit <= 5
        try:
            from app.models.claim_ast_schema import check_ast_depth_iterative
            check_ast_depth_iterative(expr, max_depth=5)
        except Exception as e:
            status = EvaluationStatus.INDETERMINATE
            summary_counts[status] += 1
            results.append(
                RuleEvaluationResult(
                    engine_name="CLAIMS",
                    rule_id=rule_id,
                    rule_code=claim_code,
                    outcome=status,
                    title=claim_title,
                    human_readable_explanation=f"Condition expression structure rejected: {str(e)}",
                    evidence_used={},
                    missing_evidence=[],
                    statutory_citation=rule.get("fssai_regulation_reference", "FSSAI Regulations 2018"),
                    official_source_url=rule.get("official_url", "https://fssai.gov.in/food-law/regulations/amendments/advertising-claims"),
                    source_version=rule.get("official_source_version", "Version III (04-10-2022)")
                )
            )
            continue

        # Evaluate AST
        outcome, evidence, missing_fields, explanation = _evaluate_group(expr, product)

        # Check Schedule II authorized synonyms
        permitted_synonyms = rule.get("permitted_synonyms_schedule_ii", synonyms_map.get(claim_code, []))
        declared_match = None
        for decl in product.declared_claims:
            if decl.claim_code == claim_code or decl.raw_label_statement in permitted_synonyms:
                declared_match = decl.raw_label_statement
                break

        if declared_match:
            evidence["declared_label_claim"] = declared_match
            evidence["is_schedule_ii_authorized_synonym"] = declared_match in permitted_synonyms

        summary_counts[outcome] += 1
        results.append(
            RuleEvaluationResult(
                engine_name="CLAIMS",
                rule_id=rule_id,
                rule_code=claim_code,
                outcome=outcome,
                title=f"{claim_title} Eligibility",
                human_readable_explanation=explanation or rule.get("consumer_explanation", "Evaluated against FSSAI Schedule I criteria."),
                evidence_used=evidence,
                missing_evidence=missing_fields,
                statutory_citation=rule.get("fssai_regulation_reference", "FSSAI Claims Reg 2018 Schedule I"),
                official_source_url=rule.get("official_url", "https://fssai.gov.in/food-law/regulations/amendments/advertising-claims"),
                source_version=rule.get("official_source_version", "Version III (04-10-2022)")
            )
        )

    return EngineBatchResult(
        engine_name="CLAIMS",
        product_id=product.product_id,
        food_form=product.food_form.value,
        results=results,
        summary_counts=summary_counts
    )
