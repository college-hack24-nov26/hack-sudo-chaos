"""
Unit and Integration Tests for ProductRepository.

Validates product retrieval, 3NF eager-loading of nutrients and ingredients,
unknown barcode handling, and non-invasive rollback isolation.
Zero records persist in the development database after test completion.
"""

import uuid
import unittest
import sys
from decimal import Decimal
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.orm import Session

from app.db.session import engine
from app.models import (
    Product, Nutrient, ProductNutrient,
    Ingredient, ProductIngredient, DataSource
)
from app.repositories.product_repository import ProductRepository


class TestProductRepository(unittest.TestCase):
    """
    Tests ProductRepository using transactional test isolation.
    All inserted test fixtures are rolled back in tearDown().
    """

    @classmethod
    def setUpClass(cls):
        # Open a dedicated connection for testing
        cls.connection = engine.connect()

    @classmethod
    def tearDownClass(cls):
        # Close connection
        cls.connection.close()

    def setUp(self):
        # Begin an atomic transaction for each test
        self.transaction = self.connection.begin()
        # Bind session to connection
        self.session = Session(bind=self.connection)
        self.repo = ProductRepository(self.session)

        # Prepare unique fixture IDs to prevent any collisions
        self.source_id = f"SRC_{uuid.uuid4().hex[:8]}"
        self.nutr_code_1 = f"nutr_prot_{uuid.uuid4().hex[:6]}"
        self.nutr_code_2 = f"nutr_sug_{uuid.uuid4().hex[:6]}"
        self.ing_code_1 = f"ing_flour_{uuid.uuid4().hex[:6]}"
        self.ing_code_2 = f"ing_sugar_{uuid.uuid4().hex[:6]}"
        self.barcode = "8901030000001"

        # 1. Insert Data Source fixture
        self.data_source = DataSource(
            source_id=self.source_id,
            name="Open Food Facts Test",
            license_type="ODbL",
            license_url="https://opendatacommons.org/licenses/odbl/",
            attribution_text="Open Food Facts Contributors",
            permits_redistribution=True
        )
        self.session.add(self.data_source)

        # 2. Insert Nutrient catalog fixtures
        self.nutr_1 = Nutrient(
            nutrient_code=self.nutr_code_1,
            display_name="Protein",
            standard_unit="g",
            is_fssai_mandatory=True,
            icmr_nin_rda_adult=Decimal("54.00")
        )
        self.nutr_2 = Nutrient(
            nutrient_code=self.nutr_code_2,
            display_name="Added Sugars",
            standard_unit="g",
            is_fssai_mandatory=True,
            icmr_nin_rda_adult=Decimal("50.00")
        )
        self.session.add_all([self.nutr_1, self.nutr_2])

        # 3. Insert Ingredient catalog fixtures
        self.ing_1 = Ingredient(
            ingredient_code=self.ing_code_1,
            canonical_name="Whole Wheat Flour",
            category="REFINED_CARB",
            processing_classification="CULINARY_PROCESSED",
            sugar_classification="NOT_SUGAR",
            is_fssai_major_allergen=True
        )
        self.ing_2 = Ingredient(
            ingredient_code=self.ing_code_2,
            canonical_name="Cane Sugar",
            category="SWEETENER",
            processing_classification="CULINARY_PROCESSED",
            sugar_classification="ADDED_FREE_SUGAR",
            is_fssai_major_allergen=False
        )
        self.session.add_all([self.ing_1, self.ing_2])

        # 4. Insert Product fixture
        self.product = Product(
            id=uuid.uuid4(),
            barcode=self.barcode,
            product_name="Digestive Biscuits",
            brand_name="Test Brand",
            package_size="100 g",
            serving_size_value=Decimal("25.00"),
            serving_size_unit="g",
            food_form="solid",
            food_category="Biscuits",
            is_verified=True,
            source_id=self.source_id,
            raw_source_payload={"product_name": "Digestive Biscuits", "image_front_url": "https://img.test/front.jpg"}
        )
        self.session.add(self.product)
        self.session.flush()

        # 5. Insert ProductNutrients bridge fixtures
        self.pn_1 = ProductNutrient(
            product_id=self.product.id,
            nutrient_code=self.nutr_code_1,
            per_100g_value=Decimal("8.500"),
            per_serving_value=Decimal("2.125"),
            unit="g",
            data_status="PRESENT"
        )
        self.pn_2 = ProductNutrient(
            product_id=self.product.id,
            nutrient_code=self.nutr_code_2,
            per_100g_value=Decimal("12.000"),
            per_serving_value=Decimal("3.000"),
            unit="g",
            data_status="PRESENT"
        )
        self.session.add_all([self.pn_1, self.pn_2])

        # 6. Insert ProductIngredients bridge fixtures (order_by sequence_order)
        self.pi_1 = ProductIngredient(
            product_id=self.product.id,
            ingredient_code=self.ing_code_1,
            sequence_order=1,
            declared_percentage=Decimal("65.00"),
            is_allergen_declared=True,
            declared_label_text="Whole Wheat Flour (65%)"
        )
        self.pi_2 = ProductIngredient(
            product_id=self.product.id,
            ingredient_code=self.ing_code_2,
            sequence_order=2,
            declared_percentage=Decimal("15.00"),
            is_allergen_declared=False,
            declared_label_text="Cane Sugar (15%)"
        )
        self.session.add_all([self.pi_1, self.pi_2])
        self.session.flush()

    def tearDown(self):
        # Close session and rollback transaction to leave DB 100% untouched
        self.session.close()
        self.transaction.rollback()

    def test_01_get_by_barcode_success(self):
        """Verify an existing barcode returns the product with scalar fields intact."""
        prod = self.repo.get_by_barcode(self.barcode)
        self.assertIsNotNone(prod)
        self.assertEqual(prod.barcode, self.barcode)
        self.assertEqual(prod.product_name, "Digestive Biscuits")
        self.assertEqual(prod.food_form, "solid")
        self.assertTrue(prod.is_verified)

    def test_02_get_by_barcode_unknown_returns_none(self):
        """Verify unknown or empty barcodes return None gracefully."""
        self.assertIsNone(self.repo.get_by_barcode("9999999999999"))
        self.assertIsNone(self.repo.get_by_barcode(""))
        self.assertIsNone(self.repo.get_by_barcode("   "))

    def test_03_eager_loaded_nutrients_retrieval(self):
        """Verify product nutrients and their master nutrient definitions are eager-loaded."""
        prod = self.repo.get_by_barcode(self.barcode)
        self.assertIsNotNone(prod)
        self.assertEqual(len(prod.nutrients), 2)

        # Map by nutrient code
        nutrient_map = {pn.nutrient_code: pn for pn in prod.nutrients}
        self.assertIn(self.nutr_code_1, nutrient_map)
        self.assertIn(self.nutr_code_2, nutrient_map)

        # Verify values and four-state status
        pn_prot = nutrient_map[self.nutr_code_1]
        self.assertEqual(pn_prot.per_100g_value, Decimal("8.500"))
        self.assertEqual(pn_prot.data_status, "PRESENT")
        # Verify joined master Nutrient entity is populated
        self.assertEqual(pn_prot.nutrient.display_name, "Protein")
        self.assertEqual(pn_prot.nutrient.standard_unit, "g")

    def test_04_eager_loaded_ingredients_sequence_order(self):
        """Verify ingredients are retrieved in 1-indexed descending weight sequence."""
        prod = self.repo.get_by_barcode(self.barcode)
        self.assertIsNotNone(prod)
        self.assertEqual(len(prod.ingredients), 2)

        # Must be ordered by sequence_order ascending (1, then 2)
        first_ing = prod.ingredients[0]
        second_ing = prod.ingredients[1]

        self.assertEqual(first_ing.sequence_order, 1)
        self.assertEqual(first_ing.ingredient_code, self.ing_code_1)
        self.assertEqual(first_ing.ingredient.canonical_name, "Whole Wheat Flour")
        self.assertTrue(first_ing.is_allergen_declared)

        self.assertEqual(second_ing.sequence_order, 2)
        self.assertEqual(second_ing.ingredient_code, self.ing_code_2)
        self.assertEqual(second_ing.ingredient.canonical_name, "Cane Sugar")

    def test_05_data_source_relationship(self):
        """Verify data source relationship is eager-loaded."""
        prod = self.repo.get_by_barcode(self.barcode)
        self.assertIsNotNone(prod)
        self.assertIsNotNone(prod.data_source)
        self.assertEqual(prod.data_source.source_id, self.source_id)
        self.assertEqual(prod.data_source.name, "Open Food Facts Test")
        self.assertEqual(prod.data_source.license_type, "ODbL")

    def test_06_exists_by_barcode(self):
        """Verify high-performance count existence check."""
        self.assertTrue(self.repo.exists_by_barcode(self.barcode))
        self.assertFalse(self.repo.exists_by_barcode("9999999999999"))
        self.assertFalse(self.repo.exists_by_barcode(""))

    def test_07_get_verified_by_barcode(self):
        """Verify retrieval filtered by is_verified = True."""
        prod = self.repo.get_verified_by_barcode(self.barcode)
        self.assertIsNotNone(prod)
        self.assertTrue(prod.is_verified)

    def test_08_get_by_id_uuid(self):
        """Verify retrieval by primary key UUID."""
        prod = self.repo.get_by_id(self.product.id)
        self.assertIsNotNone(prod)
        self.assertEqual(prod.id, self.product.id)
        self.assertEqual(prod.barcode, self.barcode)
        self.assertEqual(prod.product_name, "Digestive Biscuits")

    def test_09_get_by_id_string(self):
        """Verify retrieval by valid string-formatted UUID."""
        prod = self.repo.get_by_id(str(self.product.id))
        self.assertIsNotNone(prod)
        self.assertEqual(prod.id, self.product.id)
        self.assertEqual(prod.barcode, self.barcode)

    def test_10_get_by_id_invalid_string(self):
        """Verify malformed UUID string returns None gracefully."""
        self.assertIsNone(self.repo.get_by_id("invalid-uuid-format"))
        self.assertIsNone(self.repo.get_by_id(""))

    def test_11_get_by_barcode_without_relationships(self):
        """Verify retrieval with load_relationships=False executes without eager joins."""
        prod = self.repo.get_by_barcode(self.barcode, load_relationships=False)
        self.assertIsNotNone(prod)
        self.assertEqual(prod.barcode, self.barcode)
        self.assertEqual(prod.product_name, "Digestive Biscuits")


if __name__ == "__main__":
    unittest.main()
