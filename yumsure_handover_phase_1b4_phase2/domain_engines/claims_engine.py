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
    IngredientSugarClass
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
        basis = node.get("measurement_basis", "PER_100G")
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

        # Handle PER_100KCAL basis
        if basis == "PER_100KCAL":
            energy_obs = product.nutrients.get("energy")
            if not energy_obs or energy_obs.per_100g_value is None or energy_obs.per_100g_value <= Decimal("0"):
                return (
                    EvaluationStatus.INSUFFICIENT_DATA,
                    {},
                    ["energy"],
                    "Total energy declaration required to evaluate per-100 kcal basis."
                )
            energy_val = energy_obs.per_100g_value
            val = (val / energy_val) * Decimal("100.0")

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
        if not energy_obs or energy_obs.per_100g_value is None or energy_obs.per_100g_value <= Decimal("0"):
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, ["energy"], "Total energy declaration required for % energy calculation.")

        val_g = obs.per_100g_value or Decimal("0")
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
        return (
            EvaluationStatus.PASS,
            {"ingredient_non_addition_verified": True},
            [],
            "Ingredient list contains zero added free sugars or sweetening substitutes."
        )

    # 4. Nested Expression Group
    elif node_type == "EXPRESSION_GROUP":
        nested = node.get("nested_expression")
        if not nested:
            return (EvaluationStatus.INSUFFICIENT_DATA, {}, [], "Empty nested expression group.")
        return _evaluate_group(nested, product)

    return (EvaluationStatus.INDETERMINATE, {}, [], f"Unknown node type: {node_type}")


def _evaluate_group(
    group: Dict[str, Any],
    product: ProductEvaluationInput
) -> Tuple[EvaluationStatus, Dict[str, Any], List[str], str]:
    """
    Recursively evaluates an AST condition group with AND/OR logic.
    """
    log_op = group.get("logical_operator", "AND")
    conditions = group.get("conditions", [])

    if not conditions:
        return (EvaluationStatus.INSUFFICIENT_DATA, {}, [], "Condition group contains no conditions.")

    child_results = [_evaluate_node(c, product) for c in conditions]

    statuses = [r[0] for r in child_results]
    all_evidence: Dict[str, Any] = {}
    all_missing: List[str] = []
    explanations: List[str] = []

    for idx, (_, ev, miss, exp) in enumerate(child_results):
        all_evidence[f"condition_{idx + 1}"] = ev
        all_missing.extend(miss)
        if exp:
            explanations.append(exp)

    # AND evaluation: all must PASS
    if log_op == "AND":
        if any(s == EvaluationStatus.FAIL for s in statuses):
            final_status = EvaluationStatus.FAIL
        elif any(s == EvaluationStatus.INSUFFICIENT_DATA for s in statuses):
            final_status = EvaluationStatus.INSUFFICIENT_DATA
        elif any(s == EvaluationStatus.INDETERMINATE for s in statuses):
            final_status = EvaluationStatus.INDETERMINATE
        elif all(s in (EvaluationStatus.PASS, EvaluationStatus.NOT_APPLICABLE) for s in statuses):
            final_status = EvaluationStatus.PASS if any(s == EvaluationStatus.PASS for s in statuses) else EvaluationStatus.NOT_APPLICABLE
        else:
            final_status = EvaluationStatus.FAIL
        combined_exp = " AND ".join(explanations)
        return (final_status, all_evidence, list(set(all_missing)), combined_exp)

    # OR evaluation: at least one must PASS
    elif log_op == "OR":
        if any(s == EvaluationStatus.PASS for s in statuses):
            final_status = EvaluationStatus.PASS
        elif all(s == EvaluationStatus.FAIL for s in statuses):
            final_status = EvaluationStatus.FAIL
        elif any(s == EvaluationStatus.INSUFFICIENT_DATA for s in statuses):
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

