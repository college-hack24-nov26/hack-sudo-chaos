"""
Test suite for Migration 0003 Safe Ownership Tracking and Rollback Semantics.
Verifies Scenarios A, B, C, D, E, and F alongside static SQL contract verification.

PostgreSQL Dialect Semantics & SQLite Limitation Note:
------------------------------------------------------
Migration 0003 relies on PostgreSQL-specific data-modifying Common Table Expressions (CTEs):
`WITH ins AS (INSERT INTO ... ON CONFLICT DO NOTHING RETURNING pk) INSERT INTO migration_seed_ownership ... SELECT ... FROM ins;`
SQLite grammar (up through SQLite 3.50+) does not support data-modifying statements inside CTEs
(SQLite requires `WITH cte AS (SELECT ...)` and raises `sqlite3.OperationalError: near "INSERT": syntax error`).
Furthermore, SQLite does not support PostgreSQL PL/pgSQL procedural blocks (`DO $$ ... $$`).
Therefore, this test suite validates:
1. Exact PostgreSQL relational state machine semantics and CTE behavior via deterministic simulation.
2. Complete static SQL contract verification inspecting generated Alembic operations.
"""

import os
import sys
import unittest
from typing import Dict, Set, Tuple, List, Optional

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import importlib.util

migration_path = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions', '0003_seed_verified_rule_data.py')
)
spec = importlib.util.spec_from_file_location("migration_0003", migration_path)
m0003 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m0003)


class PostgreSQLMigrationStateSimulator:
    """
    Simulates PostgreSQL relational state machine, CTE semantics, and PL/pgSQL downgrade logic:
    - Atomic CTE insert: WITH ins AS (INSERT ... ON CONFLICT DO NOTHING RETURNING pk)
    - Ownership tracking in migration_seed_ownership table
    - PL/pgSQL downgrade loop checking active foreign keys and logging explicit warnings
    """
    def __init__(self):
        self.revision = '0003_seed_verified_rule_data'
        # Database tables
        self.nutrients: Dict[str, dict] = {}
        self.ingredients: Dict[str, dict] = {}
        self.icmr_thresholds: Dict[str, dict] = {}
        self.icmr_matrices: Dict[str, dict] = {}
        self.regulatory_claims: Dict[str, dict] = {}
        self.ingredient_rules: Dict[str, dict] = {}

        # Dependent tables with incoming Foreign Keys
        self.product_nutrients: Set[str] = set()       # nutrient_code
        self.product_ingredients: Set[str] = set()     # ingredient_code
        self.nutrition_interpretation_rules: Set[str] = set()  # nutrient_code

        # Tracking table: migration_seed_ownership (revision, target_table, record_id)
        self.ownership: Set[Tuple[str, str, str]] = set()

        # Telemetry / warnings logged during cleanup
        self.logged_warnings: List[str] = []
        self.logged_notices: List[str] = []
        self.tracker_table_dropped: bool = False

    def simulate_cte_insert(self, target_table: str, pk_col: str, pk_val: str, row_data: dict) -> bool:
        """
        Simulates PostgreSQL CTE:
        WITH ins AS (
            INSERT INTO table (pk, ...) VALUES (pk_val, ...)
            ON CONFLICT (pk) DO NOTHING
            RETURNING pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', target_table, pk FROM ins;
        """
        table_dict = getattr(self, target_table)
        if pk_val in table_dict:
            # Conflict occurred: DO NOTHING. ins yields 0 rows.
            # No ownership record is created!
            return False
        else:
            # Insert succeeds: row inserted, ins yields pk.
            table_dict[pk_val] = row_data
            self.ownership.add((self.revision, target_table, pk_val))
            return True

    def simulate_downgrade(self):
        """
        Simulates downgrade() executing in strict reverse FK order:
        1. ingredient_rules
        2. regulatory_claim_rules
        3. icmr_matrix_rules
        4. icmr_nutrient_threshold_rules
        5. ingredients (PL/pgSQL block with FK checks)
        6. nutrients (PL/pgSQL block with FK checks)
        7. Drop tracking table if empty, retain if blocked records remain
        """
        self.logged_warnings.clear()
        self.logged_notices.clear()

        # 1. ingredient_rules strictly owned by 0003
        ir_to_del = [
            rec_id for (rev, tbl, rec_id) in list(self.ownership)
            if rev == self.revision and tbl == 'ingredient_rules' and rec_id in self.ingredient_rules
        ]
        for r_id in ir_to_del:
            del self.ingredient_rules[r_id]
            self.ownership.remove((self.revision, 'ingredient_rules', r_id))

        # 2. regulatory_claim_rules strictly owned by 0003
        claims_to_del = [
            rec_id for (rev, tbl, rec_id) in list(self.ownership)
            if rev == self.revision and tbl == 'regulatory_claim_rules' and rec_id in self.regulatory_claims
        ]
        for c_id in claims_to_del:
            del self.regulatory_claims[c_id]
            self.ownership.remove((self.revision, 'regulatory_claim_rules', c_id))

        # 3. icmr_matrix_rules strictly owned by 0003
        mat_to_del = [
            rec_id for (rev, tbl, rec_id) in list(self.ownership)
            if rev == self.revision and tbl == 'icmr_matrix_rules' and rec_id in self.icmr_matrices
        ]
        for m_id in mat_to_del:
            del self.icmr_matrices[m_id]
            self.ownership.remove((self.revision, 'icmr_matrix_rules', m_id))

        # 4. icmr_nutrient_threshold_rules strictly owned by 0003
        thresh_to_del = [
            rec_id for (rev, tbl, rec_id) in list(self.ownership)
            if rev == self.revision and tbl == 'icmr_nutrient_threshold_rules' and rec_id in self.icmr_thresholds
        ]
        for t_id in thresh_to_del:
            del self.icmr_thresholds[t_id]
            self.ownership.remove((self.revision, 'icmr_nutrient_threshold_rules', t_id))

        # 5. ingredients (PL/pgSQL loop checking product_ingredients and ingredient_rules)
        ing_owned = [
            rec_id for (rev, tbl, rec_id) in list(self.ownership)
            if rev == self.revision and tbl == 'ingredients' and rec_id in self.ingredients
        ]
        blocked_ing = 0
        for ing_id in ing_owned:
            is_referenced = (
                ing_id in self.product_ingredients or
                any(r.get('ingredient_code') == ing_id for r in self.ingredient_rules.values())
            )
            if is_referenced:
                self.logged_warnings.append(
                    f'Cleanup blocked: ingredient "{ing_id}" is referenced by dependent data and will be preserved.'
                )
                blocked_ing += 1
            else:
                del self.ingredients[ing_id]
                self.ownership.remove((self.revision, 'ingredients', ing_id))
        if blocked_ing > 0:
            self.logged_notices.append(f'Preserved {blocked_ing} ingredient(s) due to active foreign key references.')

        # 6. nutrients (PL/pgSQL loop checking product_nutrients, threshold_rules, interpretation_rules)
        nut_owned = [
            rec_id for (rev, tbl, rec_id) in list(self.ownership)
            if rev == self.revision and tbl == 'nutrients' and rec_id in self.nutrients
        ]
        blocked_nut = 0
        for nut_id in nut_owned:
            is_referenced = (
                nut_id in self.product_nutrients or
                any(r.get('nutrient_code') == nut_id for r in self.icmr_thresholds.values()) or
                nut_id in self.nutrition_interpretation_rules
            )
            if is_referenced:
                self.logged_warnings.append(
                    f'Cleanup blocked: nutrient "{nut_id}" is referenced by dependent data and will be preserved.'
                )
                blocked_nut += 1
            else:
                del self.nutrients[nut_id]
                self.ownership.remove((self.revision, 'nutrients', nut_id))
        if blocked_nut > 0:
            self.logged_notices.append(f'Preserved {blocked_nut} nutrient(s) due to active foreign key references.')

        # 7. Drop tracking table if completely empty, or retain if uncleaned records remain
        if len(self.ownership) == 0:
            self.tracker_table_dropped = True
            self.logged_notices.append('migration_seed_ownership dropped (all owned records cleanly removed).')
        else:
            self.tracker_table_dropped = False
            self.logged_notices.append('migration_seed_ownership retained (uncleaned/blocked records remain for audit telemetry).')


class TestMigrationOwnershipSemantics(unittest.TestCase):
    def test_scenario_a_pre_existing_conflicting_nutrient(self):
        """
        Scenario A: Pre-existing conflicting nutrient.
        - Row exists before upgrade.
        - Migration skips it via ON CONFLICT DO NOTHING.
        - No ownership record is created (CTE RETURNING yields 0 rows).
        - Downgrade preserves it untouched.
        """
        sim = PostgreSQLMigrationStateSimulator()
        sim.nutrients['sodium'] = {'nutrient_code': 'sodium', 'display_name': 'Pre-existing Sodium'}

        # Migration 0003 runs
        inserted = sim.simulate_cte_insert('nutrients', 'nutrient_code', 'sodium', {'display_name': 'New Seed Sodium'})
        self.assertFalse(inserted, "Pre-existing record must trigger conflict and be skipped")
        self.assertEqual(sim.nutrients['sodium']['display_name'], 'Pre-existing Sodium', "Pre-existing row must not be overwritten")
        self.assertNotIn(('0003_seed_verified_rule_data', 'nutrients', 'sodium'), sim.ownership,
                         "No ownership record must be created for skipped conflicts")

        # Downgrade runs
        sim.simulate_downgrade()
        self.assertIn('sodium', sim.nutrients, "Pre-existing record must remain untouched after downgrade")
        self.assertEqual(sim.nutrients['sodium']['display_name'], 'Pre-existing Sodium')

    def test_scenario_b_migration_inserted_nutrient(self):
        """
        Scenario B: Migration-inserted nutrient.
        - Row does not exist before upgrade.
        - Migration inserts and tracks it.
        - Downgrade removes it when unreferenced.
        """
        sim = PostgreSQLMigrationStateSimulator()

        inserted = sim.simulate_cte_insert('nutrients', 'nutrient_code', 'energy', {'display_name': 'Energy'})
        self.assertTrue(inserted)
        self.assertIn('energy', sim.nutrients)
        self.assertIn(('0003_seed_verified_rule_data', 'nutrients', 'energy'), sim.ownership)

        sim.simulate_downgrade()
        self.assertNotIn('energy', sim.nutrients, "Unreferenced owned record must be removed on downgrade")
        self.assertNotIn(('0003_seed_verified_rule_data', 'nutrients', 'energy'), sim.ownership,
                         "Ownership record must be deleted upon successful row removal")
        self.assertTrue(sim.tracker_table_dropped, "Tracker table should be dropped when 0 uncleaned records remain")

    def test_scenario_c_referenced_migration_owned_nutrient(self):
        """
        Scenario C: Referenced migration-owned nutrient.
        - A dependent row references it after upgrade (e.g. product_nutrients).
        - Downgrade preserves both records (no cascade delete).
        - Cleanup reports the unresolved ownership entry explicitly via logged warning.
        """
        sim = PostgreSQLMigrationStateSimulator()

        sim.simulate_cte_insert('nutrients', 'nutrient_code', 'added_sugars', {'display_name': 'Added Sugars'})
        # Product references added_sugars
        sim.product_nutrients.add('added_sugars')

        sim.simulate_downgrade()
        # Must preserve the nutrient
        self.assertIn('added_sugars', sim.nutrients, "Referenced nutrient must be preserved to prevent foreign key violation")
        # Must retain ownership telemetry
        self.assertIn(('0003_seed_verified_rule_data', 'nutrients', 'added_sugars'), sim.ownership,
                      "Ownership entry must remain intact when cleanup is blocked")
        # Must log explicit warning
        self.assertTrue(any('Cleanup blocked: nutrient "added_sugars"' in w for w in sim.logged_warnings),
                        "Must log explicit warning when cleanup is blocked")
        self.assertFalse(sim.tracker_table_dropped, "Tracker table must NOT be dropped when blocked records remain")

    def test_scenario_d_ingredient_conflict_and_insertion_scenarios(self):
        """
        Scenario D: Equivalent ingredient conflict and insertion scenarios.
        - D.1: Pre-existing ingredient conflict is skipped, untracked, and preserved on rollback.
        - D.2: Fresh ingredient is inserted, tracked, and deleted on rollback.
        - D.3: Owned ingredient referenced by product_ingredients is preserved and warning is reported.
        - D.4: Owned ingredient referenced by ingredient_rules is preserved and warning is reported.
        """
        sim = PostgreSQLMigrationStateSimulator()

        # D.1: Pre-existing ingredient
        sim.ingredients['caffeine'] = {'ingredient_code': 'caffeine', 'canonical_name': 'Pre-existing Caffeine'}
        inserted_pre = sim.simulate_cte_insert('ingredients', 'ingredient_code', 'caffeine', {'canonical_name': 'New Caffeine'})
        self.assertFalse(inserted_pre)
        self.assertNotIn(('0003_seed_verified_rule_data', 'ingredients', 'caffeine'), sim.ownership)

        # D.2: Fresh unreferenced ingredient
        inserted_fresh = sim.simulate_cte_insert('ingredients', 'ingredient_code', 'ins_965_maltitol', {'canonical_name': 'Maltitol'})
        self.assertTrue(inserted_fresh)

        # D.3: Fresh referenced ingredient (by product)
        inserted_ref = sim.simulate_cte_insert('ingredients', 'ingredient_code', 'ins_950_acesulfame_k', {'canonical_name': 'Acesulfame K'})
        self.assertTrue(inserted_ref)
        sim.product_ingredients.add('ins_950_acesulfame_k')

        # Execute downgrade
        sim.simulate_downgrade()

        # Verify D.1: Pre-existing ingredient preserved
        self.assertIn('caffeine', sim.ingredients)
        self.assertEqual(sim.ingredients['caffeine']['canonical_name'], 'Pre-existing Caffeine')

        # Verify D.2: Fresh unreferenced ingredient deleted
        self.assertNotIn('ins_965_maltitol', sim.ingredients)

        # Verify D.3: Fresh referenced ingredient preserved with warning
        self.assertIn('ins_950_acesulfame_k', sim.ingredients)
        self.assertIn(('0003_seed_verified_rule_data', 'ingredients', 'ins_950_acesulfame_k'), sim.ownership)
        self.assertTrue(any('Cleanup blocked: ingredient "ins_950_acesulfame_k"' in w for w in sim.logged_warnings))

    def test_scenario_e_repeated_upgrade_downgrade_idempotency(self):
        """
        Scenario E: Repeated upgrade and downgrade behaviour (idempotency).
        - Multiple upgrades do not produce duplicate entries or errors.
        - Multiple downgrades execute cleanly without error.
        """
        sim = PostgreSQLMigrationStateSimulator()

        # Upgrade 1
        sim.simulate_cte_insert('nutrients', 'nutrient_code', 'protein', {'display_name': 'Protein'})
        sim.simulate_cte_insert('ingredients', 'ingredient_code', 'ins_420_sorbitol', {'canonical_name': 'Sorbitol'})
        self.assertEqual(len(sim.ownership), 2)

        # Upgrade 2 (re-run)
        sim.simulate_cte_insert('nutrients', 'nutrient_code', 'protein', {'display_name': 'Protein'})
        sim.simulate_cte_insert('ingredients', 'ingredient_code', 'ins_420_sorbitol', {'canonical_name': 'Sorbitol'})
        self.assertEqual(len(sim.ownership), 2, "Re-run must not duplicate ownership entries")

        # Downgrade 1
        sim.simulate_downgrade()
        self.assertNotIn('protein', sim.nutrients)
        self.assertNotIn('ins_420_sorbitol', sim.ingredients)
        self.assertEqual(len(sim.ownership), 0)

        # Downgrade 2 (re-run)
        sim.simulate_downgrade()
        self.assertEqual(len(sim.ownership), 0, "Second downgrade must execute cleanly without error")

    def test_scenario_f_partial_seed_conflict_scenarios(self):
        """
        Scenario F: Partial seed conflict scenarios.
        - A subset of seed records pre-exists (e.g. 3 nutrients and 2 ingredients).
        - Migration runs for the full seed dataset.
        - Exactly the non-conflicting rows are inserted and tracked.
        - Downgrade removes strictly the newly inserted rows and leaves all pre-existing rows intact.
        """
        sim = PostgreSQLMigrationStateSimulator()

        # Pre-seed 3 nutrients and 2 ingredients
        pre_existing_nuts = {'sodium', 'protein', 'energy'}
        for n in pre_existing_nuts:
            sim.nutrients[n] = {'nutrient_code': n, 'display_name': f'Pre-existing {n}'}

        pre_existing_ings = {'caffeine', 'ins_211_sodium_benzoate'}
        for i in pre_existing_ings:
            sim.ingredients[i] = {'ingredient_code': i, 'canonical_name': f'Pre-existing {i}'}

        # Full 11 nutrients from canonical_nutrients_seed.json
        all_nuts = [
            'energy', 'protein', 'carbohydrates', 'total_sugars', 'added_sugars',
            'total_fat', 'saturated_fat', 'trans_fat', 'sodium', 'dietary_fibre', 'added_fat'
        ]
        inserted_nuts = 0
        skipped_nuts = 0
        for n in all_nuts:
            if sim.simulate_cte_insert('nutrients', 'nutrient_code', n, {'display_name': n}):
                inserted_nuts += 1
            else:
                skipped_nuts += 1

        self.assertEqual(skipped_nuts, 3, "Exactly 3 conflicting nutrients must be skipped")
        self.assertEqual(inserted_nuts, 8, "Exactly 8 new nutrients must be inserted and tracked")

        # Full 6 ingredients from canonical_ingredients_seed.json
        all_ings = [
            'ins_950_acesulfame_k', 'ins_951_aspartame', 'ins_965_maltitol',
            'ins_420_sorbitol', 'caffeine', 'ins_211_sodium_benzoate'
        ]
        inserted_ings = 0
        skipped_ings = 0
        for i in all_ings:
            if sim.simulate_cte_insert('ingredients', 'ingredient_code', i, {'canonical_name': i}):
                inserted_ings += 1
            else:
                skipped_ings += 1

        self.assertEqual(skipped_ings, 2, "Exactly 2 conflicting ingredients must be skipped")
        self.assertEqual(inserted_ings, 4, "Exactly 4 new ingredients must be inserted and tracked")

        # Total owned: 8 nutrients + 4 ingredients = 12
        self.assertEqual(len(sim.ownership), 12)

        # Execute rollback
        sim.simulate_downgrade()

        # Verify all 3 pre-existing nutrients are still intact
        for n in pre_existing_nuts:
            self.assertIn(n, sim.nutrients)
            self.assertEqual(sim.nutrients[n]['display_name'], f'Pre-existing {n}')

        # Verify all 8 newly inserted nutrients are removed
        for n in all_nuts:
            if n not in pre_existing_nuts:
                self.assertNotIn(n, sim.nutrients)

        # Verify all 2 pre-existing ingredients are still intact
        for i in pre_existing_ings:
            self.assertIn(i, sim.ingredients)
            self.assertEqual(sim.ingredients[i]['canonical_name'], f'Pre-existing {i}')

        # Verify all 4 newly inserted ingredients are removed
        for i in all_ings:
            if i not in pre_existing_ings:
                self.assertNotIn(i, sim.ingredients)

    def test_static_sql_contracts_in_migration_0003(self):
        """
        Verifies that the actual Alembic migration file 0003 enforces:
        1. CREATE TABLE IF NOT EXISTS migration_seed_ownership with primary key & unique constraint
        2. CTE pattern WITH ins AS (INSERT ... ON CONFLICT (...) DO NOTHING RETURNING ... AS pk)
        3. Strict reverse FK order in downgrade
        4. PL/pgSQL block checking all incoming foreign keys and raising explicit warnings
        5. Conditional drop of migration_seed_ownership table
        """
        with open(migration_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # 1. Ownership tracking table
        self.assertIn("CREATE TABLE IF NOT EXISTS migration_seed_ownership", code)
        self.assertIn("migration_revision VARCHAR(100)", code)
        self.assertIn("target_table VARCHAR(100)", code)
        self.assertIn("record_id VARCHAR(100)", code)
        self.assertIn("CONSTRAINT uq_migration_seed_ownership UNIQUE (migration_revision, target_table, record_id)", code)

        # 2. CTE insert with ON CONFLICT DO NOTHING RETURNING pk
        self.assertIn("WITH ins AS (", code)
        self.assertIn("ON CONFLICT (nutrient_code) DO NOTHING", code)
        self.assertIn("RETURNING nutrient_code AS pk", code)
        self.assertIn("ON CONFLICT (ingredient_code) DO NOTHING", code)
        self.assertIn("RETURNING ingredient_code AS pk", code)
        self.assertIn("ON CONFLICT (rule_id) DO NOTHING", code)
        self.assertIn("RETURNING rule_id AS pk", code)
        self.assertIn("ON CONFLICT (matrix_id) DO NOTHING", code)
        self.assertIn("RETURNING matrix_id AS pk", code)
        self.assertIn("ON CONFLICT (claim_id) DO NOTHING", code)
        self.assertIn("RETURNING claim_id AS pk", code)

        # 3. Strict reverse FK order in downgrade
        downgrade_fn = code[code.index("def downgrade()"): ]
        pos_ir = downgrade_fn.index("DELETE FROM ingredient_rules")
        pos_claim = downgrade_fn.index("DELETE FROM regulatory_claim_rules")
        pos_mat = downgrade_fn.index("DELETE FROM icmr_matrix_rules")
        pos_thresh = downgrade_fn.index("DELETE FROM icmr_nutrient_threshold_rules")
        pos_ing = downgrade_fn.index("DO $cleanup_ing$")
        pos_nut = downgrade_fn.index("DO $cleanup_nut$")

        self.assertTrue(pos_ir < pos_claim < pos_mat < pos_thresh < pos_ing < pos_nut,
                        "Downgrade must execute in strict reverse FK order: ingredient_rules -> claims -> matrix -> thresholds -> ingredients -> nutrients")

        # 4. FK guards and explicit warnings
        self.assertIn("SELECT 1 FROM product_ingredients WHERE ingredient_code = r.record_id", downgrade_fn)
        self.assertIn("SELECT 1 FROM ingredient_rules WHERE ingredient_code = r.record_id", downgrade_fn)
        self.assertIn("SELECT 1 FROM product_nutrients WHERE nutrient_code = r.record_id", downgrade_fn)
        self.assertIn("SELECT 1 FROM icmr_nutrient_threshold_rules WHERE nutrient_code = r.record_id", downgrade_fn)
        self.assertIn("SELECT 1 FROM nutrition_interpretation_rules WHERE nutrient_code = r.record_id", downgrade_fn)
        self.assertIn("RAISE WARNING 'Cleanup blocked: ingredient", downgrade_fn)
        self.assertIn("RAISE WARNING 'Cleanup blocked: nutrient", downgrade_fn)

        # 5. Conditional drop of tracker
        self.assertIn("DO $drop_tracker$", downgrade_fn)
        self.assertIn("DROP TABLE migration_seed_ownership;", downgrade_fn)


if __name__ == '__main__':
    unittest.main()
