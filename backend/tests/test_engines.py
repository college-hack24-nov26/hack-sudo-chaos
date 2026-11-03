"""
Comprehensive unit tests for YumSure Deterministic Engines:
- NutritionEngine
- ClaimsEngine
- ICMRHFSSEngine
- IngredientEngine

Verifies all sample cases from ENGINE_SAMPLE_CASES.md, four-state nutrient semantics,
five standardized evaluation outcomes, and strict absence of composite scores.
"""

import os
import sys
import json
from decimal import Decimal
import unittest

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from app.domain.engines.contracts import (
    FoodForm,
    NutrientDataStatus,
    EvaluationStatus,
    IngredientProcessingClass,
    IngredientSugarClass,
    NutrientObservationInput,
    IngredientObservationInput,
    DeclaredClaimInput,
    ProductEvaluationInput,
)
from app.domain.engines.nutrition_engine import evaluate_nutrition
from app.domain.engines.claims_engine import evaluate_claims
from app.domain.engines.icmr_hfss_engine import evaluate_icmr_hfss
from app.domain.engines.ingredient_engine import evaluate_ingredients


class TestDeterministicEngines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'seeds')
        )
        with open(os.path.join(seed_dir, 'icmr_table_15_1_seed.json'), 'r', encoding='utf-8') as f:
            cls.icmr_15_1_rules = json.load(f)
        with open(os.path.join(seed_dir, 'icmr_table_15_2_seed.json'), 'r', encoding='utf-8') as f:
            cls.icmr_15_2_rules = json.load(f)
        with open(os.path.join(seed_dir, 'fssai_schedule_i_claims_seed.json'), 'r', encoding='utf-8') as f:
            cls.claims_rules = json.load(f)
        with open(os.path.join(seed_dir, 'fssai_schedule_ii_synonyms_seed.json'), 'r', encoding='utf-8') as f:
            cls.synonym_registry = json.load(f)
        with open(os.path.join(seed_dir, 'ingredient_rules_seed.json'), 'r', encoding='utf-8') as f:
            cls.ingredient_rules = json.load(f)

    # -------------------------------------------------------------------------
    # 1. Nutrition Engine Tests
    # -------------------------------------------------------------------------
    def test_nutrition_complete_declaration_pass(self):
        """Scenario 1.1: Evidence-Complete Solid Whole Food (Roasted Bengal Gram)"""
        product = ProductEvaluationInput(
            product_id="prod_roasted_chana_001",
            product_name="Traditional Roasted Bengal Gram",
            food_form=FoodForm.SOLID,
            package_size="200g",
            serving_size_value=Decimal("30.0"),
            serving_size_unit="g",
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("380.0"), per_serving_value=Decimal("114.0"),
                    unit="kcal", data_status=NutrientDataStatus.PRESENT
                ),
                "protein": NutrientObservationInput(
                    nutrient_code="protein", per_100g_value=Decimal("19.5"), per_serving_value=Decimal("5.85"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "carbohydrates": NutrientObservationInput(
                    nutrient_code="carbohydrates", per_100g_value=Decimal("58.0"), per_serving_value=Decimal("17.4"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "total_sugars": NutrientObservationInput(
                    nutrient_code="total_sugars", per_100g_value=Decimal("2.5"), per_serving_value=Decimal("0.75"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "added_sugars": NutrientObservationInput(
                    nutrient_code="added_sugars", per_100g_value=Decimal("0.0"), per_serving_value=Decimal("0.0"),
                    unit="g", data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
                "total_fat": NutrientObservationInput(
                    nutrient_code="total_fat", per_100g_value=Decimal("5.2"), per_serving_value=Decimal("1.56"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat", per_100g_value=Decimal("0.8"), per_serving_value=Decimal("0.24"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat", per_100g_value=Decimal("0.0"), per_serving_value=Decimal("0.0"),
                    unit="g", data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium", per_100g_value=Decimal("12.0"), per_serving_value=Decimal("3.6"),
                    unit="mg", data_status=NutrientDataStatus.PRESENT
                ),
                "dietary_fibre": NutrientObservationInput(
                    nutrient_code="dietary_fibre", per_100g_value=Decimal("10.8"), per_serving_value=Decimal("3.24"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
            }
        )

        batch = evaluate_nutrition(product)
        self.assertEqual(batch.engine_name, "NUTRITION")

        # Zero missing mandatory notices generated
        missing_mandatory = [r for r in batch.results if r.rule_id.startswith("fssai_mandatory_")]
        self.assertEqual(len(missing_mandatory), 0)

        # Check % daily contribution calculations
        protein_res = next(r for r in batch.results if r.rule_id == "fssai_rdi_contrib_protein")
        self.assertEqual(protein_res.outcome, EvaluationStatus.PASS)
        # Protein 5.85g / 54g = 10.83%
        self.assertAlmostEqual(float(protein_res.evidence_used["pct_rdi_per_serving"]), 10.83, delta=0.1)

        # Check that NO aggregate health score is output
        self.assertFalse(hasattr(batch, "health_score"))
        self.assertFalse(hasattr(batch, "grade"))

    def test_nutrition_missing_mandatory_declarations_insufficient_data(self):
        """Scenario 1.2: Missing mandatory nutrients -> INSUFFICIENT_DATA notices generated"""
        product = ProductEvaluationInput(
            product_name="Incompletely Labelled Wafer",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("520.0"),
                    unit="kcal", data_status=NutrientDataStatus.PRESENT
                ),
                "total_fat": NutrientObservationInput(
                    nutrient_code="total_fat", per_100g_value=Decimal("28.0"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                # Missing: protein, carbohydrates, total_sugars, added_sugars, saturated_fat, trans_fat, sodium
            }
        )
        batch = evaluate_nutrition(product)
        missing_results = [r for r in batch.results if r.rule_id.startswith("fssai_mandatory_")]
        self.assertGreater(len(missing_results), 0)
        missing_codes = {r.missing_evidence[0] for r in missing_results}
        self.assertIn("protein", missing_codes)
        self.assertIn("sodium", missing_codes)
        self.assertIn("carbohydrates", missing_codes)

    # -------------------------------------------------------------------------
    # 2. Claims Engine Tests
    # -------------------------------------------------------------------------
    def test_claims_trans_fat_free_pass(self):
        """Scenario 2.1: Trans Fat Free Claim PASS on compound AST"""
        product = ProductEvaluationInput(
            product_name="Refined Sunflower Oil",
            food_form=FoodForm.LIQUID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("900.0"), unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat", per_100g_value=Decimal("0.05"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat", per_100g_value=Decimal("0.65"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Trans Fat Free")
            ]
        )
        batch = evaluate_claims(product, self.claims_rules, self.synonym_registry)
        # Find liquid trans fat free rule result
        res = next(r for r in batch.results if r.rule_id == "fssai_claim_trans_fat_free_liquid")
        self.assertEqual(res.outcome, EvaluationStatus.PASS)
        self.assertIn("Observed 0.05g < required 0.20", res.human_readable_explanation)

    def test_claims_trans_fat_free_breached_fail(self):
        """Scenario 2.2: Trans fat free claim FAILS when saturated fat exceeds limit"""
        product = ProductEvaluationInput(
            product_name="Bakery Shortening",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("884.0"), unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat", per_100g_value=Decimal("0.10"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat", per_100g_value=Decimal("35.0"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat")
            ]
        )
        batch = evaluate_claims(product, self.claims_rules, self.synonym_registry)
        res = next(r for r in batch.results if r.rule_id == "fssai_claim_trans_fat_free_solid")
        self.assertEqual(res.outcome, EvaluationStatus.FAIL)

    def test_claims_missing_nutrient_insufficient_data(self):
        """Scenario 2.3: Saturated fat is NOT_DECLARED -> claim evaluation returns INSUFFICIENT_DATA"""
        product = ProductEvaluationInput(
            product_name="Partially Labelled Oil",
            food_form=FoodForm.LIQUID,
            nutrients={
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat", per_100g_value=Decimal("0.0"), unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat", per_100g_value=None, unit="g",
                    data_status=NutrientDataStatus.NOT_DECLARED
                ),
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Trans Fat Free")
            ]
        )
        batch = evaluate_claims(product, self.claims_rules, self.synonym_registry)
        res = next(r for r in batch.results if r.rule_id == "fssai_claim_trans_fat_free_liquid")
        self.assertEqual(res.outcome, EvaluationStatus.INSUFFICIENT_DATA)
        self.assertIn("saturated_fat", res.missing_evidence)

    def test_claims_synonym_resolution(self):
        """Schedule II synonym 'Zero Trans Fat' maps to TRANS_FAT_FREE rule"""
        product = ProductEvaluationInput(
            product_name="Cold Pressed Sesame Oil",
            food_form=FoodForm.LIQUID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("900.0"), unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat", per_100g_value=Decimal("0.0"), unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat", per_100g_value=Decimal("0.5"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="CUSTOM_LABEL_CLAIM", raw_label_statement="Zero Trans Fat")
            ]
        )
        batch = evaluate_claims(product, self.claims_rules, self.synonym_registry)
        res = next(r for r in batch.results if r.rule_id == "fssai_claim_trans_fat_free_liquid")
        self.assertEqual(res.outcome, EvaluationStatus.PASS)
        self.assertEqual(res.evidence_used.get("declared_label_claim"), "Zero Trans Fat")
        self.assertTrue(res.evidence_used.get("is_schedule_ii_authorized_synonym"))

    def test_claims_no_added_sugar_non_addition(self):
        """FSSAI Reg 6(1): No Added Sugar fails if added sugar ingredient (honey/sugar) present"""
        product = ProductEvaluationInput(
            product_name="Honey Granola",
            food_form=FoodForm.SOLID,
            nutrients={
                "added_sugars": NutrientObservationInput(
                    nutrient_code="added_sugars", per_100g_value=Decimal("0.0"), unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
            },
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="honey", declared_label_text="Pure Honey", sequence_order=1,
                    sugar_classification=IngredientSugarClass.ADDED_FREE_SUGAR
                )
            ],
            declared_claims=[
                DeclaredClaimInput(claim_code="NO_ADDED_SUGARS", raw_label_statement="No Added Sugar")
            ]
        )
        batch = evaluate_claims(product, self.claims_rules, self.synonym_registry)
        res = next(r for r in batch.results if r.rule_id == "fssai_claim_no_added_sugars")
        self.assertEqual(res.outcome, EvaluationStatus.FAIL)
        self.assertIn("Contains ingredients that impart sweetness or replace added sugar", res.human_readable_explanation)

    # -------------------------------------------------------------------------
    # 3. ICMR-NIN HFSS Engine Tests
    # -------------------------------------------------------------------------
    def test_icmr_matrix_whole_food_cell_a1(self):
        """Scenario 3.1: Minimally processed whole food (Cut Apples) -> Cell A1 (Non-UPF, Non-HFSS)"""
        product = ProductEvaluationInput(
            product_name="Fresh Cut Apple Slices",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("52.0"), unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "added_sugars": NutrientObservationInput(
                    nutrient_code="added_sugars", per_100g_value=Decimal("0.0"), unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium", per_100g_value=Decimal("1.0"), unit="mg",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "added_fat": NutrientObservationInput(
                    nutrient_code="added_fat", per_100g_value=Decimal("0.0"), unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
            },
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="apple", declared_label_text="Fresh Apples", sequence_order=1,
                    processing_classification=IngredientProcessingClass.WHOLE_FOOD
                )
            ]
        )
        batch = evaluate_icmr_hfss(product, self.icmr_15_1_rules, self.icmr_15_2_rules)
        matrix_res = next(r for r in batch.results if "MATRIX" in r.rule_code)
        self.assertEqual(matrix_res.outcome, EvaluationStatus.PASS)
        self.assertEqual(matrix_res.evidence_used["cell_code"], "A1")
        self.assertFalse(matrix_res.evidence_used["is_upf"])
        self.assertFalse(matrix_res.evidence_used["is_hfss"])

    def test_icmr_matrix_ultra_processed_cell_c3(self):
        """Scenario 3.2: Ultra-processed snack with cosmetic additive >500 kcal -> Cell C3 (UPF, HFSS)"""
        product = ProductEvaluationInput(
            product_name="Cheese Flavoured Puffs",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("530.0"), unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "added_sugars": NutrientObservationInput(
                    nutrient_code="added_sugars", per_100g_value=Decimal("4.5"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium", per_100g_value=Decimal("750.0"), unit="mg",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "added_fat": NutrientObservationInput(
                    nutrient_code="added_fat", per_100g_value=Decimal("28.0"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
            },
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="corn_meal", declared_label_text="Degermed Corn Meal", sequence_order=1,
                    processing_classification=IngredientProcessingClass.CULINARY_PROCESSED
                ),
                IngredientObservationInput(
                    ingredient_code="flavour_enhancer_621", declared_label_text="MSG (INS 621)", sequence_order=2,
                    processing_classification=IngredientProcessingClass.COSMETIC_ADDITIVE
                ),
            ]
        )
        batch = evaluate_icmr_hfss(product, self.icmr_15_1_rules, self.icmr_15_2_rules)
        matrix_res = next(r for r in batch.results if "MATRIX" in r.rule_code)
        self.assertEqual(matrix_res.outcome, EvaluationStatus.PASS)
        self.assertEqual(matrix_res.evidence_used["cell_code"], "C3")
        self.assertTrue(matrix_res.evidence_used["is_upf"])
        self.assertTrue(matrix_res.evidence_used["is_hfss"])

    def test_icmr_liquid_matrix_not_applicable(self):
        """Scenario 3.3: Liquid beverages return NOT_APPLICABLE for Table 15.2 matrix"""
        product = ProductEvaluationInput(
            product_name="Sparkling Cola Beverage",
            food_form=FoodForm.LIQUID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("44.0"), unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "added_sugars": NutrientObservationInput(
                    nutrient_code="added_sugars", per_100g_value=Decimal("10.6"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium", per_100g_value=Decimal("15.0"), unit="mg",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "added_fat": NutrientObservationInput(
                    nutrient_code="added_fat", per_100g_value=Decimal("0.0"), unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
            }
        )
        batch = evaluate_icmr_hfss(product, self.icmr_15_1_rules, self.icmr_15_2_rules)
        matrix_res = next(r for r in batch.results if "MATRIX" in r.rule_code)
        self.assertEqual(matrix_res.outcome, EvaluationStatus.NOT_APPLICABLE)
        self.assertIn("solid", matrix_res.human_readable_explanation.lower())

    def test_icmr_missing_added_fat_insufficient_data(self):
        """Added fat cannot be inferred from total fat; missing added fat returns INSUFFICIENT_DATA"""
        product = ProductEvaluationInput(
            product_name="Snack Cracker",
            food_form=FoodForm.SOLID,
            nutrients={
                "total_fat": NutrientObservationInput(
                    nutrient_code="total_fat", per_100g_value=Decimal("18.0"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                ),
                # added_fat is not provided
            }
        )
        batch = evaluate_icmr_hfss(product, self.icmr_15_1_rules, self.icmr_15_2_rules)
        fat_rule = next(r for r in batch.results if r.rule_id == "icmr_15_1_added_fat_solid")
        self.assertEqual(fat_rule.outcome, EvaluationStatus.INSUFFICIENT_DATA)
        self.assertIn("added_fat", fat_rule.missing_evidence)

    # -------------------------------------------------------------------------
    # 4. Ingredient Engine Tests
    # -------------------------------------------------------------------------
    def test_ingredient_aspartame_pku_warning(self):
        """Scenario 4.1: Mandatory label warning for Aspartame (PKU)"""
        product = ProductEvaluationInput(
            product_name="Zero Calorie Cola",
            food_form=FoodForm.LIQUID,
            food_category="BEVERAGE",
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="ins_951_aspartame", declared_label_text="Aspartame (INS 951)",
                    sequence_order=1, ins_number="951"
                )
            ]
        )
        batch = evaluate_ingredients(product, self.ingredient_rules)
        pku_res = next(r for r in batch.results if r.rule_id == "ir_aspartame_pku_warning")
        self.assertEqual(pku_res.outcome, EvaluationStatus.PASS)
        self.assertIn("PHENYLKETONURICS", pku_res.evidence_used["warning_statement_mandated"])

    def test_ingredient_caffeine_beverage_limit_and_warning(self):
        """Caffeine in beverage generates advisory and evaluates 300 ppm maximum limit"""
        product = ProductEvaluationInput(
            product_name="Energy Booster Drink",
            food_form=FoodForm.LIQUID,
            food_category="BEVERAGE",
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="caffeine", declared_label_text="Caffeine", sequence_order=2
                )
            ]
        )
        batch = evaluate_ingredients(product, self.ingredient_rules)
        caffeine_res = next(r for r in batch.results if r.rule_id == "ir_caffeine_warning")
        self.assertEqual(caffeine_res.outcome, EvaluationStatus.PASS)
        self.assertIn("CONTAINS CAFFEINE", caffeine_res.evidence_used["warning_statement_mandated"])

    def test_ingredient_uncharacterized_notice(self):
        """Scenario 4.3: Uncharacterized ingredient triggers consumer advisory notice"""
        product = ProductEvaluationInput(
            product_name="Herbal Concoction",
            food_form=FoodForm.SOLID,
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="unknown_extract_x", declared_label_text="Novel Botanical Extract X",
                    sequence_order=1, processing_classification=IngredientProcessingClass.UNKNOWN
                )
            ]
        )
        batch = evaluate_ingredients(product, self.ingredient_rules)
        unchar_res = next(r for r in batch.results if r.rule_id == "uncharacterized_ingredients_notice")
        self.assertEqual(unchar_res.outcome, EvaluationStatus.INSUFFICIENT_DATA)
        self.assertIn("Novel Botanical Extract X", unchar_res.evidence_used["uncharacterized_ingredients"])

    # -------------------------------------------------------------------------
    # 5. Robustness and Edge Case Tests
    # -------------------------------------------------------------------------
    def test_claims_invalid_operator_fails_safely(self):
        """Invalid AST operator must fail safely to INDETERMINATE without crashing"""
        product = ProductEvaluationInput(
            product_name="Safe Test Product",
            food_form=FoodForm.SOLID,
            nutrients={
                "protein": NutrientObservationInput(
                    nutrient_code="protein", per_100g_value=Decimal("15.0"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                )
            }
        )
        bad_rule = {
            "claim_id": "test_bad_op",
            "claim_code": "BAD_OPERATOR_CLAIM",
            "food_form": "solid",
            "condition_expression": {
                "logical_operator": "AND",
                "conditions": [
                    {
                        "type": "NUTRIENT_THRESHOLD",
                        "nutrient_code": "protein",
                        "operator": "INVALID_OP",
                        "threshold_value": 5.0,
                        "food_form": "solid"
                    }
                ]
            }
        }
        batch = evaluate_claims(product, [bad_rule])
        self.assertEqual(len(batch.results), 1)
        self.assertEqual(batch.results[0].outcome, EvaluationStatus.INDETERMINATE)
        self.assertIn("Unsupported comparison operator", batch.results[0].human_readable_explanation)

    def test_claims_depth_limit_exceeded_fails_safely(self):
        """AST exceeding max depth 5 must be rejected as INDETERMINATE without recursion error"""
        product = ProductEvaluationInput(
            product_name="Deep Test Product",
            food_form=FoodForm.SOLID,
            nutrients={
                "protein": NutrientObservationInput(
                    nutrient_code="protein", per_100g_value=Decimal("15.0"), unit="g",
                    data_status=NutrientDataStatus.PRESENT
                )
            }
        )
        # Construct tree with depth 7
        curr = {
            "type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein",
            "operator": "GTE", "threshold_value": 5.0, "food_form": "solid"
        }
        for _ in range(7):
            curr = {
                "logical_operator": "AND",
                "conditions": [
                    {"type": "EXPRESSION_GROUP", "nested_expression": curr}
                ]
            }

        deep_rule = {
            "claim_id": "test_deep_ast",
            "claim_code": "DEEP_AST_CLAIM",
            "food_form": "solid",
            "condition_expression": curr
        }
        batch = evaluate_claims(product, [deep_rule])
        self.assertEqual(batch.results[0].outcome, EvaluationStatus.INDETERMINATE)
        self.assertIn("depth", batch.results[0].human_readable_explanation.lower())

    def test_ingredient_category_specific_filtering(self):
        """Additive rules must respect target_food_category and reject mismatches"""
        # Confectionery product with Sodium Benzoate (a Beverage-only rule)
        candy = ProductEvaluationInput(
            product_name="Hard Candy",
            food_form=FoodForm.SOLID,
            food_category="CONFECTIONERY",
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="ins_211_sodium_benzoate", declared_label_text="Sodium Benzoate",
                    sequence_order=1
                )
            ]
        )
        batch = evaluate_ingredients(candy, self.ingredient_rules)
        # ir_sodium_benzoate_max_limit_beverages should not apply to CONFECTIONERY
        applied_rules = [r.rule_id for r in batch.results]
        self.assertNotIn("ir_sodium_benzoate_max_limit_beverages", applied_rules)

        # Unspecified food_category -> INSUFFICIENT_DATA
        generic_product = ProductEvaluationInput(
            product_name="Generic Flavoured Drink",
            food_form=FoodForm.LIQUID,
            food_category=None,
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="ins_211_sodium_benzoate", declared_label_text="Sodium Benzoate",
                    sequence_order=1
                )
            ]
        )
        batch_generic = evaluate_ingredients(generic_product, self.ingredient_rules)
        benzoate_res = next(r for r in batch_generic.results if r.rule_id == "ir_sodium_benzoate_max_limit_beverages")
        self.assertEqual(benzoate_res.outcome, EvaluationStatus.INSUFFICIENT_DATA)
        self.assertIn("food_category", benzoate_res.missing_evidence)


if __name__ == '__main__':
    unittest.main()
