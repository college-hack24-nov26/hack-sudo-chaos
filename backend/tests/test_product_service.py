"""
Unit Tests for ProductService.

Verifies:
1. Product retrieval and domain mapping coordination.
2. Complete execution of all four deterministic engines (Nutrition, ICMR-HFSS, Claims, Ingredients).
3. High-resolution latency benchmarking and metric aggregation.
4. Structured ProductAnalysisResponse compatibility.
5. Graceful handling of missing products, missing nutrients, and uncharacterized ingredients.
"""

import uuid
from decimal import Decimal
import unittest
from unittest.mock import MagicMock

from app.models.product import Product
from app.models.product_nutrient import ProductNutrient
from app.models.product_ingredient import ProductIngredient
from app.models.ingredient import Ingredient
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.domain.engines.coordinator import EvaluationCoordinator, EvaluationRulesBundle
from app.domain.engines.contracts import (
    FoodForm,
    NutrientDataStatus,
    EvaluationStatus,
    IngredientProcessingClass,
    IngredientSugarClass,
    DeclaredClaimInput,
)
from app.schemas.product_analysis import ProductAnalysisResponse


class TestProductService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock(spec=ProductRepository)
        self.coordinator = EvaluationCoordinator.get_default()
        self.service = ProductService(
            product_repository=self.mock_repo,
            evaluation_coordinator=self.coordinator
        )

        # Build a realistic sample Product
        self.prod_id = uuid.uuid4()
        self.sample_product = Product(
            id=self.prod_id,
            barcode="8901030825279",
            product_name="Roasted Bengal Gram (Chana)",
            brand_name="YumSure Organics",
            food_form="solid",
            food_category="LEGUME_PULSE",
            package_size="200g",
            serving_size_value=Decimal("30.0"),
            serving_size_unit="g",
            is_verified=True,
            source_id="curated_verified_catalog",
            nutrients=[
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="energy",
                    per_100g_value=Decimal("387.0"),
                    per_serving_value=Decimal("116.1"),
                    unit="kcal",
                    data_status="PRESENT"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="protein",
                    per_100g_value=Decimal("22.5"),
                    per_serving_value=Decimal("6.75"),
                    unit="g",
                    data_status="PRESENT"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="total_fat",
                    per_100g_value=Decimal("5.2"),
                    per_serving_value=Decimal("1.56"),
                    unit="g",
                    data_status="PRESENT"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="saturated_fat",
                    per_100g_value=Decimal("0.8"),
                    per_serving_value=Decimal("0.24"),
                    unit="g",
                    data_status="PRESENT"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="trans_fat",
                    per_100g_value=Decimal("0.0"),
                    per_serving_value=Decimal("0.0"),
                    unit="g",
                    data_status="EXPLICITLY_ZERO"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="carbohydrates",
                    per_100g_value=Decimal("58.0"),
                    per_serving_value=Decimal("17.4"),
                    unit="g",
                    data_status="PRESENT"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="total_sugars",
                    per_100g_value=Decimal("2.0"),
                    per_serving_value=Decimal("0.6"),
                    unit="g",
                    data_status="PRESENT"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="added_sugars",
                    per_100g_value=Decimal("0.0"),
                    per_serving_value=Decimal("0.0"),
                    unit="g",
                    data_status="EXPLICITLY_ZERO"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="sodium",
                    per_100g_value=Decimal("15.0"),
                    per_serving_value=Decimal("4.5"),
                    unit="mg",
                    data_status="PRESENT"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="dietary_fibre",
                    per_100g_value=Decimal("12.0"),
                    per_serving_value=Decimal("3.6"),
                    unit="g",
                    data_status="PRESENT"
                ),
            ],
            ingredients=[
                ProductIngredient(
                    product_id=self.prod_id,
                    ingredient_code="roasted_chana",
                    sequence_order=1,
                    declared_percentage=Decimal("100.0"),
                    declared_label_text="Roasted Bengal Gram",
                    ingredient=Ingredient(
                        ingredient_code="roasted_chana",
                        canonical_name="Roasted Bengal Gram",
                        category="OTHER",
                        processing_classification="WHOLE_FOOD",
                        sugar_classification="NOT_SUGAR",
                        is_fssai_major_allergen=False,
                    )
                )
            ]
        )

    def test_01_get_product_by_barcode(self):
        """Verifies repository delegation with eager-loading flag enabled."""
        self.mock_repo.get_by_barcode.return_value = self.sample_product

        result = self.service.get_product_by_barcode("8901030825279")

        self.assertIsNotNone(result)
        self.assertEqual(result.product_name, "Roasted Bengal Gram (Chana)")
        self.mock_repo.get_by_barcode.assert_called_once_with(
            "8901030825279", load_relationships=True
        )

    def test_02_get_domain_product_by_barcode(self):
        """Verifies mapping to domain ProductEvaluationInput."""
        self.mock_repo.get_by_barcode.return_value = self.sample_product

        domain_dto = self.service.get_domain_product_by_barcode("8901030825279")

        self.assertIsNotNone(domain_dto)
        self.assertEqual(domain_dto.product_name, "Roasted Bengal Gram (Chana)")
        self.assertEqual(domain_dto.food_form, FoodForm.SOLID)
        self.assertEqual(len(domain_dto.nutrients), 10)
        self.assertEqual(len(domain_dto.ingredients), 1)
        self.assertEqual(domain_dto.ingredients[0].processing_classification, IngredientProcessingClass.WHOLE_FOOD)

    def test_03_get_domain_product_not_found(self):
        """Verifies lookup miss returns None cleanly without error."""
        self.mock_repo.get_by_barcode.return_value = None

        domain_dto = self.service.get_domain_product_by_barcode("9999999999999")
        self.assertIsNone(domain_dto)

    def test_04_analyze_product_by_barcode_full_pipeline(self):
        """
        Verifies end-to-end multi-engine evaluation via ProductService:
        1. Eagerly queries repository.
        2. Converts to domain DTO.
        3. Executes all four deterministic engines.
        4. Benchmarks latency.
        5. Returns complete ProductAnalysisResponse.
        """
        self.mock_repo.get_by_barcode.return_value = self.sample_product

        # Also declare a claim to test claims engine integration
        extra_claims = [
            DeclaredClaimInput(
                claim_code="TRANS_FAT_FREE",
                raw_label_statement="Zero Trans Fat"
            ),
            DeclaredClaimInput(
                claim_code="HIGH_PROTEIN",
                raw_label_statement="Rich in Protein"
            )
        ]

        response = self.service.analyze_product_by_barcode(
            barcode="8901030825279",
            extra_claims=extra_claims
        )

        self.assertIsInstance(response, ProductAnalysisResponse)
        
        # Product Summary
        self.assertEqual(response.product.barcode, "8901030825279")
        self.assertEqual(response.product.product_name, "Roasted Bengal Gram (Chana)")
        self.assertTrue(response.product.is_verified)
        self.assertEqual(response.product.nutrient_count, 10)
        self.assertEqual(response.product.ingredient_count, 1)

        # Engine Batch Results
        self.assertEqual(response.nutrition_evaluation.engine_name, "NUTRITION")
        self.assertGreater(len(response.nutrition_evaluation.results), 0)

        self.assertEqual(response.icmr_hfss_evaluation.engine_name, "ICMR_HFSS")
        self.assertGreater(len(response.icmr_hfss_evaluation.results), 0)

        self.assertEqual(response.claims_evaluation.engine_name, "CLAIMS")
        self.assertEqual(len(response.claims_evaluation.results), 14, "Must evaluate all 14 statutory Schedule I claims")
        # Trans fat free claim should pass
        tff_result = next(r for r in response.claims_evaluation.results if r.rule_code == "TRANS_FAT_FREE")
        self.assertEqual(tff_result.outcome, EvaluationStatus.PASS)

        self.assertEqual(response.ingredient_evaluation.engine_name, "INGREDIENT")
        self.assertIsInstance(response.ingredient_evaluation.results, list)
        self.assertEqual(len(response.ingredient_evaluation.results), 0, "Whole food chana contains no additives/allergens")

        # Performance Metrics
        metrics = response.metrics
        self.assertGreaterEqual(metrics.db_lookup_ms, 0.0)
        self.assertGreaterEqual(metrics.domain_mapping_ms, 0.0)
        self.assertGreater(metrics.nutrition_engine_ms, 0.0)
        self.assertGreater(metrics.icmr_hfss_engine_ms, 0.0)
        self.assertGreater(metrics.claims_engine_ms, 0.0)
        self.assertGreater(metrics.ingredient_engine_ms, 0.0)
        self.assertGreater(metrics.total_analysis_ms, 0.0)
        # Total latency should be <= 50ms for in-memory / local evaluation
        self.assertLess(metrics.total_analysis_ms, 100.0, "Multi-engine analysis must execute in < 100ms")

    def test_05_analyze_product_missing_nutrients_fails_safely(self):
        """
        A product missing mandatory nutrients must generate INSUFFICIENT_DATA notices
        without crashing or assuming zeroes.
        """
        # Product with only energy declared
        incomplete_product = Product(
            id=uuid.uuid4(),
            barcode="8900000000001",
            product_name="Incomplete Biscuit",
            food_form="solid",
            nutrients=[
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="energy",
                    per_100g_value=Decimal("400.0"),
                    unit="kcal",
                    data_status="PRESENT"
                )
            ],
            ingredients=[]
        )
        self.mock_repo.get_by_barcode.return_value = incomplete_product

        response = self.service.analyze_product_by_barcode("8900000000001")
        self.assertIsNotNone(response)
        
        # Nutrition engine should identify missing mandatory nutrients
        nut_eval = response.nutrition_evaluation
        insufficient_results = [r for r in nut_eval.results if r.outcome == EvaluationStatus.INSUFFICIENT_DATA]
        self.assertGreater(len(insufficient_results), 0)
        self.assertTrue(any("mandatory" in r.title.lower() for r in insufficient_results))

    def test_06_analyze_product_with_additive_triggers_ingredient_warning(self):
        """
        A product containing a regulated additive (e.g. Aspartame 951) must trigger
        statutory warning statements in the ingredient evaluation batch result.
        """
        aspartame_product = Product(
            id=uuid.uuid4(),
            barcode="8900000000002",
            product_name="Diet Cola Drink",
            food_form="liquid",
            food_category="BEVERAGE",
            is_verified=True,
            nutrients=[
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="energy",
                    per_100g_value=Decimal("1.0"),
                    unit="kcal",
                    data_status="PRESENT"
                )
            ],
            ingredients=[
                ProductIngredient(
                    product_id=self.prod_id,
                    ingredient_code="ins_951_aspartame",
                    sequence_order=1,
                    declared_label_text="Aspartame",
                    ingredient=Ingredient(
                        ingredient_code="ins_951_aspartame",
                        canonical_name="Aspartame",
                        ins_number="951",
                        category="SWEETENER",
                        processing_classification="FUNCTIONAL_ADDITIVE",
                        sugar_classification="NON_NUTRITIVE_SWEETENER",
                        is_fssai_major_allergen=False,
                    )
                )
            ]
        )
        self.mock_repo.get_by_barcode.return_value = aspartame_product

        response = self.service.analyze_product_by_barcode("8900000000002")
        self.assertIsNotNone(response)

        ing_eval = response.ingredient_evaluation
        self.assertGreater(len(ing_eval.results), 0)
        # Check that PKU / mandatory warning was emitted
        pku_result = next((r for r in ing_eval.results if "aspartame" in r.rule_id.lower()), None)
        self.assertIsNotNone(pku_result)
        self.assertEqual(pku_result.outcome, EvaluationStatus.PASS)
        self.assertIn("phenylketonurics", pku_result.human_readable_explanation.lower())


if __name__ == "__main__":
    unittest.main()
