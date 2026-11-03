"""
Test suite for YumSure verified regulatory seed data integrity and provenance.
Reconciles all seven seed datasets and validates exact entity counts, primary keys,
dataset-to-table mappings, and schema contracts.
"""

import os
import sys
import json
import unittest
import re
import importlib.util
from unittest.mock import patch

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.claim_ast_schema import check_ast_depth_iterative, ClaimConditionGroup


class TestSeedDataIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed_dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'seeds')
        )

    def _load(self, filename: str):
        path = os.path.join(self.seed_dir, filename)
        self.assertTrue(os.path.exists(path), f"Seed file {filename} does not exist at {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_seed_dataset_reconciliation_counts(self):
        """
        Reconcile the 54 vs 63 count discrepancy across all seven seed datasets:
        1. canonical_nutrients_seed.json: 11 rows -> nutrients table
        2. canonical_ingredients_seed.json: 6 rows -> ingredients table
        3. icmr_table_15_1_seed.json: 8 rows -> icmr_nutrient_threshold_rules table
        4. icmr_table_15_2_seed.json: 9 rows -> icmr_matrix_rules table
        5. fssai_schedule_i_claims_seed.json: 14 rows -> regulatory_claim_rules table
        6. ingredient_rules_seed.json: 6 rows -> ingredient_rules table
        Sum of relational database entities = 11 + 6 + 8 + 9 + 14 + 6 = 54 rows.

        7. fssai_schedule_ii_synonyms_seed.json: 9 claim synonym mappings (JSON dictionary).
        Total seed items across all 7 seed files = 54 + 9 = 63 items.
        """
        nutrients = self._load('canonical_nutrients_seed.json')
        ingredients = self._load('canonical_ingredients_seed.json')
        t151 = self._load('icmr_table_15_1_seed.json')
        t152 = self._load('icmr_table_15_2_seed.json')
        claims = self._load('fssai_schedule_i_claims_seed.json')
        ingredient_rules = self._load('ingredient_rules_seed.json')
        synonyms = self._load('fssai_schedule_ii_synonyms_seed.json')

        self.assertEqual(len(nutrients), 11, "Nutrients seed must contain exactly 11 items")
        self.assertEqual(len(ingredients), 6, "Ingredients seed must contain exactly 6 items")
        self.assertEqual(len(t151), 8, "ICMR Table 15.1 seed must contain exactly 8 items")
        self.assertEqual(len(t152), 9, "ICMR Table 15.2 seed must contain exactly 9 items")
        self.assertEqual(len(claims), 14, "Claims seed must contain exactly 14 items")
        self.assertEqual(len(ingredient_rules), 6, "Ingredient rules seed must contain exactly 6 items")
        self.assertEqual(len(synonyms), 9, "Schedule II synonyms must contain exactly 9 synonym mappings")

        # Total relational entities inserted by migration 0003 into PostgreSQL tables
        relational_entity_count = (
            len(nutrients) + len(ingredients) + len(t151) +
            len(t152) + len(claims) + len(ingredient_rules)
        )
        self.assertEqual(relational_entity_count, 54, "Total relational entities must equal exactly 54")

        # Total items across all 7 seed files
        total_seed_items = relational_entity_count + len(synonyms)
        self.assertEqual(total_seed_items, 63, "Total seed items across all 7 files must equal exactly 63")

    def test_canonical_nutrients(self):
        data = self._load('canonical_nutrients_seed.json')
        self.assertEqual(len(data), 11, "Must contain exactly 11 canonical nutrients")
        codes = [n['nutrient_code'] for n in data]
        self.assertEqual(len(codes), len(set(codes)), "Nutrient codes must be unique")
        expected = {
            'energy', 'protein', 'carbohydrates', 'total_sugars', 'added_sugars',
            'total_fat', 'saturated_fat', 'trans_fat', 'sodium', 'dietary_fibre', 'added_fat'
        }
        self.assertEqual(set(codes), expected)
        for n in data:
            self.assertIn('nutrient_code', n)
            self.assertIn('display_name', n)
            self.assertIn('standard_unit', n)
            self.assertIn('is_fssai_mandatory', n)
            self.assertIn(n['standard_unit'], ['g', 'mg', 'kcal'])

    def test_canonical_ingredients(self):
        data = self._load('canonical_ingredients_seed.json')
        self.assertEqual(len(data), 6, "Must contain 6 canonical ingredients")
        codes = [ing['ingredient_code'] for ing in data]
        self.assertEqual(len(codes), len(set(codes)), "Ingredient codes must be unique")
        for ing in data:
            self.assertIn('ingredient_code', ing)
            self.assertIn('canonical_name', ing)
            self.assertIn('category', ing)
            self.assertIn(ing['processing_classification'], [
                'WHOLE_FOOD', 'CULINARY_PROCESSED', 'FUNCTIONAL_ADDITIVE',
                'COSMETIC_ADDITIVE', 'INDUSTRIAL_FRACTION', 'INSUFFICIENT_EVIDENCE', 'UNKNOWN'
            ])
            self.assertIn(ing['sugar_classification'], [
                'NOT_SUGAR', 'INTRINSIC_SUGAR', 'ADDED_FREE_SUGAR',
                'SUGAR_SUBSTITUTE_SWEETENER', 'NON_NUTRITIVE_SWEETENER', 'POLYOL',
                'INSUFFICIENT_EVIDENCE', 'UNKNOWN'
            ])
            self.assertTrue(len(ing.get('classification_evidence', '')) > 0)

    def test_icmr_table_15_1_thresholds(self):
        data = self._load('icmr_table_15_1_seed.json')
        self.assertEqual(len(data), 8, "Must contain 8 threshold rules (4 solid, 4 liquid)")
        rule_ids = [r['rule_id'] for r in data]
        self.assertEqual(len(rule_ids), len(set(rule_ids)), "Rule IDs must be unique")
        forms = [r['food_form'] for r in data]
        self.assertEqual(forms.count('solid'), 4)
        self.assertEqual(forms.count('liquid'), 4)
        for r in data:
            self.assertIn('rule_id', r)
            self.assertIn('rule_code', r)
            self.assertIn('nutrient_code', r)
            self.assertEqual(r['operator'], 'GT')
            self.assertIn(r['measurement_basis'], ['PER_100G', 'PER_100ML'])
            self.assertIn('https://nin.res.in', r['official_url'])
            self.assertEqual(r['verification_status'], 'VERIFIED_GUIDELINE')

    def test_icmr_table_15_2_matrix(self):
        data = self._load('icmr_table_15_2_seed.json')
        self.assertEqual(len(data), 9, "Must contain exactly 9 cells (A1 through C3)")
        matrix_ids = [m['matrix_id'] for m in data]
        self.assertEqual(len(matrix_ids), len(set(matrix_ids)), "Matrix IDs must be unique")
        cells = {m['cell_code']: m for m in data}
        expected_cells = {'A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'}
        self.assertEqual(set(cells.keys()), expected_cells)

        # Independence of UPF and HFSS verification
        # Cell C1: UPF but Non-HFSS
        self.assertTrue(cells['C1']['is_upf'], "C1 must be UPF")
        self.assertFalse(cells['C1']['is_hfss'], "C1 must NOT be HFSS")

        # Cell A1: Non-UPF, Non-HFSS
        self.assertFalse(cells['A1']['is_upf'])
        self.assertFalse(cells['A1']['is_hfss'])

        # Cell C3: UPF and HFSS
        self.assertTrue(cells['C3']['is_upf'])
        self.assertTrue(cells['C3']['is_hfss'])

    def test_fssai_schedule_i_claims(self):
        data = self._load('fssai_schedule_i_claims_seed.json')
        self.assertEqual(len(data), 14, "Must contain 14 statutory claim rules")
        claim_ids = [c['claim_id'] for c in data]
        self.assertEqual(len(claim_ids), len(set(claim_ids)), "Claim IDs must be unique")
        for claim in data:
            self.assertIn('claim_id', claim)
            self.assertIn('claim_code', claim)
            self.assertIn('food_form', claim)
            self.assertIn(claim['food_form'].lower(), ['solid', 'liquid', 'both', 'all'])
            self.assertIn('fssai_regulation_reference', claim)
            expr = claim.get('condition_expression')
            if expr:
                # Must be depth <= 5
                depth = check_ast_depth_iterative(expr, max_depth=5)
                self.assertLessEqual(depth, 5)
                # Must be valid Pydantic AST
                parsed = ClaimConditionGroup.model_validate(expr)
                self.assertIsNotNone(parsed)

    def test_fssai_schedule_ii_synonyms(self):
        data = self._load('fssai_schedule_ii_synonyms_seed.json')
        self.assertEqual(len(data), 9, "Must contain 9 Schedule II synonym entries")
        for claim_code, synonyms in data.items():
            self.assertIsInstance(synonyms, list)
            self.assertTrue(len(synonyms) > 0)
            for syn in synonyms:
                self.assertIsInstance(syn, str)
                self.assertTrue(len(syn.strip()) > 0)

    def test_ingredient_rules(self):
        data = self._load('ingredient_rules_seed.json')
        self.assertEqual(len(data), 6, "Must contain 6 ingredient rules")
        rule_ids = [r['rule_id'] for r in data]
        self.assertEqual(len(rule_ids), len(set(rule_ids)), "Rule IDs must be unique")
        for r in data:
            self.assertIn('rule_id', r)
            self.assertIn('ingredient_code', r)
            self.assertIn(r['rule_type'], [
                'MANDATORY_LABEL_WARNING', 'MAX_PERMISSIBLE_LIMIT',
                'POPULATION_PROHIBITION', 'SPECIAL_CONDITIONS'
            ])
            self.assertTrue(len(r['regulatory_reference']) > 0)


    def test_trans_fat_free_synonyms_regression(self):
        """
        Regression test for FSSAI Schedule II synonyms in trans-fat-free claims:
        1. Both solid and liquid claims contain exact 4 permitted synonyms:
           ['Trans Fat Free', 'Zero Trans Fat', 'Free of Trans Fat', 'No Trans Fat'].
        2. No duplicate synonyms exist in either claim or any other claim record.
        3. All 9 Schedule II synonym mappings remain correctly embedded in Schedule I claims.
        4. Migration 0003 actual embedded JSONB insertion payload contains all 4 synonyms for both claims.
        5. Static offline upgrade SQL evidence confirms the 4 synonyms for both claims.
        """
        claims = self._load('fssai_schedule_i_claims_seed.json')
        claims_by_id = {c['claim_id']: c for c in claims}

        expected_synonyms = [
            "Trans Fat Free",
            "Zero Trans Fat",
            "Free of Trans Fat",
            "No Trans Fat"
        ]

        # 1. Solid trans-fat-free claim contains all four synonyms in exact order
        solid = claims_by_id.get('fssai_claim_trans_fat_free_solid')
        self.assertIsNotNone(solid, "fssai_claim_trans_fat_free_solid must exist in claims seed")
        self.assertEqual(
            solid.get('permitted_synonyms_schedule_ii'),
            expected_synonyms,
            "Solid trans-fat-free claim must contain exact four permitted synonyms"
        )

        # 2. Liquid trans-fat-free claim contains all four synonyms in exact order
        liquid = claims_by_id.get('fssai_claim_trans_fat_free_liquid')
        self.assertIsNotNone(liquid, "fssai_claim_trans_fat_free_liquid must exist in claims seed")
        self.assertEqual(
            liquid.get('permitted_synonyms_schedule_ii'),
            expected_synonyms,
            "Liquid trans-fat-free claim must contain exact four permitted synonyms"
        )

        # 3. No synonym is duplicated in either claim, and across all claims
        self.assertEqual(
            len(solid['permitted_synonyms_schedule_ii']),
            len(set(solid['permitted_synonyms_schedule_ii'])),
            "Solid claim synonyms must not contain duplicates"
        )
        self.assertEqual(
            len(liquid['permitted_synonyms_schedule_ii']),
            len(set(liquid['permitted_synonyms_schedule_ii'])),
            "Liquid claim synonyms must not contain duplicates"
        )
        for c in claims:
            syns = c.get('permitted_synonyms_schedule_ii', [])
            self.assertEqual(len(syns), len(set(syns)), f"Synonyms in {c['claim_id']} must not contain duplicates")

        # 4. All nine Schedule II synonym mappings remain correctly embedded in their respective Schedule I claim records
        expected_claim_codes_with_synonyms = {
            'TRANS_FAT_FREE',
            'LOW_SATURATED_FAT',
            'SOURCE_OF_PROTEIN',
            'HIGH_PROTEIN',
            'SOURCE_OF_DIETARY_FIBRE',
            'HIGH_DIETARY_FIBRE',
            'LOW_SUGARS',
            'NO_ADDED_SUGARS',
            'LOW_SODIUM'
        }
        embedded_claim_codes = {
            c['claim_code'] for c in claims
            if isinstance(c.get('permitted_synonyms_schedule_ii'), list) and len(c['permitted_synonyms_schedule_ii']) > 0
        }
        self.assertEqual(
            embedded_claim_codes,
            expected_claim_codes_with_synonyms,
            "All 9 Schedule II synonym mappings must be embedded in Schedule I claims"
        )
        self.assertEqual(
            sum(1 for c in claims if len(c.get('permitted_synonyms_schedule_ii', [])) > 0),
            14,
            "All 14 Schedule I claims must have embedded Schedule II synonyms"
        )

        # 5. Migration 0003 actual embedded JSONB insertion payload verification
        migration_path = os.path.normpath(os.path.join(
            os.path.dirname(__file__), '..', 'alembic', 'versions', '0003_seed_verified_rule_data.py'
        ))
        self.assertTrue(os.path.exists(migration_path), f"Migration 0003 file must exist at {migration_path}")
        spec = importlib.util.spec_from_file_location('migration_0003', migration_path)
        mig_0003 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mig_0003)

        captured_sqls = []
        with patch.object(mig_0003.op, 'execute', side_effect=lambda stmt: captured_sqls.append(str(stmt))):
            mig_0003.upgrade()

        for cid in ('fssai_claim_trans_fat_free_solid', 'fssai_claim_trans_fat_free_liquid'):
            matches = [s for s in captured_sqls if cid in s]
            self.assertEqual(len(matches), 1, f"Expected 1 insertion statement for {cid} in migration 0003")
            sql_stmt = matches[0]
            jsonb_matches = re.findall(r"'(\[.*?\])'::jsonb", sql_stmt)
            self.assertTrue(len(jsonb_matches) >= 1, f"Expected JSONB array in insertion SQL for {cid}")
            parsed_synonyms = json.loads(jsonb_matches[-1])
            self.assertEqual(
                parsed_synonyms,
                expected_synonyms,
                f"Migration JSONB insertion payload for {cid} must contain exact 4 synonyms in order"
            )
            self.assertEqual(
                len(parsed_synonyms),
                len(set(parsed_synonyms)),
                f"Migration JSONB insertion payload for {cid} must not have duplicates"
            )

        # 6. Static offline SQL evidence verification
        sql_evidence_path = os.path.normpath(os.path.join(
            os.path.dirname(__file__), '..', 'alembic', 'sql_evidence', 'upgrade_0002_to_0003.sql'
        ))
        if os.path.exists(sql_evidence_path):
            with open(sql_evidence_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            expected_jsonb_literal = '\'["Trans Fat Free", "Zero Trans Fat", "Free of Trans Fat", "No Trans Fat"]\'::jsonb'
            self.assertEqual(
                sql_content.count(expected_jsonb_literal),
                2,
                "Static upgrade SQL evidence must contain exact 4-synonym JSONB literal for both solid and liquid claims"
            )


if __name__ == '__main__':
    unittest.main()
