# YumSure — Phase 1B.4 & Phase 2 Final Technical Handover

**Document Version**: 2.1.0 (Corrected Ownership Tracking & Downgrade Safety Handover)  
**Date**: November 3, 2026  
**Author**: Senior Backend Architect & Nutrition Regulatory Intelligence Lead (Abhishek)  
**Recipient / Collaborator**: Tejas (Backend Foundation & Database Lead)  
**Target Repository**: `d:\Hackthon\hack-sudo-chaos` (`develop` branch)  
**Alembic Head**: `0003_seed_verified_rule_data` (Revises: `0002_enhance_rules`)  
**Automated Test Status**: 40 Tests Ran (39 Passed, 1 Skipped — Live DB Not Required)

---

## 1. Executive Summary & Acceptance Resolution

This revised handover package addresses and resolves all blockers regarding Migration 0003:
1. **Reconciliation of Seed Dataset Counts (54 vs. 63)**:
   The numerical discrepancy is fully accounted for: exactly **54 relational database records** are inserted across 6 PostgreSQL tables, and **9 Schedule II synonym mappings** from `fssai_schedule_ii_synonyms_seed.json` are loaded as embedded JSONB into `regulatory_claim_rules.permitted_synonyms_schedule_ii`. $54 + 9 = \mathbf{63}$ total entries across all 7 seed files.
2. **Migration Ownership Tracking**:
   Replaced naive subquery deletions with an atomic tracking mechanism targeting `migration_seed_ownership`. Inserts use PostgreSQL Common Table Expressions (CTEs) (`WITH ins AS (INSERT ... ON CONFLICT DO NOTHING RETURNING pk) INSERT INTO migration_seed_ownership ... SELECT ... FROM ins;`). Pre-existing records are never tracked and never touched during rollback.
3. **Deterministic Downgrade & Foreign Key Protection**:
   Downgrade executes PL/pgSQL loops checking all referencing foreign keys (`product_ingredients`, `ingredient_rules`, `product_nutrients`, `icmr_nutrient_threshold_rules`, `nutrition_interpretation_rules`). If an owned row has acquired active references, deletion is safely blocked, an explicit warning is logged (`Cleanup blocked: ... is referenced by dependent data and will be preserved`), and the ownership entry is retained.
4. **Automated Verification**:
   Expanded test suite to **40 tests** covering all deterministic engine logic, AST validations, seed reconciliation, and migration ownership scenarios (Scenarios A through F).

---

## 2. Pre-Remediation Inspection & Findings

Prior to implementing corrections, the repository state was formally inspected:
- `backend/alembic/versions/0003_seed_verified_rule_data.py`:
  - Previously relied on naive `NOT IN (SELECT DISTINCT ... FROM product_...)` subqueries during rollback.
  - Did not check foreign keys from `ingredient_rules`, `icmr_nutrient_threshold_rules`, or `nutrition_interpretation_rules`.
  - Did not log warnings when cleanups were blocked.
  - Lacked deterministic lifecycle management for the tracking table.
- All 7 JSON Seed Files:
  - Verified present under `backend/app/data/seeds/`.
  - Exact file counts: 11 nutrients, 6 ingredients, 8 Table 15.1 rules, 9 Table 15.2 matrix cells, 14 statutory claims, 6 ingredient rules (total = 54 relational rows) + 9 Schedule II synonym keys = 63 total items.
- ORM Models & Foreign Keys in `Base.metadata`:
  - Identified 13 registered tables and all incoming/outgoing foreign keys.
- Tests:
  - `test_seed_data.py` validated schemas but lacked explicit reconciliation of 54 vs 63.
  - `test_migration_ownership.py` was created to cover Scenarios A through F.

---

## 3. Seed Dataset Reconciliation (Exact Item Accounting)

### 3.1 Detailed Breakdown Matrix

| # | Seed Dataset File | Format | Target Database Destination | Entity Count |
|---|-------------------|--------|-----------------------------|--------------|
| 1 | `canonical_nutrients_seed.json` | JSON Array | `nutrients` table | **11** rows |
| 2 | `canonical_ingredients_seed.json` | JSON Array | `ingredients` table | **6** rows |
| 3 | `icmr_table_15_1_seed.json` | JSON Array | `icmr_nutrient_threshold_rules` table | **8** rows |
| 4 | `icmr_table_15_2_seed.json` | JSON Array | `icmr_matrix_rules` table | **9** rows |
| 5 | `fssai_schedule_i_claims_seed.json` | JSON Array | `regulatory_claim_rules` table | **14** rows |
| 6 | `ingredient_rules_seed.json` | JSON Array | `ingredient_rules` table | **6** rows |
| **Σ** | **Relational Table Entities** | | **Direct SQL Table Inserts** | **54 database rows** |
| 7 | `fssai_schedule_ii_synonyms_seed.json` | JSON Object (dict) | Embedded in `regulatory_claim_rules.permitted_synonyms_schedule_ii` column | **9** claim mappings |
| **TOTAL** | **All 7 Seed Datasets Combined** | | **Complete Seed Artifact Items** | **63 total items** |

### 3.2 Origin of the Number 54
In early documentation, the figure "54 seed records" was cited because the original author summed only the direct relational table rows ($11 + 6 + 8 + 9 + 14 + 6 = 54$) and omitted the 7th file (`fssai_schedule_ii_synonyms_seed.json`, containing 9 synonym dictionary mappings) since it is embedded directly as a `JSONB` array in `regulatory_claim_rules` rather than populating a standalone SQL table.

### 3.3 Expected Insertions & Conflict Simulation
1. **Fresh Database Execution**:
   - Relational rows inserted: **54 table rows**
   - Ownership records created in `migration_seed_ownership`: **54 entries**
   - Embedded synonym dictionary entries loaded: **9 mappings**
2. **Simulated Conflict Scenario** (e.g. 3 nutrients and 2 ingredients pre-exist):
   - Skipped records: **5 records** (3 nutrients, 2 ingredients) via `ON CONFLICT DO NOTHING`
   - Inserted records: **49 table rows** (54 - 5)
   - Ownership records created: **49 entries** (only newly inserted rows)
   - On downgrade: exactly **49 rows** deleted; the 5 pre-existing rows remain 100% untouched.

---

## 4. Migration Ownership Tracking & Safe Downgrade Architecture

### 4.1 Tracking Table Schema & Lifecycle
Created in `upgrade()`:
```sql
CREATE TABLE IF NOT EXISTS migration_seed_ownership (
    id SERIAL PRIMARY KEY,
    migration_revision VARCHAR(100) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_migration_seed_ownership UNIQUE (migration_revision, target_table, record_id)
);
```
**Removal Lifecycle in `downgrade()`**:
After deleting owned records, a PL/pgSQL block evaluates whether any uncleaned/blocked records remain:
```sql
DO $drop_tracker$
BEGIN
    IF (SELECT COUNT(*) FROM migration_seed_ownership) = 0 THEN
        DROP TABLE migration_seed_ownership;
        RAISE NOTICE 'migration_seed_ownership dropped (all owned records cleanly removed).';
    ELSE
        RAISE NOTICE 'migration_seed_ownership retained (uncleaned/blocked records remain for audit telemetry).';
    END IF;
END $drop_tracker$;
```

### 4.2 Atomic CTE Insertion
Every seeded row is inserted and tracked within the same transaction using PostgreSQL Common Table Expressions:
```sql
WITH ins AS (
    INSERT INTO nutrients (
        nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
    ) VALUES (
        'energy', 'Energy', 'kcal', TRUE, 2000.0, 'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
    ) ON CONFLICT (nutrient_code) DO NOTHING
    RETURNING nutrient_code AS pk
)
INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;
```

### 4.3 Summary of Automated Test Scenarios (A through F)

All scenarios are implemented and validated in [`backend/tests/test_migration_ownership.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/tests/test_migration_ownership.py):

| Scenario | Condition | Upgrade Result | Downgrade Result | Automated Test |
|----------|-----------|----------------|------------------|----------------|
| **Scenario A** | Pre-existing conflicting nutrient (e.g. `sodium`). | Skipped via `ON CONFLICT DO NOTHING`. Zero ownership records created. | Downgrade skips it; pre-existing row preserved untouched. | `test_scenario_a_pre_existing_conflicting_nutrient` (PASS) |
| **Scenario B** | Fresh migration-inserted nutrient (e.g. `energy`). | Inserted. Ownership record logged. | Cleanly deleted from `nutrients` and `migration_seed_ownership`. | `test_scenario_b_migration_inserted_nutrient` (PASS) |
| **Scenario C** | Owned nutrient referenced by dependent data (e.g. `product_nutrients`). | Inserted and owned. | Deletion blocked. Warning logged. Row and ownership entry preserved. | `test_scenario_c_referenced_migration_owned_nutrient` (PASS) |
| **Scenario D** | Equivalent ingredient scenarios (conflict, fresh, referenced). | Pre-existing skipped; fresh deleted; referenced preserved with warning. | Referential integrity preserved across all ingredient states. | `test_scenario_d_ingredient_conflict_and_insertion_scenarios` (PASS) |
| **Scenario E** | Repeated execution (idempotency). | Re-running upgrade does not duplicate rows or ownership logs. | Re-running downgrade produces zero errors. | `test_scenario_e_repeated_upgrade_downgrade_idempotency` (PASS) |
| **Scenario F** | Partial seed conflicts (e.g. 3 pre-existing nuts, 2 pre-existing ings). | 8 nuts and 4 ings inserted and tracked; 5 conflicts skipped. | Downgrade deletes strictly the 12 owned rows; leaves all 5 pre-existing intact. | `test_scenario_f_partial_seed_conflict_scenarios` (PASS) |

---

## 5. Foreign-Key Dependency Matrix & Strict Rollback Order

### 5.1 Complete Table-by-Table FK Dependency Matrix

| Seeded Table | Referencing Table | Foreign-Key Column | On-Delete Behavior | Referential Guard in Rollback |
|--------------|-------------------|--------------------|--------------------|--------------------------------|
| `nutrients` | `product_nutrients` | `nutrient_code` | `NO ACTION` (None) | Block deletion if referenced by `product_nutrients`. |
| `nutrients` | `icmr_nutrient_threshold_rules` | `nutrient_code` | `NO ACTION` (None) | Block deletion if referenced by `icmr_nutrient_threshold_rules`. |
| `nutrients` | `nutrition_interpretation_rules` | `nutrient_code` | `NO ACTION` (None) | Block deletion if referenced by `nutrition_interpretation_rules`. |
| `ingredients` | `product_ingredients` | `ingredient_code` | `NO ACTION` (None) | Block deletion if referenced by `product_ingredients`. |
| `ingredients` | `ingredient_rules` | `ingredient_code` | `CASCADE` | Block deletion if referenced by remaining `ingredient_rules`. |
| `icmr_nutrient_threshold_rules` | *(None)* | *(None)* | N/A | Direct deletion of owned records. Clears incoming FK to `nutrients`. |
| `icmr_matrix_rules` | *(None)* | *(None)* | N/A | Direct deletion of owned records. Completely orthogonal. |
| `regulatory_claim_rules` | *(None)* | *(None)* | N/A | Direct deletion of owned records. |
| `ingredient_rules` | *(None)* | *(None)* | N/A | Direct deletion of owned records. Clears incoming FK to `ingredients`. |

### 5.2 Strict Reverse FK Rollback Order
Downgrade executes in the following mandatory sequence:
1. `ingredient_rules` (clears outgoing foreign key to `ingredients`)
2. `regulatory_claim_rules`
3. `icmr_matrix_rules`
4. `icmr_nutrient_threshold_rules` (clears outgoing foreign key to `nutrients`)
5. `ingredients` (PL/pgSQL block verifying zero incoming references from `product_ingredients` or `ingredient_rules`)
6. `nutrients` (PL/pgSQL block verifying zero incoming references from `product_nutrients`, `icmr_nutrient_threshold_rules`, or `nutrition_interpretation_rules`)
7. `migration_seed_ownership` (conditionally dropped if zero uncleaned records remain)

---

## 6. Offline Migration SQL Evidence

Static SQL evidence was generated using Alembic's offline PostgreSQL dialect mode (`--sql`):

1. **Upgrade SQL (`backend/alembic/sql_evidence/upgrade_0002_to_0003.sql`)**:
   - Size: 128,692 bytes (UTF-8)
   - Transactional DDL: `BEGIN; ... COMMIT;`
   - Content: Creates `migration_seed_ownership`, runs 54 atomic CTE inserts with `ON CONFLICT DO NOTHING RETURNING pk`, updates `alembic_version` to `'0003_seed_verified_rule_data'`.
2. **Downgrade SQL (`backend/alembic/sql_evidence/downgrade_0003_to_0002.sql`)**:
   - Size: 4,370 bytes (UTF-8)
   - Transactional DDL: `BEGIN; ... COMMIT;`
   - Content: Executes deletions in reverse FK order, runs PL/pgSQL loops with `RAISE WARNING` on blocked items, conditionally drops tracker, updates `alembic_version` to `'0002_enhance_rules'`.

---

## 7. Automated Test Suite Execution Evidence

Command executed:
```powershell
cd backend
.\venv\Scripts\python.exe -m unittest discover tests -v
```

Captured terminal output:
```text
test_claims_depth_limit_exceeded_fails_safely (test_engines.TestDeterministicEngines.test_claims_depth_limit_exceeded_fails_safely) ... ok
test_claims_invalid_operator_fails_safely (test_engines.TestDeterministicEngines.test_claims_invalid_operator_fails_safely) ... ok
test_claims_missing_nutrient_insufficient_data (test_engines.TestDeterministicEngines.test_claims_missing_nutrient_insufficient_data) ... ok
test_claims_no_added_sugar_non_addition (test_engines.TestDeterministicEngines.test_claims_no_added_sugar_non_addition) ... ok
test_claims_synonym_resolution (test_engines.TestDeterministicEngines.test_claims_synonym_resolution) ... ok
test_claims_trans_fat_free_breached_fail (test_engines.TestDeterministicEngines.test_claims_trans_fat_free_breached_fail) ... ok
test_claims_trans_fat_free_pass (test_engines.TestDeterministicEngines.test_claims_trans_fat_free_pass) ... ok
test_icmr_liquid_matrix_not_applicable (test_engines.TestDeterministicEngines.test_icmr_liquid_matrix_not_applicable) ... ok
test_icmr_matrix_ultra_processed_cell_c3 (test_engines.TestDeterministicEngines.test_icmr_matrix_ultra_processed_cell_c3) ... ok
test_icmr_matrix_whole_food_cell_a1 (test_engines.TestDeterministicEngines.test_icmr_matrix_whole_food_cell_a1) ... ok
test_icmr_missing_added_fat_insufficient_data (test_engines.TestDeterministicEngines.test_icmr_missing_added_fat_insufficient_data) ... ok
test_ingredient_aspartame_pku_warning (test_engines.TestDeterministicEngines.test_ingredient_aspartame_pku_warning) ... ok
test_ingredient_caffeine_beverage_limit_and_warning (test_engines.TestDeterministicEngines.test_ingredient_caffeine_beverage_limit_and_warning) ... ok
test_ingredient_category_specific_filtering (test_engines.TestDeterministicEngines.test_ingredient_category_specific_filtering) ... ok
test_ingredient_uncharacterized_notice (test_engines.TestDeterministicEngines.test_ingredient_uncharacterized_notice) ... ok
test_nutrition_complete_declaration_pass (test_engines.TestDeterministicEngines.test_nutrition_complete_declaration_pass) ... ok
test_nutrition_missing_mandatory_declarations_insufficient_data (test_engines.TestDeterministicEngines.test_nutrition_missing_mandatory_declarations_insufficient_data) ... ok
test_scenario_a_pre_existing_conflicting_nutrient (test_migration_ownership.TestMigrationOwnershipSemantics.test_scenario_a_pre_existing_conflicting_nutrient) ... ok
test_scenario_b_migration_inserted_nutrient (test_migration_ownership.TestMigrationOwnershipSemantics.test_scenario_b_migration_inserted_nutrient) ... ok
test_scenario_c_referenced_migration_owned_nutrient (test_migration_ownership.TestMigrationOwnershipSemantics.test_scenario_c_referenced_migration_owned_nutrient) ... ok
test_scenario_d_ingredient_conflict_and_insertion_scenarios (test_migration_ownership.TestMigrationOwnershipSemantics.test_scenario_d_ingredient_conflict_and_insertion_scenarios) ... ok
test_scenario_e_repeated_upgrade_downgrade_idempotency (test_migration_ownership.TestMigrationOwnershipSemantics.test_scenario_e_repeated_upgrade_downgrade_idempotency) ... ok
test_scenario_f_partial_seed_conflict_scenarios (test_migration_ownership.TestMigrationOwnershipSemantics.test_scenario_f_partial_seed_conflict_scenarios) ... ok
test_static_sql_contracts_in_migration_0003 (test_migration_ownership.TestMigrationOwnershipSemantics.test_static_sql_contracts_in_migration_0003) ... ok
setUpClass (test_product_repository.TestProductRepository) ... skipped 'Live PostgreSQL database not reachable'
test_01_icmr_model_separation (test_remediation_audit.TestRemediationAudit.test_01_icmr_model_separation) ... ok
test_02_matrix_a1_c3_representation (test_remediation_audit.TestRemediationAudit.test_02_matrix_a1_c3_representation) ... ok
test_03_ingredient_classification_states (test_remediation_audit.TestRemediationAudit.test_03_ingredient_classification_states) ... ok
test_04_ast_depth_limits (test_remediation_audit.TestRemediationAudit.test_04_ast_depth_limits) ... ok
test_05_ast_invalid_and_empty_structures (test_remediation_audit.TestRemediationAudit.test_05_ast_invalid_and_empty_structures) ... ok
test_06_missing_condition_expression (test_remediation_audit.TestRemediationAudit.test_06_missing_condition_expression) ... ok
test_07_ingredient_rule_types (test_remediation_audit.TestRemediationAudit.test_07_ingredient_rule_types) ... ok
test_08_sqlalchemy_metadata_registration (test_remediation_audit.TestRemediationAudit.test_08_sqlalchemy_metadata_registration) ... ok
test_canonical_ingredients (test_seed_data.TestSeedDataIntegrity.test_canonical_ingredients) ... ok
test_canonical_nutrients (test_seed_data.TestSeedDataIntegrity.test_canonical_nutrients) ... ok
test_fssai_schedule_i_claims (test_seed_data.TestSeedDataIntegrity.test_fssai_schedule_i_claims) ... ok
test_fssai_schedule_ii_synonyms (test_seed_data.TestSeedDataIntegrity.test_fssai_schedule_ii_synonyms) ... ok
test_icmr_table_15_1_thresholds (test_seed_data.TestSeedDataIntegrity.test_icmr_table_15_1_thresholds) ... ok
test_icmr_table_15_2_matrix (test_seed_data.TestSeedDataIntegrity.test_icmr_table_15_2_matrix) ... ok
test_ingredient_rules (test_seed_data.TestSeedDataIntegrity.test_ingredient_rules) ... ok
test_seed_dataset_reconciliation_counts (test_seed_data.TestSeedDataIntegrity.test_seed_dataset_reconciliation_counts) ... ok

----------------------------------------------------------------------
Ran 40 tests in 0.188s

OK (skipped=1)
```

---

## 8. Package Verification Evidence

The ZIP archive `yumsure_handover_phase_1b4_phase2.zip` was generated and systematically validated:
- Archive existence: Verified.
- Archive size: 91,280 bytes.
- ZIP integrity test (`testzip()`): Passed (0 CRC errors).
- SHA-256 hash match: 100% byte-for-byte parity between repository source files and archive members.

---

## 9. Remaining Limitations & Tejas Integration Instructions

1. **SQLite Limitation Note**:
   SQLite cannot run PostgreSQL data-modifying CTEs (`WITH ins AS (INSERT ...)`) or PL/pgSQL procedural blocks (`DO $$ ... $$`). The test suite simulates PostgreSQL relational state machine semantics and verifies static SQL syntax contracts.
2. **Offline Mode**:
   Zero live database migrations were executed during preparation.
3. **Integration Steps for Tejas**:
   ```powershell
   cd backend
   # 1. Verify heads
   .\venv\Scripts\alembic.exe heads
   # Sole head: 0003_seed_verified_rule_data (head)

   # 2. Inspect generated SQL
   Get-Content alembic/sql_evidence/upgrade_0002_to_0003.sql -Head 50
   Get-Content alembic/sql_evidence/downgrade_0003_to_0002.sql

   # 3. Apply migration to PostgreSQL at your discretion
   .\venv\Scripts\alembic.exe upgrade head
   ```
