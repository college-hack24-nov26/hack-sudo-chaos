"""
Nutrition Data Integrity & Serving Basis Conversion Regression Test Suite.

Verifies end-to-end data pipeline integrity across:
1. Canonical nutrient mapping & packaging order
2. Preserved measurement basis semantics (PER_100G, PER_100ML, PER_SERVING)
3. Bidirectional serving <-> 100g conversions with exact mathematical verification
4. Explicit zero vs missing/unobserved nutrient distinction
5. Prevention of silent conversion when measurement basis or serving weight is unresolved
6. Comprehensive nutrient inconsistency detection (negative values, sugar/fat hierarchies, Atwater energy)
7. Frontend adapter serialization and data quality grading
"""

import os
import sys
import unittest
from decimal import Decimal

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Dict, Any, List

from app.domain.engines.contracts import (
    ProductEvaluationInput,
    NutrientObservationInput,
    NutrientDataStatus,
    MeasurementBasis,
    FoodForm,
)
from app.domain.curated_catalog import (
    get_curated_product,
    CURATED_DEMO_PRODUCTS,
)
from app.domain.mappers.external_normalizer import ExternalProductNormalizer
from app.schemas.frontend_adapter import (
    build_frontend_sections,
    validate_nutrient_consistency,
    CANONICAL_NUTRIENT_ORDER,
    NUTRIENT_DISPLAY_NAMES,
)


class TestNutritionDataIntegrity(unittest.TestCase):
    """Exhaustive test suite verifying nutrition data integrity and serving calculations."""

    def test_01_all_ten_canonical_nutrients_present_with_correct_units(self):
        """Scenario 1: Nutri-Choice Digestive has all 10 canonical nutrients declared with correct units."""
        product = get_curated_product("8901030383701")
        self.assertIsNotNone(product, "Curated product 8901030383701 must exist")

        nutrients = product.nutrients
        self.assertEqual(len(nutrients), 10, "Must contain all 10 canonical nutrients")

        expected_units = {
            "energy": "kcal",
            "protein": "g",
            "carbohydrates": "g",
            "total_sugars": "g",
            "added_sugars": "g",
            "total_fat": "g",
            "saturated_fat": "g",
            "trans_fat": "g",
            "sodium": "mg",
            "dietary_fibre": "g",
        }

        for code, expected_unit in expected_units.items():
            self.assertIn(code, nutrients, f"Nutrient {code} must be present in Nutri-Choice Digestive")
            self.assertEqual(
                nutrients[code].unit,
                expected_unit,
                f"Nutrient {code} unit must be {expected_unit}, got {nutrients[code].unit}",
            )
            self.assertIsNotNone(nutrients[code].per_100g_value, f"{code} per_100g_value must be non-null")
            self.assertIsNotNone(nutrients[code].per_serving_value, f"{code} per_serving_value must be non-null")

    def test_02_measurement_basis_preserved_explicitly(self):
        """Scenario 2: Observations retain explicit MeasurementBasis without silent inference."""
        product = get_curated_product("8901030383701")
        for obs in product.nutrients.values():
            self.assertEqual(
                obs.measurement_basis,
                MeasurementBasis.PER_100G,
                f"Nutrient {obs.nutrient_code} must have explicit PER_100G basis",
            )
            self.assertNotEqual(obs.measurement_basis, MeasurementBasis.PER_100ML)
            self.assertNotEqual(obs.measurement_basis, MeasurementBasis.PER_SERVING)

    def test_03_accurate_100g_to_serving_conversion_nutri_choice(self):
        """Scenario 3: 25g serving calculations match declared packaging values exactly."""
        product = get_curated_product("8901030383701")
        nutrients = product.nutrients

        # Pack declaration: 25g serving size (1/4 of 100g)
        self.assertEqual(product.serving_size_value, Decimal("25.0"))
        self.assertEqual(product.serving_size_unit, "g")

        expected_conversions = {
            "energy": (Decimal("482.0"), Decimal("120.5")),
            "protein": (Decimal("8.0"), Decimal("2.0")),
            "carbohydrates": (Decimal("68.0"), Decimal("17.0")),
            "total_sugars": (Decimal("14.5"), Decimal("3.63")),
            "added_sugars": (Decimal("13.0"), Decimal("3.25")),
            "total_fat": (Decimal("21.0"), Decimal("5.25")),
            "saturated_fat": (Decimal("10.0"), Decimal("2.5")),
            "trans_fat": (Decimal("0.0"), Decimal("0.0")),
            "sodium": (Decimal("450.0"), Decimal("112.5")),
            "dietary_fibre": (Decimal("6.2"), Decimal("1.55")),
        }

        for code, (exp_100g, exp_serving) in expected_conversions.items():
            obs = nutrients[code]
            self.assertEqual(obs.per_100g_value, exp_100g, f"{code} 100g mismatch")
            self.assertEqual(obs.per_serving_value, exp_serving, f"{code} serving mismatch")

    def test_04_bidirectional_serving_to_100g_conversion_in_mapper(self):
        """Scenario 4: When external product has PER_SERVING basis, mapper computes per_100g_value."""
        raw_product = {
            "product_name": "Single Serving Granola Bar",
            "nutrition_data_per": "serving",
            "serving_quantity": 40.0,
            "nutriments": {
                "energy-kcal_serving": 160.0,
                "energy-kcal_unit": "kcal",
                "proteins_serving": 4.0,
                "proteins_unit": "g",
                "carbohydrates_serving": 24.0,
                "carbohydrates_unit": "g",
                "sugars_serving": 8.0,
                "sugars_unit": "g",
                "fat_serving": 6.0,
                "fat_unit": "g",
                "sodium_serving": 100.0,
                "sodium_unit": "mg",
            },
        }

        normalized = ExternalProductNormalizer.to_domain_dto("1234567890123", raw_product)
        obs_map = normalized.nutrients

        # Energy: 160 kcal / 40g * 100g = 400.0 kcal
        self.assertIn("energy", obs_map)
        energy_obs = obs_map["energy"]
        self.assertEqual(energy_obs.per_serving_value, Decimal("160.0"))
        self.assertEqual(energy_obs.per_100g_value, Decimal("400.0"))

        # Protein: 4g / 40g * 100g = 10.0g
        self.assertEqual(obs_map["protein"].per_100g_value, Decimal("10.0"))

    def test_05_missing_nutrient_distinct_from_explicit_zero(self):
        """Scenario 5: Trans fat explicit zero vs missing nutrient preserves distinct status."""
        product = get_curated_product("8901030383701")
        nutrients = product.nutrients

        trans_fat = nutrients["trans_fat"]
        self.assertEqual(trans_fat.data_status, NutrientDataStatus.EXPLICITLY_ZERO)
        self.assertEqual(trans_fat.per_100g_value, Decimal("0.0"))
        self.assertEqual(trans_fat.per_serving_value, Decimal("0.0"))

        # Create synthetic observation for undeclared nutrient
        undeclared_obs = NutrientObservationInput(
            nutrient_code="vitamin_c",
            per_100g_value=None,
            per_serving_value=None,
            unit="mg",
            measurement_basis=MeasurementBasis.PER_100G,
            data_status=NutrientDataStatus.NOT_DECLARED,
        )
        self.assertEqual(undeclared_obs.data_status, NutrientDataStatus.NOT_DECLARED)
        self.assertIsNone(undeclared_obs.per_100g_value)
        self.assertNotEqual(undeclared_obs.per_100g_value, Decimal("0"))

    def test_06_unknown_measurement_basis_prevents_silent_conversion(self):
        """Scenario 6: When measurement basis is None or serving size missing, do not convert."""
        # Case A: serving size is None
        obs = NutrientObservationInput(
            nutrient_code="sodium",
            per_100g_value=Decimal("450.0"),
            per_serving_value=None,
            unit="mg",
            measurement_basis=MeasurementBasis.PER_100G,
            data_status=NutrientDataStatus.PRESENT,
        )
        dummy_product = ProductEvaluationInput(
            product_id="test_product",
            product_name="Test Product",
            food_form=FoodForm.SOLID,
            serving_size_value=None,
            nutrients={"sodium": obs},
        )

        sections = build_frontend_sections(
            domain_product=dummy_product,
            nutrition_eval=None,
            icmr_eval=None,
            claims_eval=None,
            ingredient_eval=None,
        )
        sodium_item = sections["nutritional_interpretation"].nutrients[0]
        self.assertEqual(sodium_item.value_per_100g, 450.0)
        self.assertIsNone(sodium_item.value_per_serving, "Must remain None when serving size is missing")

        # Case B: measurement_basis is None
        obs_no_basis = NutrientObservationInput(
            nutrient_code="sodium",
            per_100g_value=Decimal("450.0"),
            per_serving_value=None,
            unit="mg",
            measurement_basis=None,
            data_status=NutrientDataStatus.PRESENT,
        )
        dummy_product_no_basis = ProductEvaluationInput(
            product_id="test_product_2",
            product_name="Test Product 2",
            food_form=FoodForm.SOLID,
            serving_size_value=Decimal("25.0"),
            serving_size_unit="g",
            nutrients={"sodium": obs_no_basis},
        )
        sections_no_basis = build_frontend_sections(
            domain_product=dummy_product_no_basis,
            nutrition_eval=None,
            icmr_eval=None,
            claims_eval=None,
            ingredient_eval=None,
        )
        sodium_no_basis = sections_no_basis["nutritional_interpretation"].nutrients[0]
        self.assertIsNone(
            sodium_no_basis.value_per_serving,
            "Must NOT convert when measurement_basis is unresolved (None)",
        )

    def test_07_inconsistency_added_sugars_exceeding_total_sugars(self):
        """Scenario 7: Added sugars > total sugars detected as impossible data error."""
        inconsistent_nutrients = {
            "total_sugars": NutrientObservationInput(
                nutrient_code="total_sugars",
                per_100g_value=Decimal("5.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
            "added_sugars": NutrientObservationInput(
                nutrient_code="added_sugars",
                per_100g_value=Decimal("10.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
        }

        issues = validate_nutrient_consistency(inconsistent_nutrients)
        self.assertTrue(
            any("Added sugars (10.0g) exceeds total sugars (5.0g)" in issue for issue in issues),
            f"Expected sugar hierarchy violation in issues: {issues}",
        )

    def test_08_inconsistency_saturated_fat_exceeding_total_fat(self):
        """Scenario 8: Saturated fat > total fat detected as impossible data error."""
        inconsistent_nutrients = {
            "total_fat": NutrientObservationInput(
                nutrient_code="total_fat",
                per_100g_value=Decimal("10.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
            "saturated_fat": NutrientObservationInput(
                nutrient_code="saturated_fat",
                per_100g_value=Decimal("15.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
        }

        issues = validate_nutrient_consistency(inconsistent_nutrients)
        self.assertTrue(
            any("Saturated fat (15.0g) exceeds total fat (10.0g)" in issue for issue in issues),
            f"Expected fat hierarchy violation in issues: {issues}",
        )

    def test_09_inconsistency_trans_fat_exceeding_total_fat(self):
        """Scenario 9: Trans fat > total fat detected as impossible data error."""
        inconsistent_nutrients = {
            "total_fat": NutrientObservationInput(
                nutrient_code="total_fat",
                per_100g_value=Decimal("5.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
            "trans_fat": NutrientObservationInput(
                nutrient_code="trans_fat",
                per_100g_value=Decimal("6.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
        }

        issues = validate_nutrient_consistency(inconsistent_nutrients)
        self.assertTrue(
            any("Trans fat (6.0g) exceeds total fat (5.0g)" in issue for issue in issues),
            f"Expected trans fat hierarchy violation in issues: {issues}",
        )

    def test_10_inconsistency_atwater_energy_plausibility(self):
        """Scenario 10: Energy deviating significantly from Atwater macronutrient sum is flagged."""
        # Declared energy 800 kcal with only 10g protein (40 kcal), 10g fat (90 kcal), 20g carb (80 kcal) = 210 kcal
        macro_nutrients = {
            "energy": NutrientObservationInput(
                nutrient_code="energy",
                per_100g_value=Decimal("800.0"),
                unit="kcal",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
            "protein": NutrientObservationInput(
                nutrient_code="protein",
                per_100g_value=Decimal("10.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
            "carbohydrates": NutrientObservationInput(
                nutrient_code="carbohydrates",
                per_100g_value=Decimal("20.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
            "total_fat": NutrientObservationInput(
                nutrient_code="total_fat",
                per_100g_value=Decimal("10.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
        }

        issues = validate_nutrient_consistency(macro_nutrients)
        self.assertTrue(
            any("deviates significantly from estimated macronutrient sum" in issue for issue in issues),
            f"Expected energy plausibility failure in issues: {issues}",
        )

    def test_11_nutri_choice_energy_plausibility_verified(self):
        """Scenario 11: Nutri-Choice Digestive declared energy (482 kcal) matches Atwater sum."""
        product = get_curated_product("8901030383701")
        issues = validate_nutrient_consistency(product.nutrients)
        # Should have zero inconsistency issues
        self.assertEqual(issues, [], f"Nutri-Choice should have 0 consistency issues, got {issues}")

    def test_12_frontend_payload_adapter_serialization_and_quality(self):
        """Scenario 12: Adapter builds payload with demo data quality for demo fixture 8901030383701."""
        product = get_curated_product("8901030383701")
        sections = build_frontend_sections(
            domain_product=product,
            nutrition_eval=None,
            icmr_eval=None,
            claims_eval=None,
            ingredient_eval=None,
        )

        interp = sections["nutritional_interpretation"]
        self.assertEqual(interp.serving_size_value, 25.0)
        self.assertEqual(interp.serving_size_unit, "g")
        self.assertEqual(interp.data_quality, "DEMO_DATA")
        self.assertEqual(interp.data_inconsistencies, [])

        # Confirm all 10 nutrients present in canonical order
        rendered_codes = [n.nutrient_code for n in interp.nutrients]
        self.assertEqual(rendered_codes, CANONICAL_NUTRIENT_ORDER)

        # Confirm carbohydrate item details
        carbs_item = next(n for n in interp.nutrients if n.nutrient_code == "carbohydrates")
        self.assertEqual(carbs_item.value_per_100g, 68.0)
        self.assertEqual(carbs_item.value_per_serving, 17.0)
        self.assertEqual(carbs_item.unit, "g")
        self.assertEqual(carbs_item.status, "PRESENT")

    def test_13_verified_commercial_barcode_classified_as_verified(self):
        """Scenario 13: Authentic commercial barcode 8901063142015 is classified as VERIFIED."""
        product = get_curated_product("8901063142015")
        self.assertIsNotNone(product, "Commercial pack 8901063142015 must exist in catalog")
        self.assertEqual(product.data_source_id, "verified_packaging")

        sections = build_frontend_sections(
            domain_product=product,
            nutrition_eval=None,
            icmr_eval=None,
            claims_eval=None,
            ingredient_eval=None,
        )
        interp = sections["nutritional_interpretation"]
        self.assertEqual(interp.data_quality, "VERIFIED")
        self.assertEqual(interp.data_inconsistencies, [])

    def test_14_per_100ml_with_valid_volume_serving_conversion(self):
        """Scenario 14: Liquid product (PER_100ML) with 200 ml serving computes serving values."""
        obs = NutrientObservationInput(
            nutrient_code="total_sugars",
            per_100g_value=Decimal("13.0"),
            per_serving_value=None,
            unit="g",
            measurement_basis=MeasurementBasis.PER_100ML,
            data_status=NutrientDataStatus.PRESENT,
        )
        liquid_product = ProductEvaluationInput(
            product_id="test_juice",
            product_name="Fruit Juice",
            food_form=FoodForm.LIQUID,
            serving_size_value=Decimal("200.0"),
            serving_size_unit="ml",
            data_source_id="verified_packaging",
            nutrients={
                "energy": NutrientObservationInput(nutrient_code="energy", per_100g_value=Decimal("56.0"), unit="kcal", measurement_basis=MeasurementBasis.PER_100ML, data_status=NutrientDataStatus.PRESENT),
                "protein": NutrientObservationInput(nutrient_code="protein", per_100g_value=Decimal("0.4"), unit="g", measurement_basis=MeasurementBasis.PER_100ML, data_status=NutrientDataStatus.PRESENT),
                "carbohydrates": NutrientObservationInput(nutrient_code="carbohydrates", per_100g_value=Decimal("13.5"), unit="g", measurement_basis=MeasurementBasis.PER_100ML, data_status=NutrientDataStatus.PRESENT),
                "total_sugars": obs,
                "total_fat": NutrientObservationInput(nutrient_code="total_fat", per_100g_value=Decimal("0.0"), unit="g", measurement_basis=MeasurementBasis.PER_100ML, data_status=NutrientDataStatus.EXPLICITLY_ZERO),
                "sodium": NutrientObservationInput(nutrient_code="sodium", per_100g_value=Decimal("10.0"), unit="mg", measurement_basis=MeasurementBasis.PER_100ML, data_status=NutrientDataStatus.PRESENT),
            },
        )
        sections = build_frontend_sections(domain_product=liquid_product, nutrition_eval=None, icmr_eval=None, claims_eval=None, ingredient_eval=None)
        sugars_item = next(n for n in sections["nutritional_interpretation"].nutrients if n.nutrient_code == "total_sugars")
        # 13.0g / 100ml * 200ml = 26.0g
        self.assertEqual(sugars_item.value_per_serving, 26.0)

    def test_15_per_100ml_with_incompatible_mass_serving_rejected(self):
        """Scenario 15: PER_100ML basis with incompatible mass serving (e.g. 25 g) rejects conversion."""
        obs = NutrientObservationInput(
            nutrient_code="total_sugars",
            per_100g_value=Decimal("13.0"),
            per_serving_value=None,
            unit="g",
            measurement_basis=MeasurementBasis.PER_100ML,
            data_status=NutrientDataStatus.PRESENT,
        )
        mismatched_product = ProductEvaluationInput(
            product_id="test_mismatch_liquid",
            product_name="Liquid with Gram Serving",
            food_form=FoodForm.LIQUID,
            serving_size_value=Decimal("25.0"),
            serving_size_unit="g",  # Mismatch: liquid reference basis requires ml serving
            data_source_id="verified_packaging",
            nutrients={"total_sugars": obs},
        )
        sections = build_frontend_sections(domain_product=mismatched_product, nutrition_eval=None, icmr_eval=None, claims_eval=None, ingredient_eval=None)
        sugars_item = sections["nutritional_interpretation"].nutrients[0]
        self.assertIsNone(sugars_item.value_per_serving, "Must reject conversion when volume basis has mass serving")

    def test_16_per_100g_with_valid_mass_serving_conversion(self):
        """Scenario 16: Solid product (PER_100G) with 25 g serving computes serving values."""
        obs = NutrientObservationInput(
            nutrient_code="protein",
            per_100g_value=Decimal("8.0"),
            per_serving_value=None,
            unit="g",
            measurement_basis=MeasurementBasis.PER_100G,
            data_status=NutrientDataStatus.PRESENT,
        )
        solid_product = ProductEvaluationInput(
            product_id="test_solid",
            product_name="Solid Biscuit",
            food_form=FoodForm.SOLID,
            serving_size_value=Decimal("25.0"),
            serving_size_unit="g",
            data_source_id="verified_packaging",
            nutrients={"protein": obs},
        )
        sections = build_frontend_sections(domain_product=solid_product, nutrition_eval=None, icmr_eval=None, claims_eval=None, ingredient_eval=None)
        prot_item = sections["nutritional_interpretation"].nutrients[0]
        # 8.0g / 100g * 25g = 2.0g
        self.assertEqual(prot_item.value_per_serving, 2.0)

    def test_17_per_100g_with_incompatible_volume_serving_rejected(self):
        """Scenario 17: PER_100G basis with incompatible volume serving (e.g. 25 ml) rejects conversion."""
        obs = NutrientObservationInput(
            nutrient_code="protein",
            per_100g_value=Decimal("8.0"),
            per_serving_value=None,
            unit="g",
            measurement_basis=MeasurementBasis.PER_100G,
            data_status=NutrientDataStatus.PRESENT,
        )
        mismatched_product = ProductEvaluationInput(
            product_id="test_mismatch_solid",
            product_name="Solid with ML Serving",
            food_form=FoodForm.SOLID,
            serving_size_value=Decimal("25.0"),
            serving_size_unit="ml",  # Mismatch: solid reference basis requires g serving
            data_source_id="verified_packaging",
            nutrients={"protein": obs},
        )
        sections = build_frontend_sections(domain_product=mismatched_product, nutrition_eval=None, icmr_eval=None, claims_eval=None, ingredient_eval=None)
        prot_item = sections["nutritional_interpretation"].nutrients[0]
        self.assertIsNone(prot_item.value_per_serving, "Must reject conversion when mass basis has volume serving")

    def test_18_unknown_serving_unit_rejected(self):
        """Scenario 18: Serving size declared in count units (e.g. 'pieces') rejects conversion."""
        obs = NutrientObservationInput(
            nutrient_code="protein",
            per_100g_value=Decimal("8.0"),
            per_serving_value=None,
            unit="g",
            measurement_basis=MeasurementBasis.PER_100G,
            data_status=NutrientDataStatus.PRESENT,
        )
        unitless_product = ProductEvaluationInput(
            product_id="test_pieces",
            product_name="Cookies by Piece",
            food_form=FoodForm.SOLID,
            serving_size_value=Decimal("2.0"),
            serving_size_unit="pieces",  # Non-metric piece count cannot be converted without weight
            data_source_id="verified_packaging",
            nutrients={"protein": obs},
        )
        sections = build_frontend_sections(domain_product=unitless_product, nutrition_eval=None, icmr_eval=None, claims_eval=None, ingredient_eval=None)
        prot_item = sections["nutritional_interpretation"].nutrients[0]
        self.assertIsNone(prot_item.value_per_serving, "Must reject conversion when serving unit is piece count")

    def test_19_missing_serving_unit_rejected(self):
        """Scenario 19: Missing serving unit (None) prevents silent conversion."""
        obs = NutrientObservationInput(
            nutrient_code="protein",
            per_100g_value=Decimal("8.0"),
            per_serving_value=None,
            unit="g",
            measurement_basis=MeasurementBasis.PER_100G,
            data_status=NutrientDataStatus.PRESENT,
        )
        no_unit_product = ProductEvaluationInput(
            product_id="test_no_unit",
            product_name="Product with Missing Unit",
            food_form=FoodForm.SOLID,
            serving_size_value=Decimal("25.0"),
            serving_size_unit=None,  # Missing unit
            data_source_id="verified_packaging",
            nutrients={"protein": obs},
        )
        sections = build_frontend_sections(domain_product=no_unit_product, nutrition_eval=None, icmr_eval=None, claims_eval=None, ingredient_eval=None)
        prot_item = sections["nutritional_interpretation"].nutrients[0]
        self.assertIsNone(prot_item.value_per_serving, "Must reject conversion when serving unit is None")

    def test_20_unknown_external_source_never_defaults_to_verified(self):
        """Scenario 20: Unknown third-party source defaults to UNVERIFIED_EXTERNAL, never VERIFIED."""
        dummy_product = ProductEvaluationInput(
            product_id="test_unknown_source",
            product_name="Crowdsourced Granola",
            food_form=FoodForm.SOLID,
            serving_size_value=Decimal("40.0"),
            serving_size_unit="g",
            data_source_id="ad_hoc_source",  # Unknown source
            nutrients={
                "energy": NutrientObservationInput(nutrient_code="energy", per_100g_value=Decimal("400.0"), unit="kcal", measurement_basis=MeasurementBasis.PER_100G, data_status=NutrientDataStatus.PRESENT),
                "protein": NutrientObservationInput(nutrient_code="protein", per_100g_value=Decimal("10.0"), unit="g", measurement_basis=MeasurementBasis.PER_100G, data_status=NutrientDataStatus.PRESENT),
                "carbohydrates": NutrientObservationInput(nutrient_code="carbohydrates", per_100g_value=Decimal("60.0"), unit="g", measurement_basis=MeasurementBasis.PER_100G, data_status=NutrientDataStatus.PRESENT),
                "total_sugars": NutrientObservationInput(nutrient_code="total_sugars", per_100g_value=Decimal("15.0"), unit="g", measurement_basis=MeasurementBasis.PER_100G, data_status=NutrientDataStatus.PRESENT),
                "total_fat": NutrientObservationInput(nutrient_code="total_fat", per_100g_value=Decimal("12.0"), unit="g", measurement_basis=MeasurementBasis.PER_100G, data_status=NutrientDataStatus.PRESENT),
                "sodium": NutrientObservationInput(nutrient_code="sodium", per_100g_value=Decimal("200.0"), unit="mg", measurement_basis=MeasurementBasis.PER_100G, data_status=NutrientDataStatus.PRESENT),
            },
        )
        sections = build_frontend_sections(domain_product=dummy_product, nutrition_eval=None, icmr_eval=None, claims_eval=None, ingredient_eval=None)
        self.assertEqual(sections["nutritional_interpretation"].data_quality, "UNVERIFIED_EXTERNAL")
        self.assertNotEqual(sections["nutritional_interpretation"].data_quality, "VERIFIED")

    def test_21_negative_quantity_in_serving_detected(self):
        """Scenario 21: Negative per-serving quantity is detected as an inconsistency."""
        inconsistent_nutrients = {
            "protein": NutrientObservationInput(
                nutrient_code="protein",
                per_100g_value=Decimal("8.0"),
                per_serving_value=Decimal("-2.0"),  # Negative per-serving quantity
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
        }
        issues = validate_nutrient_consistency(inconsistent_nutrients)
        self.assertTrue(
            any("per-serving quantity cannot be negative" in issue for issue in issues),
            f"Expected negative per-serving inconsistency, got: {issues}",
        )

    def test_22_trans_fat_exceeding_total_fat_per_serving_detected(self):
        """Scenario 22: Trans fat > total fat per serving is detected as an inconsistency."""
        inconsistent_nutrients = {
            "total_fat": NutrientObservationInput(
                nutrient_code="total_fat",
                per_100g_value=Decimal("5.0"),
                per_serving_value=Decimal("1.0"),
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
            "trans_fat": NutrientObservationInput(
                nutrient_code="trans_fat",
                per_100g_value=Decimal("0.5"),
                per_serving_value=Decimal("2.0"),  # Trans fat serving (2.0g) > total fat serving (1.0g)
                unit="g",
                measurement_basis=MeasurementBasis.PER_100G,
                data_status=NutrientDataStatus.PRESENT,
            ),
        }
        issues = validate_nutrient_consistency(inconsistent_nutrients)
        self.assertTrue(
            any("Trans fat (2.0g) exceeds total fat (1.0g) per serving" in issue for issue in issues),
            f"Expected per-serving trans fat violation, got: {issues}",
        )


if __name__ == "__main__":
    unittest.main()
