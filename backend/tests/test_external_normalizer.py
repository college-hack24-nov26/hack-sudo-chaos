"""
Unit Tests for ExternalProductNormalizer.

Verifies:
1. Missing nutrient values remain None (never converted to 0).
2. Explicit zero declarations remain Decimal(0) with EXPLICITLY_ZERO status.
3. Missing nutrient units are not replaced with grams ('g'); mapped to 'UNKNOWN'.
4. Measurement basis is NOT guessed; resolved strictly from explicit metadata or None.
5. Missing claims do not produce fabricated claims (declared_claims is empty).
6. OFF tags/categories are never treated as voluntary front-of-pack claims.
7. Ingredient sequence order is preserved.
8. Transient ORM entity generation for safe persistence.
"""

from decimal import Decimal
import unittest

from app.domain.mappers.external_normalizer import ExternalProductNormalizer
from app.domain.engines.contracts import (
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
)


class TestExternalProductNormalizer(unittest.TestCase):
    def test_01_missing_nutrient_values_remain_none(self):
        """Missing nutrient values in OFF response must remain None with NOT_DECLARED status."""
        raw_product = {
            "product_name": "Test Oats",
            "nutrition_data_per": "100g",
            "nutriments": {
                "energy_100g": 380,
                "energy_unit": "kcal",
                # protein, fat, sugars, trans_fat are completely missing
            },
        }

        dto = ExternalProductNormalizer.to_domain_dto("8901234567890", raw_product)

        # Protein missing
        self.assertIn("protein", dto.nutrients)
        self.assertIsNone(dto.nutrients["protein"].per_100g_value, "Missing nutrient value must be None")
        self.assertEqual(dto.nutrients["protein"].data_status, NutrientDataStatus.NOT_DECLARED)

        # Trans fat missing
        self.assertIn("trans_fat", dto.nutrients)
        self.assertIsNone(dto.nutrients["trans_fat"].per_100g_value, "Missing trans_fat must be None")
        self.assertEqual(dto.nutrients["trans_fat"].data_status, NutrientDataStatus.NOT_DECLARED)

    def test_02_explicit_zero_preserved(self):
        """Explicit 0 or 0.0 in OFF response must be preserved as Decimal(0) with EXPLICITLY_ZERO."""
        raw_product = {
            "product_name": "Sugar Free Beverage",
            "nutrition_data_per": "100ml",
            "nutriments": {
                "energy_100g": 0,
                "energy_unit": "kcal",
                "trans-fat_100g": 0.0,
                "trans-fat_unit": "g",
                "added-sugars_100g": 0,
                "added-sugars_unit": "g",
            },
        }

        dto = ExternalProductNormalizer.to_domain_dto("8901234567891", raw_product)

        self.assertEqual(dto.nutrients["trans_fat"].per_100g_value, Decimal("0"))
        self.assertEqual(dto.nutrients["trans_fat"].data_status, NutrientDataStatus.EXPLICITLY_ZERO)
        self.assertEqual(dto.nutrients["added_sugars"].per_100g_value, Decimal("0"))
        self.assertEqual(dto.nutrients["added_sugars"].data_status, NutrientDataStatus.EXPLICITLY_ZERO)

    def test_03_missing_nutrient_units_not_replaced_with_grams(self):
        """Nutrient value present but unit missing must NOT default to grams; must be UNKNOWN."""
        raw_product = {
            "product_name": "Unspecified Chemical Food",
            "nutrition_data_per": "100g",
            "nutriments": {
                "sodium_100g": 120,
                # sodium_unit is missing!
            },
        }

        dto = ExternalProductNormalizer.to_domain_dto("8901234567892", raw_product)

        obs = dto.nutrients["sodium"]
        self.assertEqual(obs.unit, "UNKNOWN", "Missing unit must not default to 'g'")
        self.assertEqual(obs.data_status, NutrientDataStatus.UNKNOWN, "Missing unit must force UNKNOWN status")

    def test_04_measurement_basis_not_guessed(self):
        """
        Measurement basis must be resolved strictly from explicit metadata or key suffixes.
        If cannot be resolved reliably, it must be None (unresolved), NEVER guessed from food_form.
        """
        # Case A: Explicit nutrition_data_per = '100g' -> PER_100G
        raw_a = {
            "nutrition_data_per": "100g",
            "nutriments": {"energy_100g": 200, "energy_unit": "kcal"},
        }
        self.assertEqual(
            ExternalProductNormalizer.determine_measurement_basis(raw_a, raw_a["nutriments"]),
            MeasurementBasis.PER_100G,
        )

        # Case B: Explicit nutrition_data_per = '100ml' -> PER_100ML
        raw_b = {
            "nutrition_data_per": "100ml",
            "nutriments": {"energy_100ml": 50, "energy_unit": "kcal"},
        }
        self.assertEqual(
            ExternalProductNormalizer.determine_measurement_basis(raw_b, raw_b["nutriments"]),
            MeasurementBasis.PER_100ML,
        )

        # Case C: Explicit nutrition_data_per = 'serving' -> PER_SERVING
        raw_c = {
            "nutrition_data_per": "serving",
            "nutriments": {"energy_serving": 150, "energy_unit": "kcal"},
        }
        self.assertEqual(
            ExternalProductNormalizer.determine_measurement_basis(raw_c, raw_c["nutriments"]),
            MeasurementBasis.PER_SERVING,
        )

        # Case D: Ambiguous / unresolvable metadata -> returns None without guessing
        raw_ambiguous = {
            "product_name": "Ambiguous Basis Product",
            "nutrition_data_per": "unspecified_package",
            "nutriments": {"energy_value": 300, "energy_unit": "kcal", "protein_value": 10, "protein_unit": "g"},
        }
        self.assertIsNone(
            ExternalProductNormalizer.determine_measurement_basis(raw_ambiguous, raw_ambiguous["nutriments"]),
            "Ambiguous basis must be None, never guessed silently",
        )

        # Verify that DTO normalization with unresolved basis flags declared observations as UNKNOWN
        # and leaves per_100g_value as None to prevent silent injection into 100g/ml rules
        dto_ambiguous = ExternalProductNormalizer.to_domain_dto("8901234567899", raw_ambiguous)
        # Declared nutrient with ambiguous basis -> UNKNOWN status, null per_100g_value
        obs_protein = dto_ambiguous.nutrients["protein"]
        self.assertIsNone(obs_protein.measurement_basis, "Protein measurement_basis must be None")
        self.assertIsNone(obs_protein.per_100g_value, "Protein per_100g_value must be None when basis is unresolved")
        self.assertEqual(
            obs_protein.data_status,
            NutrientDataStatus.UNKNOWN,
            "Protein data_status must be UNKNOWN when basis cannot be verified"
        )
        # Undeclared nutrient -> NOT_DECLARED
        obs_sodium = dto_ambiguous.nutrients["sodium"]
        self.assertEqual(obs_sodium.data_status, NutrientDataStatus.NOT_DECLARED)
        self.assertIsNone(obs_sodium.per_100g_value)

        # Verify serving-only basis maps to per_serving_value and leaves per_100g_value as None
        dto_serving = ExternalProductNormalizer.to_domain_dto("8901234567898", {
            "product_name": "Serving Only Product",
            "nutrition_data_per": "serving",
            "nutriments": {"energy_value": 150, "energy_unit": "kcal", "protein_value": 5, "protein_unit": "g"},
        })
        self.assertEqual(dto_serving.nutrients["energy"].measurement_basis, MeasurementBasis.PER_SERVING)
        self.assertIsNone(dto_serving.nutrients["energy"].per_100g_value, "Serving-only product must have null per_100g_value")
        self.assertEqual(dto_serving.nutrients["energy"].per_serving_value, Decimal("150"))
        self.assertEqual(dto_serving.nutrients["energy"].data_status, NutrientDataStatus.PRESENT)

    def test_05_no_fabricated_claims(self):
        """OFF categories and tags must NEVER be treated as verified front-of-pack claims."""
        raw_product = {
            "product_name": "Healthy Snack",
            "categories_tags": ["en:organic", "en:gluten-free", "en:low-fat"],
            "labels_tags": ["en:no-preservatives", "en:vegan"],
            "nutriments": {},
        }

        dto = ExternalProductNormalizer.to_domain_dto("8901234567894", raw_product)

        self.assertEqual(
            dto.declared_claims,
            [],
            "Declared claims must be empty; OFF tags are not verified packaging claims",
        )

    def test_06_ingredient_sequence_order_preserved(self):
        """Ingredient list sequence order (1, 2, 3...) must be strictly preserved."""
        raw_product = {
            "product_name": "Peanut Butter Biscuit",
            "ingredients": [
                {"id": "en:wheat-flour", "text": "Wheat Flour", "percent": 50.0},
                {"id": "en:peanuts", "text": "Roasted Peanuts", "percent": 25.0},
                {"id": "en:sugar", "text": "Cane Sugar", "percent": 15.0},
                {"id": "en:salt", "text": "Iodized Salt", "percent": 1.0},
            ],
            "nutriments": {},
        }

        dto = ExternalProductNormalizer.to_domain_dto("8901234567895", raw_product)

        self.assertEqual(len(dto.ingredients), 4)
        self.assertEqual(dto.ingredients[0].sequence_order, 1)
        self.assertEqual(dto.ingredients[0].declared_label_text, "Wheat Flour")
        self.assertEqual(dto.ingredients[1].sequence_order, 2)
        self.assertEqual(dto.ingredients[1].declared_label_text, "Roasted Peanuts")
        self.assertEqual(dto.ingredients[2].sequence_order, 3)
        self.assertEqual(dto.ingredients[2].declared_label_text, "Cane Sugar")
        self.assertEqual(dto.ingredients[3].sequence_order, 4)
        self.assertEqual(dto.ingredients[3].declared_label_text, "Iodized Salt")

    def test_07_transient_orm_entity_generation(self):
        """Constructs uncommitted Product ORM entity with source attribution and children."""
        raw_product = {
            "product_name": "Tomato Ketchup",
            "brands": "KetchupCo",
            "quantity": "500g",
            "nutrition_data_per": "100g",
            "nutriments": {
                "energy_100g": 110,
                "energy_unit": "kcal",
                "proteins_100g": 1.5,
                "proteins_unit": "g",
            },
            "ingredients": [
                {"id": "en:tomato-paste", "text": "Tomato Paste", "percent": 60}
            ],
        }

        raw_payload = {"status": 1, "product": raw_product}
        orm_entity = ExternalProductNormalizer.to_orm_entity("8901234567896", raw_product, raw_payload)

        self.assertEqual(orm_entity.barcode, "8901234567896")
        self.assertEqual(orm_entity.product_name, "Tomato Ketchup")
        self.assertEqual(orm_entity.brand_name, "KetchupCo")
        self.assertFalse(orm_entity.is_verified, "External products must default to is_verified = False")
        self.assertEqual(orm_entity.source_id, "open_food_facts")
        self.assertEqual(orm_entity.raw_source_payload, raw_payload)
        self.assertGreater(len(orm_entity.nutrients), 0)
        self.assertEqual(len(orm_entity.ingredients), 1)


if __name__ == "__main__":
    unittest.main()

