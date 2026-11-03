"""
Automated Test Suite for YumSure Phase 1B.3 Independent Audit Remediation.

Covers:
1. ICMR Table 15.1 and Table 15.2 model separation (DEF-01)
2. Matrix representation of A1-C3 and UPF vs HFSS independence (DEF-01)
3. Ingredient UNKNOWN and INSUFFICIENT_EVIDENCE states (DEF-03)
4. AST maximum nesting depth: shallow, exactly 5, 6+, malformed, empty, invalid operator (DEF-04)
5. Missing condition expression handling (DEF-02)
6. All supported IngredientRule types including legacy types (DEF-06)
7. SQLAlchemy metadata discovery and registration
8. Schema constraints and validation behavior
"""

import unittest
from decimal import Decimal
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.models import (
    Base,
    Nutrient,
    Ingredient,
    IngredientRule,
    RegulatoryClaimRule,
    IcmrNutrientThresholdRule,
    IcmrMatrixRule,
    ICMR_PROCESSING_GROUPS,
    ICMR_NUTRITIONAL_CATEGORIES,
    ICMR_MATRIX_CELLS,
    INGREDIENT_PROCESSING_CLASSES,
    INGREDIENT_SUGAR_CLASSES,
    INGREDIENT_RULE_TYPES,
    MAX_AST_DEPTH,
    validate_ast_structure,
    ClaimConditionGroup,
    ClaimConditionNode,
    ConditionType,
    ComparisonOperator,
    LogicalOperator,
    MeasurementBasis
)


class TestRemediationAudit(unittest.TestCase):

    # -------------------------------------------------------------------------
    # 1. ICMR Table 15.1 and Table 15.2 Model Separation (DEF-01)
    # -------------------------------------------------------------------------
    def test_01_icmr_model_separation(self):
        """Verify Table 15.1 and Table 15.2 are distinct tables with proper FK separation."""
        self.assertEqual(IcmrNutrientThresholdRule.__tablename__, "icmr_nutrient_threshold_rules")
        self.assertEqual(IcmrMatrixRule.__tablename__, "icmr_matrix_rules")

        # Table 15.1 threshold rule MUST have nutrient_code FK
        t15_1_cols = [c.name for c in IcmrNutrientThresholdRule.__table__.columns]
        self.assertIn("nutrient_code", t15_1_cols)
        self.assertIn("threshold_value", t15_1_cols)
        self.assertIn("operator", t15_1_cols)
        self.assertIn("measurement_basis", t15_1_cols)

        # Table 15.2 matrix rule MUST NOT have nutrient_code FK
        t15_2_cols = [c.name for c in IcmrMatrixRule.__table__.columns]
        self.assertNotIn("nutrient_code", t15_2_cols)
        self.assertNotIn("target_nutrient_code", t15_2_cols)
        self.assertIn("processing_group", t15_2_cols)
        self.assertIn("nutritional_category", t15_2_cols)
        self.assertIn("cell_code", t15_2_cols)
        self.assertIn("is_upf", t15_2_cols)
        self.assertIn("is_hfss", t15_2_cols)

    # -------------------------------------------------------------------------
    # 2. Matrix Representation of A1-C3 & UPF vs HFSS Independence (DEF-01)
    # -------------------------------------------------------------------------
    def test_02_matrix_a1_c3_representation(self):
        """Verify all 9 matrix cells can be represented and demonstrate UPF/HFSS independence."""
        self.assertEqual(len(ICMR_MATRIX_CELLS), 9)

        # Cell C1: Ultra-processed food, low calorie / non-HFSS
        cell_c1 = IcmrMatrixRule(
            matrix_id="matrix_c1",
            cell_code="C1",
            processing_group="GROUP_C",
            nutritional_category="CAT_1",
            applicable_food_form="solid",
            is_upf=True,
            is_hfss=False,
            energy_min_kcal=None,
            energy_max_kcal=Decimal("250.0"),
            processing_description="Ultra-processed formulation with cosmetic additives.",
            nutritional_description="Low energy density (<=250 kcal/100g).",
            consumer_guidance="Ultra-processed food. Consume rarely regardless of low calorie content."
        )
        self.assertTrue(cell_c1.is_upf)
        self.assertFalse(cell_c1.is_hfss)

        # Cell A3: Minimally processed food, high calorie / HFSS
        cell_a3 = IcmrMatrixRule(
            matrix_id="matrix_a3",
            cell_code="A3",
            processing_group="GROUP_A",
            nutritional_category="CAT_3",
            applicable_food_form="solid",
            is_upf=False,
            is_hfss=True,
            energy_min_kcal=Decimal("500.0"),
            energy_max_kcal=None,
            processing_description="Whole or minimally processed food.",
            nutritional_description="High energy density (>500 kcal/100g, e.g. whole nuts).",
            consumer_guidance="Wholesome nutrient-dense food; consume in controlled portions."
        )
        self.assertFalse(cell_a3.is_upf)
        self.assertTrue(cell_a3.is_hfss)

    # -------------------------------------------------------------------------
    # 3. Ingredient UNKNOWN and INSUFFICIENT_EVIDENCE States (DEF-03)
    # -------------------------------------------------------------------------
    def test_03_ingredient_classification_states(self):
        """Verify ingredient classifications include UNKNOWN and INSUFFICIENT_EVIDENCE and default to UNKNOWN."""
        self.assertIn("UNKNOWN", INGREDIENT_PROCESSING_CLASSES)
        self.assertIn("INSUFFICIENT_EVIDENCE", INGREDIENT_PROCESSING_CLASSES)
        self.assertIn("UNKNOWN", INGREDIENT_SUGAR_CLASSES)
        self.assertIn("INSUFFICIENT_EVIDENCE", INGREDIENT_SUGAR_CLASSES)

        # Verify defaults are strictly UNKNOWN
        ing = Ingredient(
            ingredient_code="test_herb_extract",
            canonical_name="Unknown Herb Extract",
            category="OTHER"
        )
        self.assertEqual(ing.processing_classification, "UNKNOWN")
        self.assertEqual(ing.sugar_classification, "UNKNOWN")

        # Explicit INSUFFICIENT_EVIDENCE
        ing_insuf = Ingredient(
            ingredient_code="test_spice_blend",
            canonical_name="Proprietary Masala",
            category="OTHER",
            processing_classification="INSUFFICIENT_EVIDENCE",
            sugar_classification="INSUFFICIENT_EVIDENCE",
            classification_evidence="Recipe proportions proprietary; processing method unverified."
        )
        self.assertEqual(ing_insuf.processing_classification, "INSUFFICIENT_EVIDENCE")

    # -------------------------------------------------------------------------
    # 4. AST Nesting Depth Protection (DEF-04)
    # -------------------------------------------------------------------------
    def _create_nested_ast(self, depth: int) -> dict:
        """Helper to generate an AST with exactly `depth` nested expression groups."""
        leaf = {
            "type": "NUTRIENT_THRESHOLD",
            "nutrient_code": "protein",
            "operator": "GTE",
            "threshold_value": 5.0,
            "measurement_basis": "PER_100G"
        }
        current = {"logical_operator": "AND", "conditions": [leaf]}
        for _ in range(depth - 1):
            current = {
                "logical_operator": "AND",
                "conditions": [
                    {
                        "type": "EXPRESSION_GROUP",
                        "nested_expression": current
                    }
                ]
            }
        return current

    def test_04_ast_depth_limits(self):
        """Verify shallow expressions pass, depth 5 passes, depth 6+ rejected."""
        # Depth 1: Pass
        ast_1 = self._create_nested_ast(1)
        res_1 = validate_ast_structure(ast_1)
        self.assertIsNotNone(res_1)

        # Depth 5: Exactly maximum limit -> Pass
        ast_5 = self._create_nested_ast(5)
        res_5 = validate_ast_structure(ast_5)
        self.assertIsNotNone(res_5)

        # Depth 6: Exceeds maximum limit -> Must raise ValueError
        ast_6 = self._create_nested_ast(6)
        with self.assertRaises(ValueError) as ctx:
            validate_ast_structure(ast_6)
        self.assertIn("AST nesting depth exceeds maximum permitted limit", str(ctx.exception))

        # Deep recursion attack (depth 50): Must be caught iteratively without RecursionError
        ast_50 = self._create_nested_ast(50)
        with self.assertRaises(ValueError) as ctx:
            validate_ast_structure(ast_50)
        self.assertIn("AST nesting depth exceeds maximum permitted limit", str(ctx.exception))

    def test_05_ast_invalid_and_empty_structures(self):
        """Verify empty groups and invalid operators are rejected."""
        # Empty dictionary
        with self.assertRaises(Exception):
            validate_ast_structure({})

        # Empty conditions array
        with self.assertRaises(Exception):
            validate_ast_structure({"logical_operator": "AND", "conditions": []})

        # Invalid operator
        with self.assertRaises(Exception):
            validate_ast_structure({
                "logical_operator": "AND",
                "conditions": [
                    {
                        "type": "NUTRIENT_THRESHOLD",
                        "nutrient_code": "protein",
                        "operator": "INVALID_OP",
                        "threshold_value": 5.0,
                        "measurement_basis": "PER_100G"
                    }
                ]
            })

    # -------------------------------------------------------------------------
    # 5. Missing Condition Expression Handling (DEF-02)
    # -------------------------------------------------------------------------
    def test_06_missing_condition_expression(self):
        """Verify condition_expression can be None and is handled safely without crashing."""
        claim = RegulatoryClaimRule(
            claim_id="test_claim_pending_ast",
            claim_code="PENDING_CLAIM",
            claim_title="Draft Claim Under Regulatory Review",
            claim_family="NUTRIENT_CONTENT_CLAIM",
            food_form="solid",
            fssai_regulation_reference="FSSAI Gazette 2022 Draft",
            consumer_explanation="Draft explanation",
            condition_expression=None  # Explicitly None
        )
        self.assertIsNone(claim.condition_expression)

        # validate_ast_structure with allow_none=True
        self.assertIsNone(validate_ast_structure(None, allow_none=True))

        # validate_ast_structure with allow_none=False
        with self.assertRaises(ValueError):
            validate_ast_structure(None, allow_none=False)

    # -------------------------------------------------------------------------
    # 6. Reconciled IngredientRule Types (DEF-06)
    # -------------------------------------------------------------------------
    def test_07_ingredient_rule_types(self):
        """Verify both foundational types and enhanced contract types are supported."""
        expected_types = {
            'MANDATORY_LABEL_WARNING',
            'MAX_PERMISSIBLE_LIMIT',
            'POPULATION_PROHIBITION',
            'SPECIAL_CONDITIONS',
            'WARNING_MANDATE',
            'MAX_LIMIT'
        }
        self.assertTrue(expected_types.issubset(set(INGREDIENT_RULE_TYPES)))

        # Foundational Tejas types
        r1 = IngredientRule(
            rule_id="r1",
            ingredient_code="ing1",
            rule_type="WARNING_MANDATE",
            regulatory_reference="Ref 1",
            consumer_guidance="Guidance 1"
        )
        self.assertEqual(r1.rule_type, "WARNING_MANDATE")

        r2 = IngredientRule(
            rule_id="r2",
            ingredient_code="ing2",
            rule_type="MAX_LIMIT",
            regulatory_reference="Ref 2",
            consumer_guidance="Guidance 2"
        )
        self.assertEqual(r2.rule_type, "MAX_LIMIT")

        # Enhanced contract types
        r3 = IngredientRule(
            rule_id="r3",
            ingredient_code="ing3",
            rule_type="MANDATORY_LABEL_WARNING",
            regulatory_reference="Ref 3",
            consumer_guidance="Guidance 3"
        )
        self.assertEqual(r3.rule_type, "MANDATORY_LABEL_WARNING")

    # -------------------------------------------------------------------------
    # 7. Metadata Registration & Discovered Tables
    # -------------------------------------------------------------------------
    def test_08_sqlalchemy_metadata_registration(self):
        """Verify all 13 tables are discovered by Base.metadata."""
        tables = set(Base.metadata.tables.keys())
        expected_tables = {
            'data_sources',
            'products',
            'nutrients',
            'product_nutrients',
            'ingredients',
            'product_ingredients',
            'regulatory_claim_rules',
            'ingredient_rules',
            'nutrition_interpretation_rules',
            'icmr_nutrient_threshold_rules',
            'icmr_matrix_rules',
            'ai_explanations',
            'scan_history'
        }
        self.assertTrue(expected_tables.issubset(tables))


if __name__ == "__main__":
    unittest.main()

