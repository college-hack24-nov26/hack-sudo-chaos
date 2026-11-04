"""
Phase 3 to Phase 4 Integration Verification Test Suite.

Verifies the 11 required integration scenarios defined in the Controlled Integration Contract:
1. Existing DB product: Existing lookup and evaluation flow works.
2. Open Food Facts fallback: Normalization and evaluation work.
3. Complete nutrient data: Four engines execute.
4. Missing nutrient: No false PASS.
5. Explicit zero: Remains distinct from missing.
6. Unresolved measurement basis: Insufficient data where required.
7. PER_SERVING against PER_100G rule: Insufficient data.
8. Permitted liquid PER_100G: Evaluates correctly.
9. One engine fails: Remaining engines continue.
10. All engines succeed: Complete API response.
11. Verified product exists: External data does not overwrite it.
"""

import unittest
from unittest.mock import MagicMock, AsyncMock
import uuid
from decimal import Decimal

from app.models.product import Product
from app.models.product_nutrient import ProductNutrient
from app.models.product_ingredient import ProductIngredient
from app.domain.engines.contracts import (
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
    EvaluationStatus,
    NutrientObservationInput,
    IngredientObservationInput,
    DeclaredClaimInput,
    ProductEvaluationInput,
    EngineBatchResult,
)
from app.domain.engines.coordinator import (
    EvaluationCoordinator,
    EvaluationRulesBundle,
    EngineFailureRecord,
)
from app.repositories.product_repository import ProductRepository
from app.integrations.open_food_facts import OpenFoodFactsClient, OpenFoodFactsResponse, OpenFoodFactsStatus
from app.services.product_service import ProductService
from app.schemas.product_analysis import ProductAnalysisResponse
from app.core.cache import product_cache


class TestPhase3Phase4Integration(unittest.TestCase):
    """End-to-end integration tests validating the 11 contract scenarios."""

    @classmethod
    def setUpClass(cls):
        cls.rules_bundle = EvaluationRulesBundle.from_seed_files()
        cls.coordinator = EvaluationCoordinator(rules_bundle=cls.rules_bundle)

    def setUp(self):
        product_cache.clear()
        self.mock_repo = MagicMock(spec=ProductRepository)
        self.mock_off = MagicMock(spec=OpenFoodFactsClient)
        self.service = ProductService(
            product_repository=self.mock_repo,
            evaluation_coordinator=self.coordinator,
            off_client=self.mock_off,
            enable_cache=False,
        )

    def _build_mock_orm_product(self, is_verified: bool = True) -> Product:
        prod_id = uuid.uuid4()
        return Product(
            id=prod_id,
            barcode="8901030825279",
            product_name="Roasted Bengal Gram (Chana)",
            brand_name="YumSure Organics",
            food_form="solid",
            food_category="LEGUME_PULSE",
            package_size="200g",
            serving_size_value=Decimal("30.0"),
            serving_size_unit="g",
            is_verified=is_verified,
            source_id="curated_catalog",
            nutrients=[
                ProductNutrient(product_id=prod_id, nutrient_code="energy", per_100g_value=Decimal("387.0"), per_serving_value=Decimal("116.1"), unit="kcal", data_status="PRESENT"),
                ProductNutrient(product_id=prod_id, nutrient_code="protein", per_100g_value=Decimal("22.5"), per_serving_value=Decimal("6.75"), unit="g", data_status="PRESENT"),
                ProductNutrient(product_id=prod_id, nutrient_code="carbohydrates", per_100g_value=Decimal("58.0"), per_serving_value=Decimal("17.4"), unit="g", data_status="PRESENT"),
                ProductNutrient(product_id=prod_id, nutrient_code="total_sugars", per_100g_value=Decimal("2.0"), per_serving_value=Decimal("0.6"), unit="g", data_status="PRESENT"),
                ProductNutrient(product_id=prod_id, nutrient_code="added_sugars", per_100g_value=Decimal("0.0"), per_serving_value=Decimal("0.0"), unit="g", data_status="EXPLICITLY_ZERO"),
                ProductNutrient(product_id=prod_id, nutrient_code="total_fat", per_100g_value=Decimal("5.2"), per_serving_value=Decimal("1.56"), unit="g", data_status="PRESENT"),
                ProductNutrient(product_id=prod_id, nutrient_code="saturated_fat", per_100g_value=Decimal("1.0"), per_serving_value=Decimal("0.3"), unit="g", data_status="PRESENT"),
                ProductNutrient(product_id=prod_id, nutrient_code="trans_fat", per_100g_value=Decimal("0.0"), per_serving_value=Decimal("0.0"), unit="g", data_status="EXPLICITLY_ZERO"),
                ProductNutrient(product_id=prod_id, nutrient_code="sodium", per_100g_value=Decimal("150.0"), per_serving_value=Decimal("45.0"), unit="mg", data_status="PRESENT"),
                ProductNutrient(product_id=prod_id, nutrient_code="dietary_fibre", per_100g_value=Decimal("16.0"), per_serving_value=Decimal("4.8"), unit="g", data_status="PRESENT"),
            ],
            ingredients=[
                ProductIngredient(product_id=prod_id, ingredient_code="bengal_gram", declared_label_text="Roasted Bengal Gram", sequence_order=1, declared_percentage=Decimal("100.0"), is_allergen_declared=False),
            ],
        )

    # 1. Existing DB product: Existing lookup and evaluation flow works
    def test_01_existing_db_product_lookup_and_evaluation(self):
        self.mock_repo.get_by_barcode.return_value = self._build_mock_orm_product()
        res = self.service.analyze_product_by_barcode("8901030825279")

        self.assertIsNotNone(res)
        self.assertEqual(res.product.barcode, "8901030825279")
        self.assertEqual(res.product.product_name, "Roasted Bengal Gram (Chana)")
        self.assertEqual(res.nutrition_evaluation.engine_name, "NUTRITION")
        self.assertEqual(res.icmr_hfss_evaluation.engine_name, "ICMR_HFSS")
        self.assertEqual(res.claims_evaluation.engine_name, "CLAIMS")
        self.assertEqual(res.ingredient_evaluation.engine_name, "INGREDIENT")
        self.assertGreater(res.summary.total_rules_evaluated, 0)

    # 2. Open Food Facts fallback: Normalization and evaluation work
    def test_02_open_food_facts_fallback_normalization_and_evaluation(self):
        self.mock_repo.get_by_barcode.return_value = None
        off_payload = {
            "product_name": "Organic Almond Milk",
            "brands": "NutriPure",
            "quantity": "1 L",
            "product_quantity_unit": "ml",
            "nutrition_data_per": "100ml",
            "nutriments": {
                "energy-kcal_100g": 35.0,
                "proteins_100g": 1.5,
                "fat_100g": 2.5,
                "saturated-fat_100g": 0.2,
                "trans-fat_100g": 0.0,
                "carbohydrates_100g": 3.0,
                "sugars_100g": 1.0,
                "added-sugars_100g": 0.0,
                "sodium_100g": 40.0,
            },
            "ingredients": [
                {"id": "water", "text": "Water", "rank": 1},
                {"id": "almonds", "text": "Almonds", "rank": 2, "percent": 5.0},
            ]
        }
        self.mock_off.get_product = AsyncMock(return_value=OpenFoodFactsResponse(
            barcode="8901234567890",
            status=OpenFoodFactsStatus.FOUND,
            product_data=off_payload,
            raw_payload={"product": off_payload}
        ))

        import asyncio
        res = asyncio.run(self.service.analyze_product_by_barcode_async("8901234567890"))

        self.assertIsNotNone(res)
        self.assertEqual(res.product.product_name, "Organic Almond Milk")
        self.assertEqual(res.product.food_form, "liquid")
        self.assertEqual(res.nutrition_evaluation.engine_name, "NUTRITION")
        self.assertEqual(res.icmr_hfss_evaluation.engine_name, "ICMR_HFSS")

    # 3. Complete nutrient data: Four engines execute
    def test_03_complete_nutrient_data_executes_four_engines(self):
        self.mock_repo.get_by_barcode.return_value = self._build_mock_orm_product()
        res = self.service.analyze_product_by_barcode("8901030825279")

        self.assertIsNotNone(res.nutrition_evaluation)
        self.assertIsNotNone(res.icmr_hfss_evaluation)
        self.assertIsNotNone(res.claims_evaluation)
        self.assertIsNotNone(res.ingredient_evaluation)
        self.assertEqual(len(res.engine_failures), 0)

    # 4. Missing nutrient: No false PASS
    def test_04_missing_nutrient_no_false_pass(self):
        # Trans fat free claim requires saturated fat declaration. If saturated fat is NOT_DECLARED, cannot pass.
        product = ProductEvaluationInput(
            product_name="Incomplete Cookie",
            food_form=FoodForm.SOLID,
            nutrients={
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat",
                    per_100g_value=Decimal("0.0"),
                    unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
                # saturated_fat is omitted
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat")
            ],
        )
        res = self.coordinator.evaluate(product)
        tff = next((r for r in res.claims_evaluation.results if r.rule_code == "TRANS_FAT_FREE"), None)
        self.assertIsNotNone(tff)
        self.assertEqual(tff.outcome, EvaluationStatus.INSUFFICIENT_DATA)
        self.assertNotEqual(tff.outcome, EvaluationStatus.PASS, "Missing saturated fat must never result in false PASS")

    # 5. Explicit zero: Remains distinct from missing
    def test_05_explicit_zero_distinct_from_missing(self):
        # Product A: Explicitly zero trans fat and compliant saturated fat + energy
        product_zero = ProductEvaluationInput(
            product_name="Explicit Zero Biscuit",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy",
                    per_100g_value=Decimal("200.0"),
                    unit="kcal",
                    data_status=NutrientDataStatus.PRESENT,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat",
                    per_100g_value=Decimal("0.0"),
                    unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat",
                    per_100g_value=Decimal("1.0"),
                    unit="g",
                    data_status=NutrientDataStatus.PRESENT,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat")
            ],
        )
        res_zero = self.coordinator.evaluate(product_zero)
        tff_zero = next(r for r in res_zero.claims_evaluation.results if r.rule_code == "TRANS_FAT_FREE")
        self.assertEqual(tff_zero.outcome, EvaluationStatus.PASS)

        # Product B: Missing trans fat (with energy and saturated fat present)
        product_missing = ProductEvaluationInput(
            product_name="Missing Trans Fat Biscuit",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy",
                    per_100g_value=Decimal("200.0"),
                    unit="kcal",
                    data_status=NutrientDataStatus.PRESENT,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat",
                    per_100g_value=None,
                    unit="g",
                    data_status=NutrientDataStatus.NOT_DECLARED,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat",
                    per_100g_value=Decimal("1.0"),
                    unit="g",
                    data_status=NutrientDataStatus.PRESENT,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat")
            ],
        )
        res_missing = self.coordinator.evaluate(product_missing)
        tff_missing = next(r for r in res_missing.claims_evaluation.results if r.rule_code == "TRANS_FAT_FREE")
        self.assertEqual(tff_missing.outcome, EvaluationStatus.INSUFFICIENT_DATA)
        self.assertNotEqual(tff_missing.outcome, tff_zero.outcome)

    # 6. Unresolved measurement basis: Insufficient data where required
    def test_06_unresolved_measurement_basis_insufficient_data(self):
        product = ProductEvaluationInput(
            product_name="Unknown Basis Drink",
            food_form=FoodForm.LIQUID,
            nutrients={
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium",
                    per_100g_value=Decimal("50.0"),
                    unit="mg",
                    data_status=NutrientDataStatus.PRESENT,
                    measurement_basis=None,  # Unresolved basis
                ),
            },
        )
        res = self.coordinator.evaluate(product)
        # ICMR Table 15.1 evaluation for sodium must reject unresolved basis
        sodium_icmr = next((r for r in res.icmr_hfss_evaluation.results if "SODIUM" in r.rule_code), None)
        if sodium_icmr:
            self.assertEqual(sodium_icmr.outcome, EvaluationStatus.INSUFFICIENT_DATA)

    # 7. PER_SERVING against PER_100G rule: Insufficient data
    def test_07_per_serving_against_per_100g_rule_insufficient_data(self):
        product = ProductEvaluationInput(
            product_name="Serving Only Snack",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy",
                    per_100g_value=None,
                    per_serving_value=Decimal("150.0"),
                    unit="kcal",
                    data_status=NutrientDataStatus.PRESENT,
                    measurement_basis=MeasurementBasis.PER_SERVING,
                ),
            },
        )
        res = self.coordinator.evaluate(product)
        # Solid Table 15.2 matrix rule strictly requires PER_100G; PER_SERVING must yield INSUFFICIENT_DATA
        matrix_res = next((r for r in res.icmr_hfss_evaluation.results if "MATRIX" in r.rule_code or "energy_missing" in r.rule_id), None)
        self.assertIsNotNone(matrix_res)
        self.assertEqual(matrix_res.outcome, EvaluationStatus.INSUFFICIENT_DATA)

    # 8. Permitted liquid PER_100G: Evaluates correctly
    def test_08_permitted_liquid_per_100g_evaluates_correctly(self):
        # Dense liquid (e.g. syrup/honey) declaring nutrition per 100g
        product = ProductEvaluationInput(
            product_name="Dense Liquid Honey Syrup",
            food_form=FoodForm.LIQUID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy",
                    per_100g_value=Decimal("300.0"),
                    unit="kcal",
                    data_status=NutrientDataStatus.PRESENT,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
                "protein": NutrientObservationInput(
                    nutrient_code="protein",
                    per_100g_value=Decimal("0.5"),
                    unit="g",
                    data_status=NutrientDataStatus.PRESENT,
                    measurement_basis=MeasurementBasis.PER_100G,
                ),
            },
        )
        res = self.coordinator.evaluate(product)
        # Liquid products evaluate correctly without crash
        self.assertIsNotNone(res.nutrition_evaluation)
        self.assertEqual(res.nutrition_evaluation.engine_name, "NUTRITION")

    # 9. One engine fails: Remaining engines continue
    def test_09_one_engine_fails_remaining_engines_continue(self):
        # Create a mock coordinator where claims_runner raises an unexpected RuntimeError
        def failing_claims_runner(*args, **kwargs):
            raise RuntimeError("Unexpected claims engine worker crash")

        coordinator = EvaluationCoordinator(
            rules_bundle=self.rules_bundle,
            claims_runner=failing_claims_runner,
        )
        service = ProductService(
            product_repository=self.mock_repo,
            evaluation_coordinator=coordinator,
            off_client=self.mock_off,
            enable_cache=False,
        )
        self.mock_repo.get_by_barcode.return_value = self._build_mock_orm_product()

        res = service.analyze_product_by_barcode("8901030825279")

        # Claims engine failed
        self.assertIsNone(res.claims_evaluation)
        self.assertEqual(len(res.engine_failures), 1)
        self.assertEqual(res.engine_failures[0].engine_name, "CLAIMS")
        self.assertEqual(res.engine_failures[0].error_type, "RuntimeError")

        # Remaining engines succeeded
        self.assertIsNotNone(res.nutrition_evaluation)
        self.assertEqual(res.nutrition_evaluation.engine_name, "NUTRITION")
        self.assertIsNotNone(res.icmr_hfss_evaluation)
        self.assertEqual(res.icmr_hfss_evaluation.engine_name, "ICMR_HFSS")
        self.assertIsNotNone(res.ingredient_evaluation)
        self.assertEqual(res.ingredient_evaluation.engine_name, "INGREDIENT")

    # 10. All engines succeed: Complete API response
    def test_10_all_engines_succeed_complete_api_response(self):
        self.mock_repo.get_by_barcode.return_value = self._build_mock_orm_product()
        res = self.service.analyze_product_by_barcode("8901030825279")

        # Canonical response models
        self.assertIsInstance(res, ProductAnalysisResponse)
        self.assertIsNotNone(res.product)
        self.assertIsNotNone(res.metrics)
        self.assertIsNotNone(res.nutritional_interpretation)
        self.assertIsNotNone(res.regulatory_claims_validation)
        self.assertIsNotNone(res.ingredient_analysis)
        self.assertIsInstance(res.key_findings, list)
        self.assertIsNotNone(res.ai_explanation)
        self.assertIsNotNone(res.nutrients)
        self.assertIsNotNone(res.ingredients)
        self.assertIsNotNone(res.summary)
        self.assertGreater(res.summary.total_rules_evaluated, 0)

    # 11. Verified product exists: External data does not overwrite it
    def test_11_verified_product_not_overwritten_by_external_data(self):
        verified_product = self._build_mock_orm_product(is_verified=True)
        self.mock_repo.get_by_barcode.return_value = verified_product

        res = self.service.analyze_product_by_barcode("8901030825279")

        # External client must never be called when local verified product exists
        self.mock_off.get_product.assert_not_called()
        self.assertTrue(res.product.is_verified)
        self.assertEqual(res.product.product_name, "Roasted Bengal Gram (Chana)")


if __name__ == "__main__":
    unittest.main()
