"""
Unit Tests for ProductService Fallback and Safe Ingestion.

Verifies:
1. Local product found -> external API is not called.
2. Local product not found -> OFF fallback is called.
3. OFF product found -> normalized and evaluated via EvaluationCoordinator.
4. OFF product not found / timeout / network failure -> returns None.
5. Verified local product is NEVER overwritten.
6. Safe persistence failure (e.g. unmigrated DB) -> in-memory evaluation succeeds with is_persisted = False.
7. Multi-engine evaluation returns 4 distinct batches without composite health scores.
"""

from decimal import Decimal
import uuid
import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.exc import OperationalError
from app.models.product import Product
from app.models.product_nutrient import ProductNutrient
from app.repositories.product_repository import ProductRepository
from app.integrations.open_food_facts import (
    OpenFoodFactsClient,
    OpenFoodFactsResponse,
    OpenFoodFactsStatus,
)
from app.services.product_service import ProductService
from app.domain.engines.coordinator import EvaluationCoordinator
from app.schemas.product_analysis import ProductAnalysisResponse


class TestProductServiceFallback(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_repo = MagicMock(spec=ProductRepository)
        self.mock_repo.session = MagicMock()
        self.mock_off = MagicMock(spec=OpenFoodFactsClient)
        self.coordinator = EvaluationCoordinator.get_default()

        self.service = ProductService(
            product_repository=self.mock_repo,
            evaluation_coordinator=self.coordinator,
            off_client=self.mock_off,
        )

        # Sample local product
        self.prod_id = uuid.uuid4()
        self.local_product = Product(
            id=self.prod_id,
            barcode="8901030825279",
            product_name="Local Curated Chana",
            food_form="solid",
            is_verified=True,
            nutrients=[
                ProductNutrient(
                    product_id=self.prod_id,
                    nutrient_code="energy",
                    per_100g_value=Decimal("387.0"),
                    unit="kcal",
                    data_status="PRESENT"
                )
            ],
            ingredients=[]
        )

    async def test_01_local_product_found_skips_external_api(self):
        """When local database contains product, external OFF API must NOT be called."""
        self.mock_repo.get_by_barcode.return_value = self.local_product

        response = await self.service.analyze_product_by_barcode_async("8901030825279")

        self.assertIsNotNone(response)
        self.assertEqual(response.product.product_name, "Local Curated Chana")
        self.assertTrue(response.product.is_persisted)
        self.assertTrue(response.product.is_verified)
        self.mock_repo.get_by_barcode.assert_called_once_with("8901030825279", load_relationships=True)
        # Ensure OFF client was NEVER called
        self.mock_off.get_product.assert_not_called()
        self.mock_off.get_product_sync.assert_not_called()

    async def test_02_local_miss_triggers_open_food_facts_fallback(self):
        """When local database misses, Open Food Facts fallback must be queried."""
        self.mock_repo.get_by_barcode.return_value = None  # Local miss

        # Mock OFF response
        mock_off_resp = OpenFoodFactsResponse(
            status=OpenFoodFactsStatus.FOUND,
            barcode="8909999999999",
            product_data={
                "product_name": "External Whole Grain Bread",
                "brands": "GlobalBakery",
                "nutrition_data_per": "100g",
                "image_front_url": "https://images.off.org/bread.jpg",
                "nutriments": {
                    "energy_100g": 250,
                    "energy_unit": "kcal",
                    "proteins_100g": 9.0,
                    "proteins_unit": "g",
                },
                "ingredients": [
                    {"id": "en:wheat-flour", "text": "Whole Wheat Flour", "percent": 70}
                ]
            },
            raw_payload={"status": 1}
        )
        self.mock_off.get_product = AsyncMock(return_value=mock_off_resp)

        # Mock successful persistence
        self.mock_repo.session = MagicMock()

        response = await self.service.analyze_product_by_barcode_async("8909999999999")

        self.assertIsNotNone(response)
        self.assertEqual(response.product.product_name, "External Whole Grain Bread")
        self.assertEqual(response.product.brand_name, "GlobalBakery")
        self.assertEqual(response.product.image_url, "https://images.off.org/bread.jpg")
        self.assertFalse(response.product.is_verified, "External product must not be marked verified")
        self.mock_off.get_product.assert_called_once_with("8909999999999")

    async def test_03_off_not_found_returns_none(self):
        """When local DB misses and OFF returns NOT_FOUND, service returns None."""
        self.mock_repo.get_by_barcode.return_value = None
        self.mock_off.get_product = AsyncMock(
            return_value=OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.NOT_FOUND,
                barcode="0000000000000",
            )
        )

        response = await self.service.analyze_product_by_barcode_async("0000000000000")

        self.assertIsNone(response)

    async def test_04_off_timeout_returns_none(self):
        """When OFF times out, service gracefully returns None without crashing."""
        self.mock_repo.get_by_barcode.return_value = None
        self.mock_off.get_product = AsyncMock(
            return_value=OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.TIMEOUT,
                barcode="8901234567890",
                error_message="Timeout after 3s",
            )
        )

        response = await self.service.analyze_product_by_barcode_async("8901234567890")

        self.assertIsNone(response)

    async def test_05_verified_product_never_overwritten(self):
        """A verified product in local DB must never be overwritten by external data."""
        # Setup verified existing product
        verified_existing = Product(
            id=uuid.uuid4(),
            barcode="8901030825279",
            product_name="Curated Verified Chana",
            is_verified=True,
        )
        self.mock_repo.get_by_barcode.return_value = verified_existing

        persisted = self.service._safe_persist_external_product(
            barcode="8901030825279",
            raw_product={"product_name": "Overwriting External Chana"},
        )

        self.assertFalse(persisted, "Must reject persistence over verified product")
        self.mock_repo.session.add.assert_not_called()

    async def test_06_persistence_unavailable_in_memory_evaluation_succeeds(self):
        """
        When database persistence fails (e.g. unmigrated Supabase / tables missing),
        in-memory evaluation must succeed and return is_persisted = False.
        """
        self.mock_repo.get_by_barcode.return_value = None  # Local miss
        self.mock_off.get_product = AsyncMock(
            return_value=OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.FOUND,
                barcode="8901234567899",
                product_data={
                    "product_name": "Unpersisted Ephemeral Snack",
                    "nutrition_data_per": "100g",
                    "nutriments": {"energy_100g": 350, "energy_unit": "kcal"},
                },
                raw_payload={"status": 1}
            )
        )

        # Mock DB session throwing OperationalError (tables not created)
        mock_session = MagicMock()
        mock_session.commit.side_effect = OperationalError("relation 'products' does not exist", None, None)
        self.mock_repo.session = mock_session

        response = await self.service.analyze_product_by_barcode_async("8901234567899")

        self.assertIsNotNone(response, "Analysis must succeed even if database persistence fails")
        self.assertEqual(response.product.product_name, "Unpersisted Ephemeral Snack")
        self.assertFalse(response.product.is_persisted, "is_persisted must truthfully report False")
        self.assertEqual(response.product.source_id, "open_food_facts")

    async def test_07_all_four_engine_batches_returned_without_composite_score(self):
        """Service response must include all 4 engine results and zero composite scores."""
        self.mock_repo.get_by_barcode.return_value = self.local_product

        response = await self.service.analyze_product_by_barcode_async("8901030825279")

        self.assertIsNotNone(response)
        self.assertEqual(response.nutrition_evaluation.engine_name, "NUTRITION")
        self.assertEqual(response.icmr_hfss_evaluation.engine_name, "ICMR_HFSS")
        self.assertEqual(response.claims_evaluation.engine_name, "CLAIMS")
        self.assertEqual(response.ingredient_evaluation.engine_name, "INGREDIENT")

        # Zero composite health score
        resp_dict = response.model_dump()
        self.assertNotIn("composite_score", resp_dict)
        self.assertNotIn("health_grade", resp_dict)
        self.assertNotIn("traffic_light_score", resp_dict)


if __name__ == "__main__":
    unittest.main()
