"""
YumSure Regression Tests — Measurement Basis & Nutrient Declaration Integrity.

Covers Tejas's 8 mandatory regression scenarios:
1. PER_100G rule + PER_SERVING observation.
2. PER_100G rule + unresolved (None) observation.
3. PER_100ML rule + PER_100G observation.
4. Missing nutrient value versus explicit Decimal("0").
5. Missing required nutrient never produces PASS.
6. Explicit zero remains distinguishable from missing data.
7. Contract accepts explicit None but rejects omission.
8. Compatibility shim exposes the synchronized contract.
"""

import json
import os
import unittest
from decimal import Decimal
from pydantic import ValidationError

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
)
import app.engines.contracts as compat_contracts
from app.domain.engines.icmr_hfss_engine import evaluate_icmr_hfss
from app.domain.engines.claims_engine import evaluate_claims
from app.domain.engines.nutrition_engine import evaluate_nutrition


class TestMeasurementBasisRegression(unittest.TestCase):
    """Regression tests for measurement basis validation and nutrient null vs zero semantics."""

    @classmethod
    def setUpClass(cls):
        seed_dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "app", "data", "seeds")
        )
        with open(os.path.join(seed_dir, "icmr_table_15_1_seed.json"), "r", encoding="utf-8") as f:
            cls.icmr_15_1 = json.load(f)
        with open(os.path.join(seed_dir, "icmr_table_15_2_seed.json"), "r", encoding="utf-8") as f:
            cls.icmr_15_2 = json.load(f)
        with open(os.path.join(seed_dir, "fssai_schedule_i_claims_seed.json"), "r", encoding="utf-8") as f:
            cls.claims_rules = json.load(f)
        with open(os.path.join(seed_dir, "fssai_schedule_ii_synonyms_seed.json"), "r", encoding="utf-8") as f:
            cls.synonyms = json.load(f)

    # -------------------------------------------------------------------------
    # Scenario 1: PER_100G rule + PER_SERVING observation
    # -------------------------------------------------------------------------
    def test_01_per_100g_rule_with_per_serving_observation(self):
        """Scenario 1: Rule requiring PER_100G must produce INSUFFICIENT_DATA when given PER_SERVING."""
        # Solid product where sodium is declared PER_SERVING
        product = ProductEvaluationInput(
            product_id="prod_per_serving_001",
            product_name="Snack Bites",
            food_form=FoodForm.SOLID,
            nutrients={
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium",
                    measurement_basis=MeasurementBasis.PER_SERVING,
                    per_100g_value=Decimal("50.0"),  # Ambiguous or per-serving in 100g field
                    per_serving_value=Decimal("50.0"),
                    unit="mg",
                    data_status=NutrientDataStatus.PRESENT
                )
            }
        )

        # 1. ICMR HFSS Table 15.1 (requires PER_100G for solid)
        icmr_batch = evaluate_icmr_hfss(product, self.icmr_15_1, self.icmr_15_2)
        sodium_rule = next((r for r in icmr_batch.results if "SALT" in r.rule_code or "salt" in r.rule_id), None)
        self.assertIsNotNone(sodium_rule)
        self.assertEqual(
            sodium_rule.outcome,
            EvaluationStatus.INSUFFICIENT_DATA,
            "ICMR HFSS salt rule must return INSUFFICIENT_DATA for PER_SERVING observation on solid food"
        )

        # 2. Nutrition Engine RDI calculation
        nutrition_batch = evaluate_nutrition(product)
        sodium_rdi = next((r for r in nutrition_batch.results if r.rule_id == "fssai_rdi_contrib_sodium"), None)
        self.assertIsNotNone(sodium_rdi)
        self.assertEqual(
            sodium_rdi.outcome,
            EvaluationStatus.INSUFFICIENT_DATA,
            "Nutrition engine must return INSUFFICIENT_DATA when observation basis is PER_SERVING"
        )

    # -------------------------------------------------------------------------
    # Scenario 2: PER_100G rule + unresolved (None) observation
    # -------------------------------------------------------------------------
    def test_02_per_100g_rule_with_unresolved_observation(self):
        """Scenario 2: Rule requiring PER_100G must produce INSUFFICIENT_DATA when basis is None."""
        product = ProductEvaluationInput(
            product_id="prod_unresolved_002",
            product_name="Generic Flour",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy",
                    measurement_basis=None,  # Unresolved basis
                    per_100g_value=Decimal("350.0"),
                    unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "added_sugars": NutrientObservationInput(
                    nutrient_code="added_sugars",
                    measurement_basis=None,  # Unresolved basis
                    per_100g_value=Decimal("0.0"),
                    unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                )
            }
        )

        # ICMR Table 15.1 Sugar threshold
        icmr_batch = evaluate_icmr_hfss(product, self.icmr_15_1, self.icmr_15_2)
        sugar_rule = next((r for r in icmr_batch.results if "SUGAR" in r.rule_code), None)
        self.assertIsNotNone(sugar_rule)
        self.assertEqual(sugar_rule.outcome, EvaluationStatus.INSUFFICIENT_DATA)
        self.assertIn("added_sugars_measurement_basis", sugar_rule.missing_evidence)

        # Claims engine with Low Sugar / Sugar Free claim
        claims_batch = evaluate_claims(product, self.claims_rules, self.synonyms)
        sugar_claim = next((r for r in claims_batch.results if "SUGAR" in r.rule_code), None)
        if sugar_claim:
            self.assertEqual(sugar_claim.outcome, EvaluationStatus.INSUFFICIENT_DATA)

    # -------------------------------------------------------------------------
    # Scenario 3: PER_100ML rule + PER_100G observation
    # -------------------------------------------------------------------------
    def test_03_per_100ml_rule_with_per_100g_observation(self):
        """Scenario 3: Rule requiring PER_100ML must produce INSUFFICIENT_DATA when given PER_100G."""
        # Beverage product whose nutrition facts panel was declared per 100g (mass) rather than per 100ml (volume)
        product = ProductEvaluationInput(
            product_id="prod_viscous_drink_003",
            product_name="Mango Pulp Drink",
            food_form=FoodForm.LIQUID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy",
                    measurement_basis=MeasurementBasis.PER_100G,  # Incompatible with liquid 100ml rule
                    per_100g_value=Decimal("65.0"),
                    unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=Decimal("30.0"),
                    unit="mg",
                    data_status=NutrientDataStatus.PRESENT
                )
            }
        )

        # ICMR Table 15.1 liquid sodium/salt rule requires PER_100ML
        icmr_batch = evaluate_icmr_hfss(product, self.icmr_15_1, self.icmr_15_2)
        sodium_rule = next((r for r in icmr_batch.results if "SALT" in r.rule_code or "salt" in r.rule_id), None)
        self.assertIsNotNone(sodium_rule)
        self.assertEqual(
            sodium_rule.outcome,
            EvaluationStatus.INSUFFICIENT_DATA,
            "PER_100ML liquid rule must return INSUFFICIENT_DATA when observation is PER_100G"
        )
        self.assertIn("incompatible", sodium_rule.human_readable_explanation)

    # -------------------------------------------------------------------------
    # Scenario 4: Missing nutrient value versus explicit Decimal("0")
    # -------------------------------------------------------------------------
    def test_04_missing_nutrient_value_versus_explicit_zero(self):
        """Scenario 4: None per_100g_value produces INSUFFICIENT_DATA; explicit Decimal('0') evaluates cleanly."""
        # Product A: Value is None
        prod_none = ProductEvaluationInput(
            product_id="prod_none",
            product_name="Test Product None",
            food_form=FoodForm.SOLID,
            nutrients={
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=None,  # Missing value
                    unit="mg",
                    data_status=NutrientDataStatus.PRESENT
                )
            }
        )
        batch_none = evaluate_icmr_hfss(prod_none, self.icmr_15_1, self.icmr_15_2)
        res_none = next((r for r in batch_none.results if "SALT" in r.rule_code), None)
        self.assertIsNotNone(res_none)
        self.assertEqual(res_none.outcome, EvaluationStatus.INSUFFICIENT_DATA)

        # Product B: Value is explicitly Decimal("0.0")
        prod_zero = ProductEvaluationInput(
            product_id="prod_zero",
            product_name="Test Product Zero",
            food_form=FoodForm.SOLID,
            nutrients={
                "sodium": NutrientObservationInput(
                    nutrient_code="sodium",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=Decimal("0.0"),  # Explicit zero
                    unit="mg",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                )
            }
        )
        batch_zero = evaluate_icmr_hfss(prod_zero, self.icmr_15_1, self.icmr_15_2)
        res_zero = next((r for r in batch_zero.results if "SALT" in r.rule_code), None)
        self.assertIsNotNone(res_zero)
        self.assertEqual(res_zero.outcome, EvaluationStatus.PASS)
        self.assertEqual(res_zero.evidence_used["sodium_mg"], 0.0)

    # -------------------------------------------------------------------------
    # Scenario 5: Missing required nutrient never produces PASS
    # -------------------------------------------------------------------------
    def test_05_missing_required_nutrient_never_produces_pass(self):
        """Scenario 5: Missing nutrient declarations must NEVER produce PASS in any engine."""
        # Product with empty nutrients dict
        product = ProductEvaluationInput(
            product_id="prod_empty_nutrients",
            product_name="Unlabelled Food",
            food_form=FoodForm.SOLID,
            nutrients={},
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Trans Fat Free")
            ]
        )

        # 1. ICMR HFSS Engine: all rules must be INSUFFICIENT_DATA (never PASS)
        icmr_batch = evaluate_icmr_hfss(product, self.icmr_15_1, self.icmr_15_2)
        for r in icmr_batch.results:
            self.assertNotEqual(r.outcome, EvaluationStatus.PASS, f"Rule {r.rule_code} emitted false PASS on missing data")

        # 2. Nutrition Engine: all mandatory rules must be INSUFFICIENT_DATA (never PASS)
        nutrition_batch = evaluate_nutrition(product)
        for r in nutrition_batch.results:
            self.assertNotEqual(r.outcome, EvaluationStatus.PASS, f"Rule {r.rule_code} emitted false PASS on missing data")

        # 3. Claims Engine: claim condition must be INSUFFICIENT_DATA (never PASS)
        claims_batch = evaluate_claims(product, self.claims_rules, self.synonyms)
        trans_fat_claim = next((r for r in claims_batch.results if "TRANS_FAT" in r.rule_code), None)
        if trans_fat_claim:
            self.assertNotEqual(trans_fat_claim.outcome, EvaluationStatus.PASS)

    # -------------------------------------------------------------------------
    # Scenario 6: Explicit zero remains distinguishable from missing data
    # -------------------------------------------------------------------------
    def test_06_explicit_zero_distinguishable_from_missing(self):
        """Scenario 6: EXPLICITLY_ZERO satisfies statutory conditions while NOT_DECLARED / None fails safely."""
        # Product with trans fat declared explicitly as 0g, saturated fat 0.5g, energy 300 kcal
        prod_declared_zero = ProductEvaluationInput(
            product_id="prod_zero_trans",
            product_name="Canola Spread",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=Decimal("300.0"),
                    unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=Decimal("0.0"),
                    unit="g",
                    data_status=NutrientDataStatus.EXPLICITLY_ZERO
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=Decimal("0.5"),
                    unit="g",
                    data_status=NutrientDataStatus.PRESENT
                )
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat")
            ]
        )
        batch_declared = evaluate_claims(prod_declared_zero, self.claims_rules, self.synonyms)
        claim_decl = next((r for r in batch_declared.results if "TRANS_FAT_FREE" in r.rule_code), None)
        self.assertIsNotNone(claim_decl)
        self.assertEqual(claim_decl.outcome, EvaluationStatus.PASS)

        # Product with trans fat omitted (NOT_DECLARED)
        prod_omitted = ProductEvaluationInput(
            product_id="prod_omitted_trans",
            product_name="Unknown Spread",
            food_form=FoodForm.SOLID,
            nutrients={
                "energy": NutrientObservationInput(
                    nutrient_code="energy",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=Decimal("300.0"),
                    unit="kcal",
                    data_status=NutrientDataStatus.PRESENT
                ),
                "trans_fat": NutrientObservationInput(
                    nutrient_code="trans_fat",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=None,
                    unit="g",
                    data_status=NutrientDataStatus.NOT_DECLARED
                ),
                "saturated_fat": NutrientObservationInput(
                    nutrient_code="saturated_fat",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=Decimal("0.5"),
                    unit="g",
                    data_status=NutrientDataStatus.PRESENT
                )
            },
            declared_claims=[
                DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat")
            ]
        )
        batch_omitted = evaluate_claims(prod_omitted, self.claims_rules, self.synonyms)
        claim_omit = next((r for r in batch_omitted.results if "TRANS_FAT_FREE" in r.rule_code), None)
        self.assertIsNotNone(claim_omit)
        self.assertEqual(claim_omit.outcome, EvaluationStatus.INSUFFICIENT_DATA)

    # -------------------------------------------------------------------------
    # Scenario 7: Contract accepts explicit None but rejects omission
    # -------------------------------------------------------------------------
    def test_07_contract_accepts_explicit_none_rejects_omission(self):
        """Scenario 7: measurement_basis accepts explicit None, but raises ValidationError if omitted."""
        # 1. Explicit None is accepted
        obs_none = NutrientObservationInput(
            nutrient_code="protein",
            measurement_basis=None,
            per_100g_value=Decimal("10.0"),
            unit="g",
            data_status=NutrientDataStatus.PRESENT
        )
        self.assertIsNone(obs_none.measurement_basis)

        # 2. Valid enum is accepted
        obs_valid = NutrientObservationInput(
            nutrient_code="protein",
            measurement_basis=MeasurementBasis.PER_100G,
            per_100g_value=Decimal("10.0"),
            unit="g",
            data_status=NutrientDataStatus.PRESENT
        )
        self.assertEqual(obs_valid.measurement_basis, MeasurementBasis.PER_100G)

        # 3. Omitting measurement_basis MUST raise ValidationError
        with self.assertRaises(ValidationError) as ctx:
            NutrientObservationInput(
                nutrient_code="protein",
                # measurement_basis omitted
                per_100g_value=Decimal("10.0"),
                unit="g",
                data_status=NutrientDataStatus.PRESENT
            )
        self.assertIn("measurement_basis", str(ctx.exception))

    # -------------------------------------------------------------------------
    # Scenario 8: Compatibility shim exposes the synchronized contract
    # -------------------------------------------------------------------------
    def test_08_compatibility_shim_synchronized(self):
        """Scenario 8: backend/app/engines/contracts.py exposes identical DTO definitions."""
        self.assertIs(
            NutrientObservationInput,
            compat_contracts.NutrientObservationInput,
            "Compatibility shim NutrientObservationInput must be the identical canonical class"
        )
        self.assertIs(
            MeasurementBasis,
            compat_contracts.MeasurementBasis,
            "Compatibility shim MeasurementBasis must be the identical canonical class"
        )
        self.assertIs(
            ProductEvaluationInput,
            compat_contracts.ProductEvaluationInput,
            "Compatibility shim ProductEvaluationInput must be the identical canonical class"
        )

    # -------------------------------------------------------------------------
    # Scenario 9: Liquid product with valid PER_100G declaration when rule permits PER_100G
    # -------------------------------------------------------------------------
    def test_09_liquid_product_with_per_100g_rule_permitted(self):
        """Liquid product with PER_100G observation is evaluated (not rejected) when rule permits PER_100G."""
        product = ProductEvaluationInput(
            product_id="prod_liquid_per_100g",
            product_name="Dense Liquid Beverage",
            food_form=FoodForm.LIQUID,
            nutrients={
                "added_sugars": NutrientObservationInput(
                    nutrient_code="added_sugars",
                    measurement_basis=MeasurementBasis.PER_100G,
                    per_100g_value=Decimal("1.5"),
                    unit="g",
                    data_status=NutrientDataStatus.PRESENT
                )
            }
        )

        # Rule that applies to liquid products and permits PER_100G
        liquid_per_100g_rule = [
            {
                "rule_id": "test_liquid_sugar_100g",
                "rule_code": "HFSS_TEST_SUGAR_LIQUID_100G",
                "nutrient_code": "added_sugars",
                "food_form": "liquid",
                "threshold_value": 2.0,
                "operator": "GT",
                "measurement_basis": "PER_100G",
                "guideline_reference": "Test Guideline"
            }
        ]

        batch = evaluate_icmr_hfss(product, liquid_per_100g_rule, [])
        res = next((r for r in batch.results if r.rule_id == "test_liquid_sugar_100g"), None)
        self.assertIsNotNone(res)
        # 1.5g <= 2.0g threshold -> PASS, NOT INSUFFICIENT_DATA!
        self.assertEqual(
            res.outcome,
            EvaluationStatus.PASS,
            "Liquid product with PER_100G observation must evaluate to PASS when rule permits PER_100G"
        )
        self.assertIn("100g", res.human_readable_explanation)

        # In contrast, when evaluated against standard ICMR liquid rule which requires PER_100ML
        standard_batch = evaluate_icmr_hfss(product, self.icmr_15_1, self.icmr_15_2)
        std_res = next((r for r in standard_batch.results if "SUGAR" in r.rule_code), None)
        self.assertIsNotNone(std_res)
        self.assertEqual(
            std_res.outcome,
            EvaluationStatus.INSUFFICIENT_DATA,
            "Standard PER_100ML liquid rule must strictly reject PER_100G observation as INSUFFICIENT_DATA"
        )


if __name__ == "__main__":
    unittest.main()
