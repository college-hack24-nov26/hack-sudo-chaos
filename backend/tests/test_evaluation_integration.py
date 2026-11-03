"""
YumSure Phase 3 — Evaluation Coordinator Integration Test Suite.

Deterministic, offline tests verifying the orchestration of all four engines:
- NutritionEngine
- ICMRHFSSEngine
- ClaimsEngine
- IngredientEngine

Zero dependencies on PostgreSQL, Supabase, or external networks.
100% deterministic test fixtures.
"""

import json
import os
import unittest
from decimal import Decimal
from copy import deepcopy

from app.domain.engines.contracts import (
    ProductEvaluationInput,
    NutrientObservationInput,
    IngredientObservationInput,
    DeclaredClaimInput,
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
    EvaluationStatus,
    IngredientProcessingClass,
    IngredientSugarClass,
    EngineBatchResult,
)
from app.domain.engines.coordinator import (
    EvaluationCoordinator,
    EvaluationRulesBundle,
    EngineFailureRecord,
    CoordinatorEvaluationResult,
)


class TestEvaluationCoordinatorIntegration(unittest.TestCase):
    """Deterministic integration tests for EvaluationCoordinator across all 14 scenarios."""

    @classmethod
    def setUpClass(cls):
        """Load deterministic seed rule datasets from local JSON files."""
        seed_dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "app", "data", "seeds")
        )
        with open(os.path.join(seed_dir, "icmr_table_15_1_seed.json"), "r", encoding="utf-8") as f:
            icmr_15_1 = json.load(f)
        with open(os.path.join(seed_dir, "icmr_table_15_2_seed.json"), "r", encoding="utf-8") as f:
            icmr_15_2 = json.load(f)
        with open(os.path.join(seed_dir, "fssai_schedule_i_claims_seed.json"), "r", encoding="utf-8") as f:
            claims = json.load(f)
        with open(os.path.join(seed_dir, "fssai_schedule_ii_synonyms_seed.json"), "r", encoding="utf-8") as f:
            synonyms = json.load(f)
        with open(os.path.join(seed_dir, "ingredient_rules_seed.json"), "r", encoding="utf-8") as f:
            ingredients = json.load(f)

        cls.rules_bundle = EvaluationRulesBundle(
            icmr_threshold_rules=icmr_15_1,
            icmr_matrix_rules=icmr_15_2,
            claims_rules=claims,
            synonym_registry=synonyms,
            ingredient_rules=ingredients,
        )

    def _create_complete_solid_product(self) -> ProductEvaluationInput:
        """Fixture: Complete Roasted Bengal Gram (Solid whole food, compliant)."""
        return ProductEvaluationInput(
            product_id="prod_roasted_chana_001",
            product_name="Traditional Roasted Bengal Gram",
            brand_name="DesiHarvest",
            food_form=FoodForm.SOLID,
            food_category="CEREAL_PULSE_PRODUCT",
            package_size="200g",
            serving_size_value=Decimal("30.0"),
            serving_size_unit="g",
            nutrients={
                "energy": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="energy", per_100g_value=Decimal("380.0"), per_serving_value=Decimal("114.0"),
                    unit="kcal", data_status=NutrientDataStatus.PRESENT
                ),
                "protein": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="protein", per_100g_value=Decimal("19.5"), per_serving_value=Decimal("5.85"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "carbohydrates": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="carbohydrates", per_100g_value=Decimal("58.0"), per_serving_value=Decimal("17.4"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "total_sugars": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="total_sugars", per_100g_value=Decimal("2.5"), per_serving_value=Decimal("0.75"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "added_sugars": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="added_sugars", per_100g_value=Decimal("0.0"), per_serving_value=Decimal("0.0"),
                    unit="g", data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
                "total_fat": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="total_fat", per_100g_value=Decimal("5.2"), per_serving_value=Decimal("1.56"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "saturated_fat": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="saturated_fat", per_100g_value=Decimal("0.8"), per_serving_value=Decimal("0.24"),
                    unit="g", data_status=NutrientDataStatus.PRESENT
                ),
                "trans_fat": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="trans_fat", per_100g_value=Decimal("0.0"), per_serving_value=Decimal("0.0"),
                    unit="g", data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
                "sodium": NutrientObservationInput(
                    measurement_basis=MeasurementBasis.PER_100G, nutrient_code="sodium", per_100g_value=Decimal("12.0"), per_serving_value=Decimal("3.6"),
                    unit="mg", data_status=NutrientDataStatus.PRESENT
                ),
            },
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="bengal_gram",
                    declared_label_text="Roasted Bengal Gram (Chana)",
                    sequence_order=1,
                    declared_percentage=Decimal("98.0"),
                    processing_classification=IngredientProcessingClass.WHOLE_FOOD,
                    sugar_classification=IngredientSugarClass.NOT_SUGAR
                ),
                IngredientObservationInput(
                    ingredient_code="turmeric_powder",
                    declared_label_text="Turmeric",
                    sequence_order=2,
                    processing_classification=IngredientProcessingClass.WHOLE_FOOD,
                    sugar_classification=IngredientSugarClass.NOT_SUGAR
                ),
            ],
            declared_claims=[
                DeclaredClaimInput(
                    claim_code="TRANS_FAT_FREE",
                    raw_label_statement="Zero Trans Fat"
                )
            ]
        )

    # -------------------------------------------------------------------------
    # Scenario 1: All four engines complete successfully
    # -------------------------------------------------------------------------
    def test_01_all_four_engines_complete_successfully(self):
        """Scenario 1: Coordinator executes all 4 engines and returns complete results."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        result = coordinator.evaluate(product)

        self.assertIsInstance(result, CoordinatorEvaluationResult)
        self.assertEqual(result.product_id, "prod_roasted_chana_001")
        self.assertEqual(result.product_name, "Traditional Roasted Bengal Gram")
        self.assertEqual(result.food_form, FoodForm.SOLID)

        # All four engine outputs must be present and non-null
        self.assertIsNotNone(result.nutrition_evaluation)
        self.assertEqual(result.nutrition_evaluation.engine_name, "NUTRITION")
        self.assertIsNotNone(result.icmr_hfss_evaluation)
        self.assertEqual(result.icmr_hfss_evaluation.engine_name, "ICMR_HFSS")
        self.assertIsNotNone(result.claims_evaluation)
        self.assertEqual(result.claims_evaluation.engine_name, "CLAIMS")
        self.assertIsNotNone(result.ingredient_evaluation)
        self.assertEqual(result.ingredient_evaluation.engine_name, "INGREDIENT")

        # Zero execution failures
        self.assertEqual(len(result.engine_failures), 0)

        # Results contain atomic evaluations
        self.assertGreater(len(result.nutrition_evaluation.results), 0)
        self.assertGreater(len(result.icmr_hfss_evaluation.results), 0)
        self.assertGreater(len(result.claims_evaluation.results), 0)

    # -------------------------------------------------------------------------
    # Scenario 2: Product with missing nutrient declarations
    # -------------------------------------------------------------------------
    def test_02_product_with_missing_nutrient_declarations(self):
        """Scenario 2: Missing mandatory nutrients emit INSUFFICIENT_DATA and do not crash."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        # Mark trans_fat and sodium as NOT_DECLARED with None values
        product.nutrients["trans_fat"] = NutrientObservationInput(
            measurement_basis=MeasurementBasis.PER_100G, nutrient_code="trans_fat", per_100g_value=None, per_serving_value=None,
            unit="g", data_status=NutrientDataStatus.NOT_DECLARED
        )
        product.nutrients["sodium"] = NutrientObservationInput(
            measurement_basis=MeasurementBasis.PER_100G, nutrient_code="sodium", per_100g_value=None, per_serving_value=None,
            unit="mg", data_status=NutrientDataStatus.NOT_DECLARED
        )

        result = coordinator.evaluate(product)

        self.assertIsNotNone(result.nutrition_evaluation)
        self.assertIsNotNone(result.claims_evaluation)

        # Missing mandatory nutrient notices in nutrition engine
        missing_rules = [
            r for r in result.nutrition_evaluation.results
            if r.outcome == EvaluationStatus.INSUFFICIENT_DATA
        ]
        self.assertGreaterEqual(len(missing_rules), 2)

        # Summary outcome counts must include INSUFFICIENT_DATA
        self.assertGreater(result.summary.by_outcome[EvaluationStatus.INSUFFICIENT_DATA], 0)

    # -------------------------------------------------------------------------
    # Scenario 3: Explicitly zero nutrient values
    # -------------------------------------------------------------------------
    def test_03_explicitly_zero_nutrient_values(self):
        """Scenario 3: EXPLICITLY_ZERO (0g declared on pack) substantiates claims."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        # Both added_sugars and trans_fat explicitly 0.0
        product.nutrients["trans_fat"] = NutrientObservationInput(
            measurement_basis=MeasurementBasis.PER_100G, nutrient_code="trans_fat", per_100g_value=Decimal("0.0"), per_serving_value=Decimal("0.0"),
            unit="g", data_status=NutrientDataStatus.EXPLICITLY_ZERO
        )
        product.nutrients["saturated_fat"] = NutrientObservationInput(
            measurement_basis=MeasurementBasis.PER_100G, nutrient_code="saturated_fat", per_100g_value=Decimal("0.5"), per_serving_value=Decimal("0.15"),
            unit="g", data_status=NutrientDataStatus.PRESENT
        )

        result = coordinator.evaluate(product)

        # Claim 'Zero Trans Fat' should PASS
        claim_result = next(
            (r for r in result.claims_evaluation.results if "TRANS_FAT_FREE" in r.rule_code),
            None
        )
        self.assertIsNotNone(claim_result)
        self.assertEqual(claim_result.outcome, EvaluationStatus.PASS)

    # -------------------------------------------------------------------------
    # Scenario 4: Unknown nutrient observations
    # -------------------------------------------------------------------------
    def test_04_unknown_nutrient_observations(self):
        """Scenario 4: Corrupted or unreadable OCR (UNKNOWN) emits INSUFFICIENT_DATA."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        product.nutrients["saturated_fat"] = NutrientObservationInput(
            measurement_basis=MeasurementBasis.PER_100G, nutrient_code="saturated_fat", per_100g_value=None, per_serving_value=None,
            unit="g", data_status=NutrientDataStatus.UNKNOWN
        )

        result = coordinator.evaluate(product)

        # Trans fat free claim condition requires saturated fat <= 1.5g.
        # With saturated fat UNKNOWN, claim condition cannot be evaluated -> INSUFFICIENT_DATA
        claim_result = next(
            (r for r in result.claims_evaluation.results if "TRANS_FAT_FREE" in r.rule_code),
            None
        )
        self.assertIsNotNone(claim_result)
        self.assertEqual(claim_result.outcome, EvaluationStatus.INSUFFICIENT_DATA)

    # -------------------------------------------------------------------------
    # Scenario 5: Invalid measurement basis
    # -------------------------------------------------------------------------
    def test_05_invalid_measurement_basis(self):
        """Scenario 5: Nutrient observation with invalid measurement basis raises ValueError."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        # Attach an invalid measurement basis dynamically to test validation guard
        product.nutrients["protein"].measurement_basis = "PER_SPOON"

        with self.assertRaises(ValueError) as ctx:
            coordinator.evaluate(product)
        self.assertIn("Invalid measurement basis", str(ctx.exception))

    # -------------------------------------------------------------------------
    # Scenario 6: Invalid product input
    # -------------------------------------------------------------------------
    def test_06_invalid_product_input(self):
        """Scenario 6: Passing None or invalid types raises ValueError / TypeError."""
        coordinator = EvaluationCoordinator(self.rules_bundle)

        with self.assertRaises(ValueError):
            coordinator.evaluate(None)

        with self.assertRaises(TypeError):
            coordinator.evaluate("not a product")

        with self.assertRaises(TypeError):
            coordinator.evaluate({"product_name": "dict product"})

    # -------------------------------------------------------------------------
    # Scenario 7: INSUFFICIENT_DATA returned by an engine
    # -------------------------------------------------------------------------
    def test_07_insufficient_data_aggregation(self):
        """Scenario 7: INSUFFICIENT_DATA from engines is correctly aggregated in summary counts."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        # Omit energy entirely so ICMR Table 15.2 cannot determine calorie category
        del product.nutrients["energy"]

        result = coordinator.evaluate(product)

        # ICMR engine must emit INSUFFICIENT_DATA for missing energy
        icmr_matrix_res = next(
            (r for r in result.icmr_hfss_evaluation.results if "MATRIX" in r.rule_code or "energy_missing" in r.rule_id),
            None
        )
        self.assertIsNotNone(icmr_matrix_res)
        self.assertEqual(icmr_matrix_res.outcome, EvaluationStatus.INSUFFICIENT_DATA)
        self.assertGreater(result.summary.by_outcome[EvaluationStatus.INSUFFICIENT_DATA], 0)

    # -------------------------------------------------------------------------
    # Scenario 8: INDETERMINATE returned by an engine
    # -------------------------------------------------------------------------
    def test_08_indeterminate_aggregation(self):
        """Scenario 8: Ambiguous ingredients emit INDETERMINATE and aggregate cleanly."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        # Add functional additive with no other markers -> ICMR engine marks processing group indeterminate
        product.ingredients.append(
            IngredientObservationInput(
                ingredient_code="xanthan_gum",
                declared_label_text="Xanthan Gum (INS 415)",
                sequence_order=3,
                processing_classification=IngredientProcessingClass.FUNCTIONAL_ADDITIVE
            )
        )

        result = coordinator.evaluate(product)

        icmr_results = result.icmr_hfss_evaluation.results
        has_indeterminate = any(r.outcome == EvaluationStatus.INDETERMINATE for r in icmr_results)
        self.assertTrue(has_indeterminate)
        self.assertGreater(result.summary.by_outcome[EvaluationStatus.INDETERMINATE], 0)

    # -------------------------------------------------------------------------
    # Scenario 9: One engine raises an exception
    # -------------------------------------------------------------------------
    def test_09_one_engine_raises_exception_isolation(self):
        """Scenario 9: If one engine crashes, it is recorded in engine_failures, not regulatory outcomes."""
        def crashing_nutrition(prod, **kwargs):
            raise ZeroDivisionError("Simulated divide by zero in nutrition engine")

        coordinator = EvaluationCoordinator(
            self.rules_bundle,
            nutrition_runner=crashing_nutrition
        )
        product = self._create_complete_solid_product()

        result = coordinator.evaluate(product)

        # Nutrition failed
        self.assertIsNone(result.nutrition_evaluation)
        self.assertEqual(len(result.engine_failures), 1)
        failure = result.engine_failures[0]
        self.assertEqual(failure.engine_name, "NUTRITION")
        self.assertEqual(failure.error_type, "ZeroDivisionError")
        self.assertIn("Engine execution error", failure.message)

        # Did NOT convert failure to regulatory PASS/FAIL
        self.assertNotIn("ZeroDivisionError", str(result.summary.by_outcome))

    # -------------------------------------------------------------------------
    # Scenario 10: Multiple engines raise exceptions
    # -------------------------------------------------------------------------
    def test_10_multiple_engines_raise_exceptions(self):
        """Scenario 10: Multiple failing engines are all captured without crashing coordinator."""
        def crashing_nutrition(prod, **kwargs):
            raise KeyError("missing_key")

        def crashing_claims(prod, **kwargs):
            raise RuntimeError("AST recursion limit")

        coordinator = EvaluationCoordinator(
            self.rules_bundle,
            nutrition_runner=crashing_nutrition,
            claims_runner=crashing_claims
        )
        product = self._create_complete_solid_product()

        result = coordinator.evaluate(product)

        self.assertIsNone(result.nutrition_evaluation)
        self.assertIsNone(result.claims_evaluation)
        self.assertEqual(len(result.engine_failures), 2)
        failed_engines = {f.engine_name for f in result.engine_failures}
        self.assertEqual(failed_engines, {"NUTRITION", "CLAIMS"})

    # -------------------------------------------------------------------------
    # Scenario 11: Remaining engines still execute after one failure
    # -------------------------------------------------------------------------
    def test_11_remaining_engines_execute_after_failure(self):
        """Scenario 11: Successful engines complete even when another engine fails."""
        def crashing_nutrition(prod, **kwargs):
            raise ValueError("Bad nutrient value")

        coordinator = EvaluationCoordinator(
            self.rules_bundle,
            nutrition_runner=crashing_nutrition
        )
        product = self._create_complete_solid_product()

        result = coordinator.evaluate(product)

        self.assertIsNone(result.nutrition_evaluation)
        self.assertIsNotNone(result.icmr_hfss_evaluation)
        self.assertIsNotNone(result.claims_evaluation)
        self.assertIsNotNone(result.ingredient_evaluation)

        # The successful engines' results are populated and valid
        self.assertGreater(len(result.icmr_hfss_evaluation.results), 0)
        self.assertGreater(len(result.claims_evaluation.results), 0)

    # -------------------------------------------------------------------------
    # Scenario 12: Aggregate outcome counts match actual atomic results
    # -------------------------------------------------------------------------
    def test_12_aggregate_outcome_counts_match_atomic_results(self):
        """Scenario 12: Total rules count equals sum of all results across all successful engines."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        result = coordinator.evaluate(product)

        all_results = []
        for batch in (
            result.nutrition_evaluation,
            result.icmr_hfss_evaluation,
            result.claims_evaluation,
            result.ingredient_evaluation,
        ):
            if batch and batch.results:
                all_results.extend(batch.results)

        # 1. Total count matches
        self.assertEqual(result.summary.total_rules_evaluated, len(all_results))

        # 2. Outcome breakdown matches exact manual count
        expected_counts = {
            status: sum(1 for r in all_results if r.outcome == status)
            for status in EvaluationStatus
        }
        for status in EvaluationStatus:
            self.assertEqual(
                result.summary.by_outcome[status],
                expected_counts[status],
                f"Mismatch for status {status}"
            )

        # 3. Sum of all outcome buckets equals total_rules_evaluated
        self.assertEqual(
            sum(result.summary.by_outcome.values()),
            result.summary.total_rules_evaluated
        )

    # -------------------------------------------------------------------------
    # Scenario 13: No composite score is produced
    # -------------------------------------------------------------------------
    def test_13_no_composite_health_score(self):
        """Scenario 13: Strict prohibition against health scores, star ratings, or letter grades."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        result = coordinator.evaluate(product)

        # Verify no prohibited composite score attributes exist on result or summary
        prohibited_attrs = [
            "score", "health_score", "overall_score", "grade", "health_grade",
            "stars", "star_rating", "rating", "composite_score", "traffic_light"
        ]
        for attr in prohibited_attrs:
            self.assertFalse(hasattr(result, attr), f"Prohibited attribute '{attr}' found on result")
            self.assertFalse(hasattr(result.summary, attr), f"Prohibited attribute '{attr}' found on summary")

        # Result dump should have no composite score keys
        dump = result.model_dump()
        for attr in prohibited_attrs:
            self.assertNotIn(attr, dump)
            self.assertNotIn(attr, dump.get("summary", {}))

    # -------------------------------------------------------------------------
    # Scenario 14: Repeated evaluations do not mutate shared rule data or product input
    # -------------------------------------------------------------------------
    def test_14_immutability_across_repeated_evaluations(self):
        """Scenario 14: Repeated evaluate calls never mutate product or rules bundle."""
        coordinator = EvaluationCoordinator(self.rules_bundle)
        product = self._create_complete_solid_product()

        # Capture snapshot before evaluations
        initial_product_dict = deepcopy(product.model_dump())
        initial_rules_dict = deepcopy(self.rules_bundle.model_dump())

        # Evaluate 5 times consecutively
        results = [coordinator.evaluate(product) for _ in range(5)]

        # Check immutability of inputs
        self.assertEqual(product.model_dump(), initial_product_dict)
        self.assertEqual(self.rules_bundle.model_dump(), initial_rules_dict)

        # Check determinism: all 5 runs produce identical outcome counts
        first_summary = results[0].summary.model_dump()
        for i, res in enumerate(results[1:], start=2):
            self.assertEqual(
                res.summary.model_dump(),
                first_summary,
                f"Evaluation {i} produced different summary counts"
            )


if __name__ == "__main__":
    unittest.main()
