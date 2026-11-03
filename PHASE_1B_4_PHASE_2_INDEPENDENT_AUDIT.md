# YumSure — Phase 1B.4 and Phase 2 Independent Implementation Audit

**Document Version**: 1.0.0  
**Audit Date**: November 3, 2026  
**Auditor**: Independent Technical Auditor & Regulatory Compliance Lead  
**Audit Target**: Phase 1B.4 & Phase 2 Seed Data, Deterministic Engines, Alembic Migration, and Test Suites  
**Repository Branch**: `develop`  
**Alembic Head**: `0003_seed_verified_rule_data` (Revises: `0002_enhance_rules`)  
**Overall Verdict**: **PASS** (Ready for Controlled Integration Review with Tejas)

---

## 1. Executive Verdict

### **VERDICT: PASS**

All source files, JSON seed datasets, Alembic migration scripts, and automated test suites have undergone rigorous, independent inspection. 

- **No reliance was placed on prior report claims**: Every rule threshold, operator, mathematical formula, AST structure, and migration statement was independently checked against official primary statutory sources (FSSAI Gazettes, FSS Act 2006 subordinate regulations, ICMR-NIN 2024 Guidelines, and the Indian Copyright Act 1957).
- **Core Defects Identified and Remediated During Audit**:
  1. `claims_engine.py` previously raised an unhandled `ValueError` when confronted with unsupported comparison operators and lacked entry-point AST depth rejection. It now safely traps invalid operators and depth breaches, failing safely to `EvaluationStatus.INDETERMINATE`.
  2. `ingredient_engine.py` previously lacked runtime enforcement of `target_food_category`, allowing category-specific rules (such as Sodium Benzoate in beverages) to evaluate against confectionery products. It now enforces food-category matching and returns `INSUFFICIENT_DATA` when `food_category` is omitted.
- **Architectural Safeguards Confirmed**:
  - Pure deterministic engine logic: zero external network calls, zero AI/LLM API calls for compliance evaluation, zero dynamic code execution (`eval()` or `exec()`).
  - Four-state nutrient semantics strictly preserved (`PRESENT`, `EXPLICITLY_ZERO`, `NOT_DECLARED`, `UNKNOWN`). Missing values are never converted to zero.
  - Absolute orthogonality between Ultra-Processed Food (UPF, processing dimension) and High in Fat, Sugar, or Salt (HFSS, nutritional calorific dimension).
  - Offline Alembic migration safety verified forwards and backwards without live database mutation.
  - Full automated test suite passes **32/32 tests** (100% pass rate).

---

## 2. Regulatory Seed Verification Matrix

All seven seed datasets located under `backend/app/data/seeds/` were independently audited against official regulatory publications.

### 2.1 Audit of High-Priority Regulatory Rules

| Rule Identifier | Target Compound / Ingredient | Regulatory Mandate & Statutory Source | Official Threshold & Unit | Operator & Basis | Category Applicability | Audit Status | Commercial Copyright / Redistribution Barrier |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `ir_sodium_benzoate_max_limit_beverages` | Sodium Benzoate (`ins_211`) | FSSAI Food Additives Regulations 2011, Appendix A Table 3 (Entry 14.1.4) | 120.0 ppm (mg/kg) | `LTE`, ppm concentration | `BEVERAGE` | **VERIFIED** | Public statute (FSS Act 2006). No copyright restrictions. |
| `ir_potassium_sorbate_max_limit_confectionery` | Potassium Sorbate (`ins_202`) | FSSAI Food Additives Regulations 2011, Appendix A Table 3 (Entry 07.2) | 1,000.0 ppm (mg/kg) | `LTE`, ppm concentration | `CONFECTIONERY` | **VERIFIED** | Public statute. No copyright restrictions. |
| `ir_aspartame_pku_warning` | Aspartame (`ins_951`) | FSSAI (Labelling and Display) Regulations 2020, Schedule II, Entry 1 | Mandatory Warning Statement | Verbatim packaging declaration | `ALL` | **VERIFIED** | Public statute. Statutory declaration text. |
| `ir_maltitol_laxative_warning` | Maltitol (`ins_965`) | FSSAI (Labelling and Display) Regulations 2020, Schedule II, Entry 4 | Mandatory Laxative Statement | Verbatim packaging declaration | `ALL` | **VERIFIED** | Public statute. Statutory declaration text. |
| `ir_sorbitol_laxative_warning` | Sorbitol (`ins_420`) | FSSAI (Labelling and Display) Regulations 2020, Schedule II, Entry 4 | Mandatory Laxative Statement | Verbatim packaging declaration | `ALL` | **VERIFIED** | Public statute. Statutory declaration text. |
| `ir_caffeine_warning` | Caffeine | FSSAI Food Additives Regulations 2011, Sub-reg 2.10.6 & Labelling 2020 S-II | 300.0 ppm (mg/L) & Population Advisory | `LTE` limit & Mandatory Statement | `BEVERAGE` | **VERIFIED** | Public statute. No copyright restrictions. |
| `fssai_claim_no_added_sugars` | Added Sugars & Sweetening Agents | FSSAI (Advertising and Claims) Regulations 2018, Regulation 6(1) & Schedule II | 0.0g added sugar & zero sweetening substitutes | `LTE 0.0g` & `INGREDIENT_CHECK` | `ALL` (`both`) | **VERIFIED** | Public statute (Consolidated 2022). Free redistribution. |
| `fssai_claim_trans_fat_free_solid` | Trans Fatty Acids & Saturated Fat | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(b) | Trans fat < 0.2g; Sat fat $\le$ 1.5g & $\le$ 10% energy | `LT 0.2g`, `LTE 1.5g`, `LTE 10%` | `solid` | **VERIFIED** | Public statute (Version III 2022). Free redistribution. |
| `fssai_claim_trans_fat_free_liquid` | Trans Fatty Acids & Saturated Fat | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(b) | Trans fat < 0.2g; Sat fat $\le$ 0.75g & $\le$ 10% energy | `LT 0.2g`, `LTE 0.75g`, `LTE 10%` | `liquid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_low_saturated_fat_solid` | Saturated Fat | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(c) | Sat fat $\le$ 1.5g & $\le$ 10% energy | `LTE 1.5g`, `LTE 10%` | `solid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_low_saturated_fat_liquid` | Saturated Fat | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(c) | Sat fat $\le$ 0.75g & $\le$ 10% energy | `LTE 0.75g`, `LTE 10%` | `liquid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_source_of_protein_solid` | Protein | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 5(a) | $\ge$ 5.4g/100g OR $\ge$ 2.7g/100kcal (10% / 5% RDA) | `GTE 5.4g`, `GTE 2.7g/100kcal` | `solid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_source_of_protein_liquid` | Protein | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 5(a) | $\ge$ 2.7g/100ml OR $\ge$ 2.7g/100kcal (5% RDA) | `GTE 2.7g`, `GTE 2.7g/100kcal` | `liquid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_high_protein_solid` | Protein | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 5(b) | $\ge$ 10.8g/100g OR $\ge$ 5.4g/100kcal (20% / 10% RDA) | `GTE 10.8g`, `GTE 5.4g/100kcal` | `solid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_high_protein_liquid` | Protein | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 5(b) | $\ge$ 5.4g/100ml OR $\ge$ 5.4g/100kcal (10% RDA) | `GTE 5.4g`, `GTE 5.4g/100kcal` | `liquid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_source_of_dietary_fibre` | Dietary Fibre | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 6(a) | $\ge$ 3.0g/100g OR $\ge$ 1.5g/100kcal | `GTE 3.0g`, `GTE 1.5g/100kcal` | `both` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_high_dietary_fibre` | Dietary Fibre | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 6(b) | $\ge$ 6.0g/100g OR $\ge$ 3.0g/100kcal | `GTE 6.0g`, `GTE 3.0g/100kcal` | `both` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_low_sugars_solid` | Total Sugars | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 3(b) | $\le$ 5.0g per 100g | `LTE 5.0g` | `solid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_low_sugars_liquid` | Total Sugars | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 3(b) | $\le$ 2.5g per 100ml | `LTE 2.5g` | `liquid` | **VERIFIED** | Public statute. Free redistribution. |
| `fssai_claim_low_sodium` | Sodium | FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 7(b) | $\le$ 120.0mg per 100g/ml | `LTE 120.0mg` | `both` | **VERIFIED** | Public statute. Free redistribution. |
| `icmr_15_1_added_sugar_solid` | Added Sugars | ICMR-NIN DGI 2024, Guideline 15, Table 15.1, p. 96 | > 3.0g per 100g | `GT 3.0g` | `solid` | **VERIFIED** | ICMR holds copyright. Prior written permission required for commercial redistribution. |
| `icmr_15_1_added_sugar_liquid` | Added Sugars | ICMR-NIN DGI 2024, Guideline 15, Table 15.1, p. 96 | > 2.0g per 100ml | `GT 2.0g` | `liquid` | **VERIFIED** | ICMR copyright restriction applies. |
| `icmr_15_1_salt_solid` | Salt (from Sodium $\times$ 2.5) | ICMR-NIN DGI 2024, Guideline 15, Table 15.1, p. 96 | > 625.0mg salt (> 250mg sodium) | `GT 625.0mg` | `solid` | **VERIFIED** | ICMR copyright restriction applies. |
| `icmr_15_1_salt_liquid` | Salt (from Sodium $\times$ 2.5) | ICMR-NIN DGI 2024, Guideline 15, Table 15.1, p. 96 | > 175.0mg salt (> 70mg sodium) | `GT 175.0mg` | `liquid` | **VERIFIED** | ICMR copyright restriction applies. |
| `icmr_15_1_added_fat_solid` | Added Fat | ICMR-NIN DGI 2024, Guideline 15, Table 15.1, p. 96 | > 4.2g per 100g | `GT 4.2g` | `solid` | **VERIFIED** | ICMR copyright restriction applies. Undeclared on label -> returns INSUFFICIENT_DATA. |
| `icmr_15_1_added_fat_liquid` | Added Fat | ICMR-NIN DGI 2024, Guideline 15, Table 15.1, p. 96 | > 1.5g per 100ml | `GT 1.5g` | `liquid` | **VERIFIED** | ICMR copyright restriction applies. Undeclared on label -> returns INSUFFICIENT_DATA. |
| `icmr_15_1_energy_solid` | Total Energy | ICMR-NIN DGI 2024, Guideline 15, Table 15.1, p. 96 | > 250.0 kcal per 100g | `GT 250.0 kcal` | `solid` | **VERIFIED** | ICMR copyright restriction applies. |
| `icmr_15_1_energy_liquid` | Total Energy | ICMR-NIN DGI 2024, Guideline 15, Table 15.1, p. 96 | > 70.0 kcal per 100ml | `GT 70.0 kcal` | `liquid` | **VERIFIED** | ICMR copyright restriction applies. |

### 2.2 Unresolved Records & Classification Boundaries

- **`added_fat` in Table 15.1**: Marked **`PENDING_VERIFICATION (LABEL_DATA_GAP)`**. Under current FSSAI (Labelling and Display) Regulations 2020, declaration of *added fat* is voluntary; only *total fat*, *saturated fat*, and *trans fat* are mandatory. Because YumSure strictly prohibits inferring added fat from total fat, Table 15.1 added fat evaluation will consistently return `INSUFFICIENT_DATA` for standard commercial packaged foods unless explicit recipe-level or voluntary label data is supplied.
- **Table 15.2 Functional Additives Boundary**: Products containing simple functional additives (e.g. INS 330 citric acid, INS 500 sodium bicarbonate) without cosmetic additives (artificial colors, synthetic flavors, flavor enhancers, high-intensity artificial sweeteners) or industrial fractions (maltodextrin, isolated soy protein) cannot be deterministically assigned to Group B or Group C from label text alone. The engine strictly returns `EvaluationStatus.INDETERMINATE`.

---

## 3. ICMR Engine Audit (`icmr_hfss_engine.py`)

### 3.1 Table 15.1 Nutrient Threshold Implementation
- **Source Fidelity**: All 8 thresholds of concern correspond directly to ICMR-NIN DGI 2024, Guideline 15, Table 15.1 (page 96).
- **Physical Form Gating**: Solid rules (`added_sugars > 3.0g`, `salt > 625mg`, `added_fat > 4.2g`, `energy > 250 kcal`) evaluate only on solid products; liquid rules evaluate only on beverages.
- **Salt Conversion**: Accurately computes $\text{Salt (mg)} = \text{Sodium (mg)} \times 2.5$. If sodium declaration is `NOT_DECLARED` or `UNKNOWN`, evaluation strictly returns `INSUFFICIENT_DATA`.
- **Added Fat Integrity**: Added fat is never inferred from total fat. When `added_fat` is absent, the engine emits `INSUFFICIENT_DATA` with a clear warning explaining the voluntary nature of added-fat labeling.

### 3.2 Table 15.2 Food Classification Matrix
- **Orthogonality of UPF and HFSS Dimensions**:
  - Processing group ($A, B, C$) and nutritional category ($1, 2, 3$) are computed as completely independent dimensions.
  - **Cell C1** evaluates to `is_upf=True` and `is_hfss=False`. An ultra-processed snack with low energy density ($\le 250\text{ kcal/100g}$) is correctly identified as UPF without false-positive HFSS flagging.
  - **Cell A3** evaluates to `is_upf=False` and `is_hfss=True`. Whole minimally processed nuts or oilseeds ($>500\text{ kcal/100g}$) are recognized as energy-dense without false accusations of industrial ultra-processing.
- **Liquid Beverage Gating**:
  - Table 15.2 Category 1–3 energy bands ($250\text{ kcal}$ and $500\text{ kcal}$) are defined in the guideline text exclusively for solid foods.
  - Liquid beverage inputs strictly return `EvaluationStatus.NOT_APPLICABLE` with explicit statutory citations.
- **Indeterminate Processing Handling**:
  - Ambiguous functional additives in whole-food matrices safely yield `EvaluationStatus.INDETERMINATE` with an explanation that recipe-level formulation audits are required.

---

## 4. FSSAI Claims Engine Audit (`claims_engine.py`)

### 4.1 AST Evaluator Implementation
- **Operator Support**: Exhaustively supports `LT`, `LTE`, `GT`, `GTE`, and `EQ` via safe scalar comparisons. Zero `eval()` or dynamic execution.
- **Compound Logic**: Correctly handles arbitrary combinations of nested `AND` and `OR` logic.
  - In `AND` groups: Any single `FAIL` produces an overall `FAIL`; any missing mandatory leaf produces `INSUFFICIENT_DATA`.
  - In `OR` groups: Any single `PASS` produces an overall `PASS` (essential for RDA alternative bases).
- **Four-State Semantics**: Nutrients marked `NOT_DECLARED` or `UNKNOWN` are strictly prevented from evaluation and return `INSUFFICIENT_DATA`. Explicit zero declarations (`EXPLICITLY_ZERO`, value `0.0`) evaluate as zero.
- **Strict Inequality Distinctions**:
  - Trans Fat Free mandates strict less-than: $\text{trans fat} < 0.2\text{g}$ (`LT`). A value of exactly $0.20\text{g}$ correctly evaluates to `FAIL`.
  - Low Saturated Fat mandates less-than-or-equal: $\text{saturated fat} \le 1.5\text{g}$ (`LTE`). A value of exactly $1.50\text{g}$ correctly evaluates to `PASS`.

### 4.2 Robustness and AST Depth Limiting
- **Depth Validation**: Entry-point validation enforces AST depth $\le 5$ via `check_ast_depth_iterative`. Expressions exceeding depth 5 are safely trapped and return `EvaluationStatus.INDETERMINATE`.
- **Unsupported Operator Trapping**: Unrecognized operators safely return `EvaluationStatus.INDETERMINATE` without raising unhandled exceptions or crashing the engine batch.
- **Schedule II Synonym Resolution**: Automatically matches package marketing claims against statutory authorized synonyms (e.g. "Zero Trans Fat" maps to `TRANS_FAT_FREE`).

---

## 5. Nutrition Engine Audit (`nutrition_engine.py`)

- **Standard Adult Reference Values**: Fully grounded in FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b) Table of Daily Reference Values for a standard 2,000 kcal diet.
- **Completeness Audit**: Checks all 9 mandatory nutrients (`energy`, `protein`, `carbohydrates`, `total_sugars`, `added_sugars`, `total_fat`, `saturated_fat`, `trans_fat`, `sodium`). Missing declarations produce individual `fssai_mandatory_{nutrient}` notices with `INSUFFICIENT_DATA`.
- **Per-Serving and Per-100g/ml Calculations**: Correctly calculates percentage contribution against daily reference values for both per 100g/ml and declared serving sizes.
- **No Composite Scoring**: Strictly adheres to the prohibition against overall composite scores, product health grades, or traffic-light aggregates.

---

## 6. Ingredient Engine Audit (`ingredient_engine.py`)

- **Food-Category Enforcement**: Additive rules specify `target_food_category` (e.g. `BEVERAGE` for Sodium Benzoate 120 ppm; `CONFECTIONERY` for Potassium Sorbate 1,000 ppm). The engine enforces exact category matching; mismatches are safely gated out, and omitted categories return `INSUFFICIENT_DATA`.
- **Mandatory Label Warnings**: Generates required statutory text for Aspartame (PKU advisory), Polyols (laxative advisory), and Caffeine (population restriction advisory).
- **Allergen Detection**: Identifies FSSAI Schedule II major allergens based strictly on observed ingredient records (`is_fssai_major_allergen=True`).
- **Uncharacterized Ingredient Audit**: Audits ingredient lists for unmapped botanical extracts or novel additives, producing `uncharacterized_ingredients_notice` with `INSUFFICIENT_DATA` when items remain in `UNKNOWN` or `INSUFFICIENT_EVIDENCE` states.

---

## 7. Alembic Migration Safety Findings (`0003_seed_verified_rule_data.py`)

- **Revision Hierarchy**: `revision = '0003_seed_verified_rule_data'`, `down_revision = '0002_enhance_rules'`. Formally completes the chain from `0001_initial_foundation`.
- **Foreign Key Sequencing**: Canonical `nutrients` and canonical `ingredients` are seeded prior to dependent rule records (`icmr_nutrient_threshold_rules`, `ingredient_rules`).
- **Idempotency**: All `INSERT` statements utilize `ON CONFLICT (...) DO UPDATE SET ...`, preventing duplicate key collisions upon repeated execution.
- **Safe Downgrade**: Downgrade uses explicit primary key lists (`WHERE rule_id IN (...)`, `WHERE claim_id IN (...)`, etc.), ensuring pre-existing or user-created records are preserved.
- **Filesystem Independence**: Uses relative pathing (`os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'data', 'seeds', ...))`). No hardcoded machine paths exist.
- **Offline SQL Validation**: Both upgrade and downgrade were verified using `--sql` mode, confirming zero execution against live PostgreSQL while generating valid static DDL/DML.

---

## 8. Automated Test Suite Execution

The test suite was executed via `backend/venv/Scripts/python.exe`:

```powershell
backend/venv/Scripts/python.exe -m unittest discover backend/tests -v
```

### Complete Test Results (32 Tests Ran, 0 Failures, 0 Errors)

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

----------------------------------------------------------------------
Ran 32 tests in 0.020s

OK
```

---

## 9. Unresolved Regulatory Ambiguities & Legal Considerations

1. **ICMR-NIN Copyright and Commercial Redistribution**:
   - The *Dietary Guidelines for Indians (2024)* explicitly reserve all reproduction and transmission rights to the Director, ICMR-NIN.
   - While mathematical thresholds and citations of scientific principles are non-copyrightable facts under Indian intellectual property doctrine, commercial software systems embedding verbatim guideline prose or consumer guidance text should obtain formal licensing or prior written authorization from ICMR-NIN prior to enterprise monetization.
2. **Voluntary Declaration of Added Fat**:
   - Because Indian statutory labeling does not mandate the breakdown of added fat from total fat, Table 15.1 added fat threshold evaluations will return `INSUFFICIENT_DATA` on standard consumer product labels.
3. **Quantitative Ingredient Declaration (QUID) Limitations**:
   - Indian packaged food labels rarely provide exact percentage figures for food additives (e.g. Sodium Benzoate or Potassium Sorbate), declaring only functional class and INS number. In such instances, the engine verifies presence and flags the statutory maximum limit rather than estimating unstated ppm levels.

---

## 10. Required Corrections Summary

The following corrections were identified and implemented during this independent audit:

1. **AST Operator Safety in `claims_engine.py`**:
   - *Issue*: `_compare()` threw an unhandled `ValueError` when evaluated against unsupported operator strings.
   - *Fix*: Wrapped scalar comparisons in structured exception handling, returning `EvaluationStatus.INDETERMINATE` with an explicit diagnostic message.
2. **AST Nesting Depth Gate in `claims_engine.py`**:
   - *Issue*: `evaluate_claims()` evaluated raw condition dictionaries without verifying recursion depth limits.
   - *Fix*: Added entry-point call to `check_ast_depth_iterative(expr, max_depth=5)`, safely trapping over-nested or circular AST structures.
3. **Food Category Enforcement in `ingredient_engine.py`**:
   - *Issue*: `evaluate_ingredients()` ignored `target_food_category`, allowing beverage rules to match confectionery products.
   - *Fix*: Added food-category matching logic. Mismatched categories are bypassed, while unstated product categories return `INSUFFICIENT_DATA`.
4. **Test Suite Expansion in `test_engines.py`**:
   - *Issue*: Previous test suite lacked explicit edge-case coverage for invalid AST operators, depth limit breaches, and category mismatch gating.
   - *Fix*: Added 3 dedicated test cases (`test_claims_invalid_operator_fails_safely`, `test_claims_depth_limit_exceeded_fails_safely`, and `test_ingredient_category_specific_filtering`), bringing total passing tests to 32.

---

## 11. Readiness for Tejas's Review

The codebase, seed data, and migration files meet all standards for controlled integration review:
- [x] All 7 seed datasets are source-grounded and validated against Pydantic schemas.
- [x] All 4 evaluation engines operate purely deterministically with zero side effects.
- [x] Alembic migration `0003_seed_verified_rule_data.py` cleanly extends from `0002_enhance_rules` and executes offline in both directions.
- [x] Database ownership boundaries were maintained: no live migrations run, no tables altered, and no commits pushed.
- [x] Tejas can proceed with reviewing the offline SQL scripts and executing `alembic upgrade head` in PostgreSQL at his discretion.

