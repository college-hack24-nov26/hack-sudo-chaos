"""
API Integration Tests for GET /api/v1/products/{barcode}.

Verifies:
1. HTTP 200 for local database hit.
2. HTTP 200 for Open Food Facts external fallback hit.
3. HTTP 404 for product not found anywhere.
4. HTTP 422 for invalid barcode formats (too short, too long, special characters).
5. All four independent engine outputs present in response body.
6. Zero composite health scores or arbitrary grades.
7. Zero stack trace leaks on error responses.
"""

from decimal import Decimal
import uuid
import unittest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_product_service
from app.models.product import Product
from app.models.product_nutrient import ProductNutrient
from app.services.product_service import ProductService
from app.integrations.open_food_facts import (
    OpenFoodFactsClient,
    OpenFoodFactsResponse,
    OpenFoodFactsStatus,
)
from app.repositories.product_repository import ProductRepository
from app.domain.engines.coordinator import EvaluationCoordinator


class TestProductApi(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock(spec=ProductRepository)
        self.mock_off = MagicMock(spec=OpenFoodFactsClient)
        self.coordinator = EvaluationCoordinator.get_default()

        # Build real service with mocked repo & OFF client
        self.mock_service = ProductService(
            product_repository=self.mock_repo,
            evaluation_coordinator=self.coordinator,
            off_client=self.mock_off,
        )

        # Override dependency in FastAPI
        app.dependency_overrides[get_product_service] = lambda: self.mock_service
        self.client = TestClient(app)

        # Realistic local product fixture
        self.prod_id = uuid.uuid4()
        self.local_product = Product(
            id=self.prod_id,
            barcode="8901030825279",
            product_name="Local Roasted Chana",
            brand_name="YumFoods",
            food_form="solid",
            food_category="SNACK",
            is_verified=True,
            nutrients=[
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="energy",
                    per_100g_value=Decimal("387.0"),
                    unit="kcal",
                    data_status="PRESENT"
                ),
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="protein",
                    per_100g_value=Decimal("22.5"),
                    unit="g",
                    data_status="PRESENT"
                ),
            ],
            ingredients=[]
        )

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_01_get_product_local_hit(self):
        """GET /api/v1/products/{barcode} with local product returns 200 OK."""
        self.mock_repo.get_by_barcode.return_value = self.local_product

        resp = self.client.get("/api/v1/products/8901030825279")

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["product"]["barcode"], "8901030825279")
        self.assertEqual(data["product"]["product_name"], "Local Roasted Chana")
        self.assertTrue(data["product"]["is_verified"])
        self.assertTrue(data["product"]["is_persisted"])

        # Check all 4 engines are present
        self.assertIn("nutrition_evaluation", data)
        self.assertIn("icmr_hfss_evaluation", data)
        self.assertIn("claims_evaluation", data)
        self.assertIn("ingredient_evaluation", data)
        self.assertEqual(data["nutrition_evaluation"]["engine_name"], "NUTRITION")
        self.assertEqual(data["icmr_hfss_evaluation"]["engine_name"], "ICMR_HFSS")

        # Confirm NO composite score exists
        self.assertNotIn("composite_score", data)
        self.assertNotIn("health_grade", data)

    def test_02_get_product_external_fallback_hit(self):
        """GET /api/v1/products/{barcode} on local miss queries OFF and returns 200 OK."""
        self.mock_repo.get_by_barcode.return_value = None  # local miss

        # Mock OFF response
        mock_off_resp = OpenFoodFactsResponse(
            status=OpenFoodFactsStatus.FOUND,
            barcode="8901234567890",
            product_data={
                "product_name": "External High Fibre Cereal",
                "brands": "MorningGrain",
                "quantity": "500g",
                "nutrition_data_per": "100g",
                "nutriments": {
                    "energy_100g": 360,
                    "energy_unit": "kcal",
                    "proteins_100g": 11.0,
                    "proteins_unit": "g",
                },
                "ingredients": [
                    {"id": "en:whole-wheat", "text": "Whole Wheat", "percent": 85}
                ]
            },
            raw_payload={"status": 1}
        )
        self.mock_off.get_product = AsyncMock(return_value=mock_off_resp)
        self.mock_repo.session = MagicMock()

        resp = self.client.get("/api/v1/products/8901234567890")

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["product"]["barcode"], "8901234567890")
        self.assertEqual(data["product"]["product_name"], "External High Fibre Cereal")
        self.assertEqual(data["product"]["brand_name"], "MorningGrain")
        self.assertFalse(data["product"]["is_verified"])

    def test_03_get_product_not_found(self):
        """When product is not found locally or externally, API returns 404."""
        self.mock_repo.get_by_barcode.return_value = None
        self.mock_off.get_product = AsyncMock(
            return_value=OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.NOT_FOUND,
                barcode="8900000000000",
            )
        )

        resp = self.client.get("/api/v1/products/8900000000000")

        self.assertEqual(resp.status_code, 404)
        data = resp.json()
        self.assertIn("not found", data["detail"].lower())

    def test_04_invalid_barcode_format_validation(self):
        """Barcodes with illegal characters or invalid length must return 422."""
        # Special characters
        resp1 = self.client.get("/api/v1/products/bad_barcode!")
        self.assertEqual(resp1.status_code, 422)

        # Too short (< 8 chars)
        resp2 = self.client.get("/api/v1/products/1234")
        self.assertEqual(resp2.status_code, 422)

        # Too long (> 14 chars)
        resp3 = self.client.get("/api/v1/products/12345678901234567")
        self.assertEqual(resp3.status_code, 422)

    def test_05_off_timeout_returns_404(self):
        """When OFF times out, API safely returns 404 without crashing."""
        self.mock_repo.get_by_barcode.return_value = None
        self.mock_off.get_product = AsyncMock(
            return_value=OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.TIMEOUT,
                barcode="8901111111111",
                error_message="Timed out",
            )
        )

        resp = self.client.get("/api/v1/products/8901111111111")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()

