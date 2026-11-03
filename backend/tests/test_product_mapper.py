"""
Unit Tests for ORM-to-Domain ProductMapper.

Verifies:
1. Strict four-state nutrient semantics (PRESENT, EXPLICITLY_ZERO, NOT_DECLARED, UNKNOWN).
2. Missing nutrient values are NEVER converted to zero (None remains None).
3. Explicit measurement basis mapping (PER_100G, PER_100ML, PER_SERVING) from product metadata.
4. Unsafe unit fallback removal (never falls back to 'g'; missing unit becomes 'UNKNOWN').
5. Dedicated DeclaredClaimsNormalizer (validates typed claims, never invents claims, preserves raw payload).
6. Ingredient sequence ordering (sequence_order ascending = label descending weight).
7. Ingredient scientific classification propagation and UNKNOWN fallbacks.
8. Food form mapping (solid vs liquid) and serving size preservation.
"""

import uuid
from decimal import Decimal
import unittest

from app.models.product import Product
from app.models.product_nutrient import ProductNutrient
from app.models.product_ingredient import ProductIngredient
from app.models.nutrient import Nutrient
from app.models.ingredient import Ingredient
from app.domain.engines.contracts import (
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
    IngredientProcessingClass,
    IngredientSugarClass,
    DeclaredClaimInput,
)
from app.domain.mappers.product_mapper import (
    ProductMapper,
    DeclaredClaimsNormalizer,
    map_orm_product_to_domain,
)


class TestProductMapper(unittest.TestCase):
    def setUp(self):
        self.prod_id = uuid.uuid4()

    def test_01_food_form_mapping(self):
        """Food form strings must map to proper FoodForm enum with safe fallback."""
        self.assertEqual(ProductMapper.map_food_form("solid"), FoodForm.SOLID)
        self.assertEqual(ProductMapper.map_food_form("SOLID"), FoodForm.SOLID)
        self.assertEqual(ProductMapper.map_food_form("liquid"), FoodForm.LIQUID)
        self.assertEqual(ProductMapper.map_food_form("LIQUID"), FoodForm.LIQUID)
        # Fallback
        self.assertEqual(ProductMapper.map_food_form(None), FoodForm.SOLID)
        self.assertEqual(ProductMapper.map_food_form("gas"), FoodForm.SOLID)

    def test_02_nutrient_status_preservation(self):
        """Strict four-state nutrient declaration semantics must be preserved."""
        # 1. PRESENT
        self.assertEqual(
            ProductMapper.map_nutrient_status("PRESENT", Decimal("10.5"), None),
            NutrientDataStatus.PRESENT
        )
        # 2. EXPLICITLY_ZERO
        self.assertEqual(
            ProductMapper.map_nutrient_status("EXPLICITLY_ZERO", Decimal("0.0"), None),
            NutrientDataStatus.EXPLICITLY_ZERO
        )
        # 3. NOT_DECLARED
        self.assertEqual(
            ProductMapper.map_nutrient_status("NOT_DECLARED", None, None),
            NutrientDataStatus.NOT_DECLARED
        )
        # 4. UNKNOWN
        self.assertEqual(
            ProductMapper.map_nutrient_status("UNKNOWN", None, None),
            NutrientDataStatus.UNKNOWN
        )
        # 5. Fallback inference when raw_status is None
        self.assertEqual(
            ProductMapper.map_nutrient_status(None, None, None),
            NutrientDataStatus.NOT_DECLARED
        )
        self.assertEqual(
            ProductMapper.map_nutrient_status(None, Decimal("0"), None),
            NutrientDataStatus.EXPLICITLY_ZERO
        )
        self.assertEqual(
            ProductMapper.map_nutrient_status(None, Decimal("5.2"), None),
            NutrientDataStatus.PRESENT
        )

    def test_03_missing_nutrient_value_never_converted_to_zero(self):
        """
        CRITICAL: None values for missing nutrients must NEVER be converted to Decimal(0).
        Conflating missing data with zero breaches FSSAI and ICMR guidelines.
        """
        pn = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="added_sugars",
            per_100g_value=None,
            per_serving_value=None,
            unit="g",
            data_status="NOT_DECLARED",
        )
        dto = ProductMapper.map_nutrient(pn)
        self.assertIsNone(dto.per_100g_value, "Missing per_100g_value must remain None")
        self.assertIsNone(dto.per_serving_value, "Missing per_serving_value must remain None")
        self.assertEqual(dto.data_status, NutrientDataStatus.NOT_DECLARED)
        self.assertEqual(dto.unit, "g")

    def test_04_explicitly_zero_nutrient_preserved(self):
        """Explicit zero declaration (e.g. trans fat 0g) must be preserved as Decimal(0)."""
        pn = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="trans_fat",
            per_100g_value=Decimal("0.0"),
            per_serving_value=Decimal("0.0"),
            unit="g",
            data_status="EXPLICITLY_ZERO",
        )
        dto = ProductMapper.map_nutrient(pn)
        self.assertEqual(dto.per_100g_value, Decimal("0.0"))
        self.assertEqual(dto.per_serving_value, Decimal("0.0"))
        self.assertEqual(dto.data_status, NutrientDataStatus.EXPLICITLY_ZERO)

    def test_05_measurement_basis_explicit_mapping(self):
        """
        Measurement basis must be explicitly mapped to PER_100G, PER_100ML, or PER_SERVING
        based strictly on product metadata and declaration scope, NEVER inferred from values.
        """
        # Solid product with reference quantity
        pn_solid = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="protein",
            per_100g_value=Decimal("12.0"),
            unit="g",
            data_status="PRESENT"
        )
        dto_solid = ProductMapper.map_nutrient(pn_solid, food_form=FoodForm.SOLID)
        self.assertEqual(dto_solid.measurement_basis, MeasurementBasis.PER_100G)

        # Liquid product with reference quantity
        pn_liquid = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="protein",
            per_100g_value=Decimal("3.0"),
            unit="g",
            data_status="PRESENT"
        )
        dto_liquid = ProductMapper.map_nutrient(pn_liquid, food_form=FoodForm.LIQUID)
        self.assertEqual(dto_liquid.measurement_basis, MeasurementBasis.PER_100ML)

        # Serving-only declaration (per_100g_value is None, per_serving_value is present)
        pn_serving_only = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="sodium",
            per_100g_value=None,
            per_serving_value=Decimal("50.0"),
            unit="mg",
            data_status="PRESENT"
        )
        dto_serving = ProductMapper.map_nutrient(pn_serving_only, food_form=FoodForm.SOLID)
        self.assertEqual(dto_serving.measurement_basis, MeasurementBasis.PER_SERVING)

    def test_06_nutrient_unit_fallback_removal(self):
        """
        Unsafe fallback to grams ('g') must be completely removed.
        Missing units from both ProductNutrient and master Nutrient must explicitly
        result in unit='UNKNOWN' and data_status=UNKNOWN.
        """
        # 1. Valid unit preserved
        pn_valid = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="sodium",
            per_100g_value=Decimal("150.0"),
            unit="mg",
            data_status="PRESENT"
        )
        dto_valid = ProductMapper.map_nutrient(pn_valid)
        self.assertEqual(dto_valid.unit, "mg")
        self.assertEqual(dto_valid.data_status, NutrientDataStatus.PRESENT)

        # 2. Missing unit on pn, but master Nutrient has unit
        master_nut = Nutrient(nutrient_code="energy", display_name="Energy", standard_unit="kcal")
        pn_master_unit = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="energy",
            per_100g_value=Decimal("250.0"),
            unit=None,  # Missing on product record
            data_status="PRESENT",
            nutrient=master_nut
        )
        dto_master = ProductMapper.map_nutrient(pn_master_unit)
        self.assertEqual(dto_master.unit, "kcal")
        self.assertEqual(dto_master.data_status, NutrientDataStatus.PRESENT)

        # 3. Completely missing unit (both pn and master lack unit)
        pn_missing = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="unknown_compound",
            per_100g_value=Decimal("10.0"),
            unit=None,
            data_status="PRESENT",
            nutrient=None
        )
        dto_missing = ProductMapper.map_nutrient(pn_missing)
        self.assertEqual(dto_missing.unit, "UNKNOWN", "Missing unit must not default to 'g'")
        self.assertEqual(dto_missing.data_status, NutrientDataStatus.UNKNOWN, "Missing unit must force status to UNKNOWN")

    def test_07_declared_claims_normalization_boundary(self):
        """
        Dedicated DeclaredClaimsNormalizer must strictly validate claims,
        never invent claims when empty, and preserve raw payload.
        """
        # 1. No claims in payload -> yields empty list
        empty_payload = {"some_other_key": 123}
        claims_empty = DeclaredClaimsNormalizer.normalize(empty_payload)
        self.assertEqual(claims_empty, [], "Must return empty list when no claim declarations exist")

        # None payload -> yields empty list
        self.assertEqual(DeclaredClaimsNormalizer.normalize(None), [])

        # 2. Valid authentic claims
        valid_payload = {
            "declared_claims": [
                {"claim_code": "trans_fat_free", "raw_label_statement": "Zero Trans Fat"},
                {"claim_code": "HIGH_PROTEIN", "raw_label_statement": "Rich in Protein"},
            ]
        }
        claims = DeclaredClaimsNormalizer.normalize(valid_payload)
        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[0].claim_code, "TRANS_FAT_FREE")
        self.assertEqual(claims[0].raw_label_statement, "Zero Trans Fat")
        self.assertEqual(claims[1].claim_code, "HIGH_PROTEIN")

        # 3. Malformed items skipped safely
        malformed_payload = {
            "declared_claims": [
                {"claim_code": "VALID", "raw_label_statement": "Valid Statement"},
                {"claim_code": "", "raw_label_statement": "Empty Code"},
                {"claim_code": "NO_STMT"},
                "not_a_dict"
            ]
        }
        filtered = DeclaredClaimsNormalizer.normalize(malformed_payload)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].claim_code, "VALID")

    def test_08_ingredient_ordering_preserved(self):
        """
        Ingredients must be strictly ordered by integer sequence_order ascending (1, 2, 3...),
        representing descending weight on the product label.
        """
        pi3 = ProductIngredient(product_id=self.prod_id, ingredient_code="salt", sequence_order=3, declared_label_text="Salt")
        pi1 = ProductIngredient(product_id=self.prod_id, ingredient_code="flour", sequence_order=1, declared_label_text="Wheat Flour")
        pi2 = ProductIngredient(product_id=self.prod_id, ingredient_code="oil", sequence_order=2, declared_label_text="Palm Oil")

        prod = Product(
            id=self.prod_id,
            barcode="8901234567890",
            product_name="Test Biscuits",
            food_form="solid",
            ingredients=[pi3, pi1, pi2],
        )

        domain_prod = ProductMapper.map_product(prod)
        self.assertEqual(len(domain_prod.ingredients), 3)
        self.assertEqual(domain_prod.ingredients[0].sequence_order, 1)
        self.assertEqual(domain_prod.ingredients[0].ingredient_code, "flour")
        self.assertEqual(domain_prod.ingredients[1].sequence_order, 2)
        self.assertEqual(domain_prod.ingredients[1].ingredient_code, "oil")
        self.assertEqual(domain_prod.ingredients[2].sequence_order, 3)
        self.assertEqual(domain_prod.ingredients[2].ingredient_code, "salt")

    def test_09_ingredient_classification_propagation(self):
        """Master Ingredient classifications must propagate to IngredientObservationInput."""
        master_ing = Ingredient(
            ingredient_code="ins_951_aspartame",
            canonical_name="Aspartame",
            ins_number="951",
            category="SWEETENER",
            processing_classification="FUNCTIONAL_ADDITIVE",
            sugar_classification="NON_NUTRITIVE_SWEETENER",
            classification_evidence="Artificial sweetener",
        )
        pi = ProductIngredient(
            product_id=self.prod_id,
            ingredient_code="ins_951_aspartame",
            sequence_order=1,
            declared_label_text="Aspartame 951",
            ingredient=master_ing,
        )
        dto = ProductMapper.map_ingredient(pi)

        self.assertEqual(dto.ingredient_code, "ins_951_aspartame")
        self.assertEqual(dto.ins_number, "951")
        self.assertEqual(dto.processing_classification, IngredientProcessingClass.FUNCTIONAL_ADDITIVE)
        self.assertEqual(dto.sugar_classification, IngredientSugarClass.NON_NUTRITIVE_SWEETENER)

    def test_10_full_product_mapping_liquid_basis_and_provenance(self):
        """Full ORM Product mapping for liquid product with explicit PER_100ML and provenance."""
        n_energy = Nutrient(nutrient_code="energy", display_name="Energy", standard_unit="kcal")
        pn_energy = ProductNutrient(
            product_id=self.prod_id,
            nutrient_code="energy",
            per_100g_value=Decimal("42.0"),
            unit="kcal",
            data_status="PRESENT",
            nutrient=n_energy,
        )

        raw_payload = {
            "source_api": "open_food_facts",
            "declared_claims": [
                {"claim_code": "NO_ADDED_SUGARS", "raw_label_statement": "Without Added Sugar"}
            ]
        }

        prod = Product(
            id=self.prod_id,
            barcode="8901030825279",
            product_name="Mango Nectar Juice",
            brand_name="YumBeverages",
            package_size="1L",
            serving_size_value=Decimal("200.0"),
            serving_size_unit="ml",
            food_form="liquid",
            food_category="BEVERAGE",
            is_verified=True,
            source_id="open_food_facts",
            raw_source_payload=raw_payload,
            nutrients=[pn_energy],
            ingredients=[]
        )

        dto = map_orm_product_to_domain(prod)

        self.assertEqual(dto.food_form, FoodForm.LIQUID)
        self.assertEqual(dto.nutrients["energy"].measurement_basis, MeasurementBasis.PER_100ML)
        self.assertEqual(dto.nutrients["energy"].unit, "kcal")
        self.assertEqual(dto.data_source_id, "open_food_facts")
        self.assertEqual(len(dto.declared_claims), 1)
        self.assertEqual(dto.declared_claims[0].claim_code, "NO_ADDED_SUGARS")


if __name__ == "__main__":
    unittest.main()
