"""
Frontend Endpoints & Response Compatibility Test Suite.

Verifies that FastAPI backend outputs match the exact JSON schema
required by the YumSure Flutter mobile client:
- /api/v1/products/{barcode} (ProductDetailsResponse with all 6 sections)
- /api/v1/search
- /api/v1/trending
- /api/v1/history
- /api/v1/history/insights
"""

import unittest
from decimal import Decimal
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_product_service, get_db
from app.services.product_service import ProductService
from app.domain.engines.contracts import (
    ProductEvaluationInput,
    NutrientObservationInput,
    IngredientObservationInput,
    DeclaredClaimInput,
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
)
from app.domain.engines.coordinator import EvaluationCoordinator


class TestFrontendApiCompatibility(unittest.TestCase):
    """Verifies backend API responses align with Flutter frontend model deserializers."""

    def setUp(self):
        self.client = TestClient(app)

    def test_01_search_endpoint_returns_items(self):
        """GET /api/v1/search?q=maggi must return items list matching SearchResultItem."""
        resp = self.client.get("/api/v1/search?q=maggi")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)
        self.assertIsInstance(data["items"], list)
        self.assertGreater(len(data["items"]), 0)
        item = data["items"][0]
        self.assertIn("barcode", item)
        self.assertIn("product_name", item)
        self.assertIn("category", item)
        self.assertIn("badges", item)

    def test_02_trending_endpoint_returns_items(self):
        """GET /api/v1/trending must return items list matching TrendingProductItem."""
        resp = self.client.get("/api/v1/trending")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)
        self.assertIsInstance(data["items"], list)
        self.assertGreater(len(data["items"]), 0)
        item = data["items"][0]
        self.assertIn("barcode", item)
        self.assertIn("product_name", item)
        self.assertIn("category", item)

    def test_03_history_endpoint_returns_items(self):
        """GET /api/v1/history must return items list matching ScanHistoryItem."""
        resp = self.client.get("/api/v1/history?limit=3")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)
        self.assertIsInstance(data["items"], list)
        self.assertLessEqual(len(data["items"]), 3)
        item = data["items"][0]
        self.assertIn("barcode", item)
        self.assertIn("product_name", item)
        self.assertIn("scanned_at", item)
        self.assertIn("key_finding", item)
        self.assertIn("key_finding_severity", item)

    def test_04_history_insights_returns_insight(self):
        """GET /api/v1/history/insights must return ScanInsight schema."""
        resp = self.client.get("/api/v1/history/insights?timeframe=7d")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("title", data)
        self.assertIn("description", data)
        self.assertIn("affected_count", data)
        self.assertIn("total_scanned_count", data)
        self.assertIn("finding_type", data)
        self.assertEqual(data["timeframe"], "7d")

    def test_05_product_details_contains_all_six_flutter_sections(self):
        """GET /api/v1/products/{barcode} must contain all sections expected by Flutter ProductDetailsResponse."""
        # Mock ProductService to return a rich analysis
        mock_service = MagicMock(spec=ProductService)

        # Create realistic biscuit input
        domain_product = ProductEvaluationInput(
            product_id="8901030383701",
            product_name="Nutri-Choice Digestive Biscuits",
            brand_name="Britannia",
            food_form=FoodForm.SOLID,
            food_category="Biscuits & Bakery",
            package_size="100g",
            serving_size_value=Decimal("25.0"),
            serving_size_unit="g",
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy", per_100g_value=Decimal("482.0"), unit="kcal",
                    data_status=NutrientDataStatus.PRESENT, measurement_basis=MeasurementBasis.PER_100G
                ),
                "protein": NutrientObservationInput(
                    nutrient_code="protein", per_100g_value=Decimal("8.0"), unit="g",
                    data_status=NutrientDataStatus.PRESENT, measurement_basis=MeasurementBasis.PER_100G
                ),
                "added_sugars": NutrientObservationInput(
                    nutrient_code="added_sugars", per_100g_value=Decimal("13.0"), unit="g",
                    data_status=NutrientDataStatus.PRESENT, measurement_basis=MeasurementBasis.PER_100G
                ),
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium", per_100g_value=Decimal("450.0"), unit="mg",
                    data_status=NutrientDataStatus.PRESENT, measurement_basis=MeasurementBasis.PER_100G
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat", per_100g_value=Decimal("0.0"), unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO, measurement_basis=MeasurementBasis.PER_100G
                ),
            },
            ingredients=[
                IngredientObservationInput(
                    ingredient_code="wheat_flour", declared_label_text="Refined Wheat Flour",
                    sequence_order=1, is_fssai_major_allergen=True
                ),
                IngredientObservationInput(
                    ingredient_code="sugar", declared_label_text="Sugar",
                    sequence_order=2
                ),
            ],
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat")
            ],
        )

        coordinator = EvaluationCoordinator.get_default()
        coord_result = coordinator.evaluate(domain_product)

        from app.schemas.product_analysis import ProductSummaryResponse, EnginePerformanceMetrics, ProductAnalysisResponse
        from app.schemas.frontend_adapter import build_frontend_sections

        summary = ProductSummaryResponse(
            product_id="8901030383701",
            barcode="8901030383701",
            product_name="Nutri-Choice Digestive Biscuits",
            brand_name="Britannia",
            food_form="solid",
            food_category="Biscuits & Bakery",
            package_size="100g",
            serving_size_value=Decimal("25.0"),
            serving_size_unit="g",
            is_verified=True,
            is_veg=True,
            image_url="https://images.openfoodfacts.org/front.jpg",
            nutrient_count=5,
            ingredient_count=2,
            is_persisted=True,
        )

        metrics = EnginePerformanceMetrics(
            db_lookup_ms=1.2,
            external_lookup_ms=None,
            domain_mapping_ms=0.5,
            nutrition_engine_ms=0.8,
            icmr_hfss_engine_ms=0.9,
            claims_engine_ms=1.1,
            ingredient_engine_ms=0.6,
            total_analysis_ms=5.1,
        )

        fe_sections = build_frontend_sections(
            domain_product=domain_product,
            nutrition_eval=coord_result.nutrition_evaluation,
            icmr_eval=coord_result.icmr_hfss_evaluation,
            claims_eval=coord_result.claims_evaluation,
            ingredient_eval=coord_result.ingredient_evaluation,
            include_ai_explanation=True,
        )

        analysis_response = ProductAnalysisResponse(
            product=summary,
            nutrition_evaluation=coord_result.nutrition_evaluation,
            icmr_hfss_evaluation=coord_result.icmr_hfss_evaluation,
            claims_evaluation=coord_result.claims_evaluation,
            ingredient_evaluation=coord_result.ingredient_evaluation,
            metrics=metrics,
            nutritional_interpretation=fe_sections["nutritional_interpretation"],
            regulatory_claims_validation=fe_sections["regulatory_claims_validation"],
            ingredient_analysis=fe_sections["ingredient_analysis"],
            key_findings=fe_sections["key_findings"],
            ai_explanation=fe_sections["ai_explanation"],
        )

        mock_service.analyze_product_by_barcode_async.return_value = analysis_response
        app.dependency_overrides[get_product_service] = lambda: mock_service

        try:
            resp = self.client.get("/api/v1/products/8901030383701")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()

            # 1. Product identity
            self.assertIn("product", data)
            self.assertEqual(data["product"]["barcode"], "8901030383701")
            self.assertEqual(data["product"]["product_name"], "Nutri-Choice Digestive Biscuits")

            # 2. Nutritional Interpretation
            self.assertIn("nutritional_interpretation", data)
            self.assertIsNotNone(data["nutritional_interpretation"])
            nutrients = data["nutritional_interpretation"]["nutrients"]
            self.assertGreater(len(nutrients), 0)
            sugar_item = next((n for n in nutrients if n["nutrient_code"] == "added_sugars"), None)
            self.assertIsNotNone(sugar_item)
            self.assertEqual(sugar_item["value_per_100g"], 13.0)
            self.assertEqual(sugar_item["classification"], "High")

            # 3. Regulatory Claims Validation
            self.assertIn("regulatory_claims_validation", data)
            self.assertIsNotNone(data["regulatory_claims_validation"])
            self.assertIn("claims", data["regulatory_claims_validation"])

            # 4. Ingredient Analysis
            self.assertIn("ingredient_analysis", data)
            self.assertIsNotNone(data["ingredient_analysis"])
            self.assertIn("declared_allergens", data["ingredient_analysis"])
            self.assertIn("categories", data["ingredient_analysis"])

            # 5. Key Findings
            self.assertIn("key_findings", data)
            self.assertIsInstance(data["key_findings"], list)
            self.assertGreater(len(data["key_findings"]), 0)

            # 6. AI Explanation
            self.assertIn("ai_explanation", data)
            self.assertIsNotNone(data["ai_explanation"])
            self.assertIn("text", data["ai_explanation"])
            self.assertTrue(len(data["ai_explanation"]["text"]) > 10)

        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()

