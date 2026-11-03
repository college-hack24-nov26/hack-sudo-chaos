# YumSure — Complete Technical Work Handover for Tejas

**Author:** Abhishek Mahadik (Senior Nutrition & Regulatory Intelligence Lead, Database Architect)  
**Recipient:** Tejas (Backend & API Lead, YumSure Core Architect)  
**Date:** 3 November 2026  
**Document Version:** 1.0.0 (Phase 1B.3 Post-Remediation Baseline)  
**Associated Commit:** `bf3dab8` (*"Nutrition Report Analyasis"*) on branch `develop`  
**Audit Baseline:** Remediated against `PHASE_1B_3_INDEPENDENT_AUDIT.md` (Verdict: **PASS**)  

---

## 1. Executive Summary

This handover document provides a complete, evidence-backed accounting of all research, regulatory modeling, database architecture design, and Phase 1B.3 implementation completed by Abhishek for YumSure.

All work described herein is backed by concrete files, tests, and Git commits present in the workspace. In response to the independent audit findings (`DEF-01` through `DEF-06`), the schema has been enhanced, validated against PostgreSQL 18 dialect requirements, verified via an 8-case automated test suite (`backend/tests/test_remediation_audit.py`), and confirmed with clean offline migration generation (`0001_initial_foundation` $\rightarrow$ `0002_enhance_rules_and_ingredients`).

### High-Level Status:
- **Research & Regulatory Specifications**: 100% Completed & Formally Registered.
- **SQLAlchemy 2.0 Extended Models**: 100% Implemented & Verified in `Base.metadata`.
- **AST Security & Validation Schema**: 100% Implemented (No `eval`/`exec`, depth $\le 5$).
- **Alembic Migration Scripts**: 100% Generated & Tested via Offline SQL generation.
- **Automated Remediation Audit**: 8/8 Tests Passing (`test_remediation_audit.py`).
- **Live Database Migrations**: **PENDING / BLOCKED** awaiting PostgreSQL service startup and Tejas's final execution approval.

---

## 2. Responsibilities and Contributions

| Area of Ownership | Contributor | Scope of Responsibility |
|---|---|---|
| **Research & Regulatory Intelligence** | Abhishek | FSSAI claims regulations (2018/2022), ICMR-NIN Dietary Guidelines (2024), WHO SEARO NPM scope, nutrient reference values, evidence hierarchy, and provenance auditing. |
| **Rule & AST Architecture** | Abhishek | Compound rule expression tree, AST schema, depth limiting, processing classification, sugar taxonomy, and 5-state evaluation protocol (`PASS`, `FAIL`, `INSUFFICIENT_DATA`, `INDETERMINATE`, `NOT_APPLICABLE`). |
| **Phase 1B.3 Models & Migrations** | Abhishek | Authored `claim_ast_schema.py`, `icmr_threshold_rule.py`, `icmr_matrix_rule.py`, updated `ingredient.py`, `ingredient_rule.py`, `regulatory_claim_rule.py`, and migration `0002_enhance_rules_and_ingredients.py`. |
| **Backend Core & API Infrastructure** | Tejas | FastAPI framework, `app.core.config.Settings`, SQLAlchemy synchronous engine, connection pooling (`pool_pre_ping=True`), session lifecycle (`get_db()`), and baseline Phase 1A foundation. |
| **Mobile Client Application** | Ubaid | Flutter Android application, camera barcode scanning, nutrition card views, and claims badges. |

---

## 3. Research Completed

All regulatory thresholds and classifications in YumSure are derived directly from primary statutory gazettes and institutional clinical standards. No thresholds are arbitrary.

### 3.1 Primary Research Documents Produced
1. **`NUTRIENT_REFERENCE_AUDIT.md` (v3.0.0)**:
   - Compares ICMR-NIN 2020 RDA (biological nutrition average for sedentary adult man/woman) against FSSAI 2020 Schedule II (mandatory consumer packaging reference standard: 2,000 kcal diet, 54g protein, 67g total fat, 22g saturated fat, 2g trans fat, 50g added sugars, 2,000mg sodium, 30g dietary fibre).
   - Establishes that **FSSAI Daily Reference Values** must govern consumer labelling percentage calculations on packaging, not biological RDA variations.
2. **`NUTRIENT_CLASSIFICATION_RESEARCH.md` (v4.0.0)**:
   - Audits FSSAI (Advertising and Claims) Regulations 2018 (Consolidated 2022).
   - Resolves the statutory distinction between **Schedule I** (quantitative claim conditions: thresholds, operators, secondary caloric percentage caps) and **Schedule II** (permitted synonyms: e.g., "Zero", "No", "Negligible" for "Free"; "Provides", "Contains" for "Source").
   - Details multi-base alternatives: Energy basis (`g/100 kcal`), weight basis (`g/100g`), volume basis (`g/100ml`), and serving basis.
   - Formalizes the "No Added Sugar" statutory conditions: no sugars of any type added, no ingredients containing sugars as ingredients, no concentrated fruit juice added that increases sugar content.
3. **`ICMR_TABLE_15_2_VERIFICATION.md` (v4.0.0)**:
   - Deep-dives into the **ICMR-NIN Dietary Guidelines for Indians (DGI) 2024, Guideline 15**.
   - **Table 15.1**: Nutrient thresholds per 100g/ml for Added Sugar, Added Fat, Salt, and Energy.
   - **Table 15.2**: The $3 \times 3$ matrix classifying foods by Level of Processing (Group A: Minimally Processed, Group B: Culinary Processed, Group C: Ultra-Processed Foods / UPF) across Energy Density Categories (Cat 1: Low, Cat 2: Medium, Cat 3: High).
   - Proves that **UPF and HFSS are independent dimensions**:
     - *Cell C1*: Ultra-Processed Food with Low Energy Density ($\rightarrow$ UPF, but NOT HFSS).
     - *Cell A3*: Minimally Processed Food with High Energy Density ($\rightarrow$ HFSS, but NOT UPF; e.g. pure raw nuts, cold-pressed vegetable oil).
4. **`SOURCE_PROVENANCE_REGISTER.md` (v4.0.0)**:
   - Registers all statutory source documents, legal citations, gazette notification numbers, publication dates, and explicit regulatory limitations.

---

## 4. Nutrition Interpretation Architecture

### 4.1 Foundational Architecture Principles
1. **Nutrient-Specific Evaluation**: Every nutrient is evaluated independently against its statutory standard. YumSure strictly rejects assigning a single composite "health score" (e.g. 72/100 or letter grade A–E). Composite scores mislead consumers by allowing high dietary fibre or protein to mask dangerously elevated added sugar or sodium.
2. **Explicit Measurement Denominators**: Enforces physical measurement bases:
   - `PER_100G`: Solid food concentration.
   - `PER_100ML`: Liquid beverage concentration.
   - `PER_100KCAL`: Caloric density (e.g. protein per 100 kcal).
   - `PER_SERVING`: Declared single portion.
   - `PCT_TOTAL_ENERGY`: Caloric contribution ($\% = \frac{\text{Nutrient (g)} \times \text{Atwater Factor}}{\text{Total Energy (kcal)}} \times 100$).
   - `PCT_TOTAL_FAT`: Fraction of lipid weight ($\% = \frac{\text{Trans Fat (g)}}{\text{Total Fat (g)}} \times 100$).
3. **Separation of Solids vs. Liquids**: Viscosity alters consumption velocity and satiety kinetics. FSSAI and ICMR-NIN establish distinct thresholds for solids and liquids (e.g., Low Sugar is $\le 5\text{g/100g}$ for solids vs $\le 2.5\text{g/100ml}$ for liquids).
4. **Four-State Nutrient Semantics**:
   - `PRESENT`: Explicitly extracted from facts panel.
   - `EXPLICITLY_ZERO`: Label explicitly declares 0g.
   - `NOT_DECLARED`: Omitted from label.
   - `UNKNOWN`: Unreadable or OCR error.
   - **Critical Rule**: Missing data (`NOT_DECLARED`) is **never converted to 0.0g**. If a manufacturer omits Added Sugar, the engine returns `INSUFFICIENT_DATA`, preventing unverified claims.
5. **No AI/LLM in Regulatory Decisions**: All evaluations are 100% deterministic Python AST executions. An LLM is never permitted to calculate compliance, invent thresholds, or override statutory pass/fail outcomes.

---

## 5. Database Architecture Decisions

Documented across `DATABASE_COMPATIBILITY_REVIEW.md`, `DATABASE_CONTRACT_PROPOSAL.md`, and `DATABASE_IMPLEMENTATION_REPORT.md`:

### 5.1 Decoupling FSSAI Claims from ICMR-NIN HFSS Rules
- `regulatory_claim_rules`: Strictly governs manufacturer voluntary claims under FSSAI 2018/2022.
- `icmr_nutrient_threshold_rules`: Governs Table 15.1 nutrient thresholds.
- `icmr_matrix_rules`: Governs Table 15.2 processing/energy matrix (A1–C3) without nutrient FK constraints.
- `nutrition_interpretation_rules` (Tejas's Phase 1A model): Retained for backwards compatibility, but flagged for transition to the dedicated ICMR models.

### 5.2 Compound Abstract Syntax Tree (AST) for Regulatory Claims
Replaces flat scalar columns with a structured, recursive AST schema stored in PostgreSQL `JSONB`:
```json
{
  "operator": "AND",
  "conditions": [
    {
      "nutrient_code": "saturated_fat",
      "basis": "PER_100G",
      "operator": "LTE",
      "value": 1.5
    },
    {
      "nutrient_code": "saturated_fat",
      "basis": "PCT_TOTAL_ENERGY",
      "operator": "LTE",
      "value": 10.0
    }
  ]
}
```
- **Supported Operators**: `'LT'` ($<$), `'LTE'` ($\le$), `'GT'` ($>$), `'GTE'` ($\ge$), `'EQ'` ($=$).
- **Security Guardrail**: Prohibits Python `eval()` and `exec()`. Validates AST using Pydantic v2 and enforces an iterative depth ceiling ($\le 5$ levels) via `check_ast_depth_iterative()`.

### 5.3 Five-State Evaluation Protocol
Every rule execution returns one of five standard enum values:
- `PASS`: Product satisfies all primary and secondary conditions.
- `FAIL`: Product violates at least one statutory condition.
- `INSUFFICIENT_DATA`: Mandatory nutrient is `NOT_DECLARED` or `UNKNOWN`.
- `INDETERMINATE`: Data is contradictory or unparsable.
- `NOT_APPLICABLE`: Food form or category outside the rule's statutory scope (e.g., Table 15.2 evaluated on beverages).

---

## 6. Phase 1B.3 Implementation Details

### 6.1 Implemented & Remediated Files
1. **`backend/app/models/claim_ast_schema.py`**:
   - Pydantic v2 schema defining `ClaimASTNode`, `LeafCondition`, and `CompoundCondition`.
   - Implements `check_ast_depth_iterative(raw_data, max_depth=5)` to prevent recursion/DoS attacks.
   - Enforces allowlisted operators and non-empty dictionaries/lists.
2. **`backend/app/models/regulatory_claim_rule.py`**:
   - Added `claim_family` (`NUTRIENT_CONTENT`, `NON_ADDITION`).
   - Added `condition_expression` as `JSONB, nullable=True` with `@validates` hook. Missing expressions safely return `INSUFFICIENT_DATA`.
   - Added `permitted_synonyms_schedule_ii` (`JSONB`).
3. **`backend/app/models/icmr_threshold_rule.py`**:
   - Maps to `icmr_nutrient_threshold_rules`. Captures Table 15.1 thresholds for Sugar, Fat, Salt, Energy per solid/liquid. Linked to `nutrients` FK.
4. **`backend/app/models/icmr_matrix_rule.py`**:
   - Maps to `icmr_matrix_rules`. Captures Table 15.2 9-cell matrix (`A1`–`C3`).
   - Stores `is_upf` and `is_hfss` independently. No nutrient FK. Solid food form default.
5. **`backend/app/models/ingredient.py`**:
   - Enhanced with `processing_classification` (`WHOLE_FOOD`, `CULINARY_PROCESSED`, `FUNCTIONAL_ADDITIVE`, `COSMETIC_ADDITIVE`, `INDUSTRIAL_FRACTION`, `INSUFFICIENT_EVIDENCE`, `UNKNOWN`).
   - Enhanced with `sugar_classification` (`NOT_SUGAR`, `INTRINSIC_SUGAR`, `ADDED_FREE_SUGAR`, `SUGAR_SUBSTITUTE_SWEETENER`, `NON_NUTRITIVE_SWEETENER`, `POLYOL`, `INSUFFICIENT_EVIDENCE`, `UNKNOWN`).
   - Both default strictly to `'UNKNOWN'` to prevent unverified false positives.
6. **`backend/app/models/ingredient_rule.py`**:
   - Reconciled check constraint `chk_ingredient_rule_type` supporting all 6 rule types: `'MANDATORY_LABEL_WARNING'`, `'MAX_PERMISSIBLE_LIMIT'`, `'POPULATION_PROHIBITION'`, `'SPECIAL_CONDITIONS'`, `'WARNING_MANDATE'`, `'MAX_LIMIT'`.
7. **`backend/app/models/nutrient.py`**:
   - Added relationship to `IcmrNutrientThresholdRule`.
8. **`backend/app/models/__init__.py`**:
   - Re-exports all 13 models, enum tuples, and AST validation functions. All tables register in `Base.metadata`.
9. **`backend/alembic/versions/0001_initial_foundation.py`**:
   - Baseline migration representing Tejas's Phase 1A schema.
10. **`backend/alembic/versions/0002_enhance_rules_and_ingredients.py`**:
    - Remediated migration applying Phase 1B enhancements without invalid `{}` defaults, creating the 2 separate ICMR tables, and applying reconciled check constraints.

---

## 7. Inventory of Files Created and Modified

| File Relative Path | Change Type | Responsibility | Status |
|---|---|---|---|
| `backend/app/models/claim_ast_schema.py` | Created | AST schema, iterative depth limiting, validation. | **VERIFIED** |
| `backend/app/models/icmr_threshold_rule.py` | Created | Table 15.1 nutrient thresholds model. | **VERIFIED** |
| `backend/app/models/icmr_matrix_rule.py` | Created | Table 15.2 2D matrix model (A1–C3 cells). | **VERIFIED** |
| `backend/app/models/regulatory_claim_rule.py` | Modified | Added AST JSONB, Schedule II synonyms, claim families. | **VERIFIED** |
| `backend/app/models/ingredient.py` | Modified | Added processing/sugar classes with UNKNOWN defaults. | **VERIFIED** |
| `backend/app/models/ingredient_rule.py` | Modified | Reconciled 6-type check constraint. | **VERIFIED** |
| `backend/app/models/nutrient.py` | Modified | Linked relationship to `IcmrNutrientThresholdRule`. | **VERIFIED** |
| `backend/app/models/__init__.py` | Modified | Re-exported all 13 tables for Alembic metadata. | **VERIFIED** |
| `backend/alembic/versions/0001_initial_foundation.py` | Created | Phase 1A baseline migration. | **VERIFIED** |
| `backend/alembic/versions/0002_enhance_rules_and_ingredients.py` | Created / Remediated | Phase 1B schema upgrade. | **VERIFIED** |
| `backend/tests/test_remediation_audit.py` | Created | 8-test automated audit suite. | **VERIFIED** |
| `PHASE_1B_3_INDEPENDENT_AUDIT.md` | Created | Initial audit ledger identifying DEF-01 to DEF-06. | **COMPLETED** |
| `PHASE_1B_3_REMEDIATION_REPORT.md` | Created | Detailed report of all 6 audit resolutions. | **COMPLETED** |
| `DATABASE_CONTRACT_PROPOSAL.md` | Created | Master technical contract for database layer. | **COMPLETED** |
| `DATABASE_COMPATIBILITY_REVIEW.md` | Created | Review of Phase 1A models vs regulatory research. | **COMPLETED** |
| `DATABASE_IMPLEMENTATION_REPORT.md` | Created | Implementation journal for Phase 1B.3. | **COMPLETED** |
| `NUTRIENT_REFERENCE_AUDIT.md` | Created | FSSAI vs ICMR RDA reconciliation. | **COMPLETED** |
| `NUTRIENT_CLASSIFICATION_RESEARCH.md` | Created | FSSAI Schedule I & II rules audit. | **COMPLETED** |
| `ICMR_TABLE_15_2_VERIFICATION.md` | Created | ICMR DGI 2024 Guideline 15 mathematical audit. | **COMPLETED** |
| `SOURCE_PROVENANCE_REGISTER.md` | Created | Legal provenance and statutory citations register. | **COMPLETED** |

---

## 8. Verification and Testing Evidence

### 8.1 Automated Test Suite (`backend/tests/test_remediation_audit.py`)
Executed command:
```powershell
.\backend\venv\Scripts\python.exe -m unittest backend/tests/test_remediation_audit.py
```
**Actual Output**:
```
........
----------------------------------------------------------------------
Ran 8 tests in 0.113s

OK
```

### Test Case Breakdown:
1. `test_01_icmr_model_separation`: **PASS**. Table 15.1 has nutrient FK; Table 15.2 has no nutrient FK and contains processing and category dimensions.
2. `test_02_matrix_a1_c3_representation`: **PASS**. All 9 cells verified. Cell C1 confirmed as `is_upf=True, is_hfss=False` (UPF without HFSS); Cell A3 confirmed as `is_upf=False, is_hfss=True`.
3. `test_03_ingredient_classification_states`: **PASS**. `UNKNOWN` and `INSUFFICIENT_EVIDENCE` present; defaults confirmed as `UNKNOWN`.
4. `test_04_ast_depth_limits`: **PASS**. Shallow AST passes; depth 5 passes; depth 6 rejected with `ValueError`; depth 50 rejected iteratively without recursion errors.
5. `test_05_ast_invalid_and_empty_structures`: **PASS**. Empty dicts, empty condition arrays, and invalid operators are rejected.
6. `test_06_missing_condition_expression`: **PASS**. `condition_expression=None` stores cleanly without validation exceptions.
7. `test_07_ingredient_rule_types`: **PASS**. All 6 rule types verified valid.
8. `test_08_sqlalchemy_metadata_registration`: **PASS**. All 13 tables discovered in `Base.metadata`.

### 8.2 Offline DDL Generation (PostgreSQL 18 Dialect)
Executed commands:
```powershell
.\backend\venv\Scripts\python.exe -m alembic -c alembic.ini upgrade --sql 0001_initial_foundation:0002_enhance_rules_and_ingredients
.\backend\venv\Scripts\python.exe -m alembic -c alembic.ini downgrade --sql 0002_enhance_rules_and_ingredients:0001_initial_foundation
```
**Results**:
- **Upgrade**: Successfully emits PostgreSQL DDL creating `icmr_nutrient_threshold_rules`, `icmr_matrix_rules`, adding columns with `UNKNOWN` defaults, and adding nullable `condition_expression`.
- **Downgrade**: Symmetrically reverts all operations in reverse foreign-key order.

---

## 9. Git and Collaboration Status

- **Branch**: `develop`
- **Latest Commit**: `bf3dab8` (*"Nutrition Report Analyasis"*)
- **Status with Remote**: Clean; all 21 files committed and synchronized.
- **Working Tree**: Clean (`nothing to commit, working tree clean`).
- **Dependencies on Tejas's Core**:
  - Leverages Tejas's `Base` in `backend/app/db/base.py`.
  - Leverages Tejas's `engine` and connection pooling in `backend/app/db/session.py`.
  - Fully compatible with `app.core.config.Settings`.

---

## 10. Status Summary Table

| Work Stream / Component | Status | Notes |
|---|:---:|---|
| **Nutrient Reference & Classification Research** | **COMPLETED** | Documented in 4 dedicated research markdown files. |
| **FSSAI Schedule I & II AST Modeling** | **COMPLETED** | `claim_ast_schema.py` and `regulatory_claim_rule.py`. |
| **ICMR Table 15.1 & 15.2 Decoupling** | **COMPLETED** | `icmr_threshold_rule.py` and `icmr_matrix_rule.py`. |
| **Ingredient UNKNOWN Defaults & Classification** | **COMPLETED** | `ingredient.py` and `ingredient_rule.py`. |
| **Automated Remediation Test Suite** | **COMPLETED** | 8/8 tests passing (`test_remediation_audit.py`). |
| **Offline Alembic Migration Scripts (0001 & 0002)** | **COMPLETED** | Generated, tested, and verified with `--sql`. |
| **Independent Remediation Review** | **REVIEWED** | Audit verdict: PASS (`PHASE_1B_3_REMEDIATION_REPORT.md`). |
| **PostgreSQL Windows Service Startup** | **BLOCKED** | Service `postgresql-x64-18` currently stopped on host. |
| **Live Database Migration Execution** | **PENDING** | Awaiting PostgreSQL service start and Tejas's command execution. |
| **Seed Reference Data (ICMR & FSSAI tables)** | **PROPOSED** | Ready to insert once migrations are applied. |
| **Deterministic Nutrition Engine Implementation** | **PENDING** | Phase 2 deliverable (`nutrition_engine.py`). |
| **Deterministic Claims Engine Implementation** | **PENDING** | Phase 2 deliverable (`claims_engine.py`). |
| **Deterministic Ingredient Engine Implementation** | **PENDING** | Phase 4 deliverable (`ingredient_engine.py`). |

---

## 11. Technical Risks and Important Decisions

1. **Migration Baseline Collision**:
   - If PostgreSQL is brand new: Run `alembic upgrade head` (Path A).
   - If PostgreSQL already had tables created via `create_all()`: Run `alembic stamp 0001_initial_foundation` then `alembic upgrade head` (Path B).
2. **AST Nesting Depth Limit**:
   - Depth is strictly capped at 5. Any rule requiring $> 5$ levels must be broken into composite sub-rules.
3. **Table 15.2 Liquid Foods Handling**:
   - Table 15.2 applies exclusively to solid foods. Beverages must always return `NOT_APPLICABLE` when evaluated against the A1–C3 matrix.
4. **Missing Nutrient Values**:
   - Never allow downstream API or engine code to coerce `None` or `NOT_DECLARED` into `0.0g`.

---

## 12. Action Items for Tejas

Tejas, as the Backend Lead, here are your exact action items to finalize Phase 1B:

1. **Review this Handover**: Confirm alignment with the 13-table schema and AST design.
2. **Start the PostgreSQL Service**:
   Run in an Administrator PowerShell prompt:
   ```powershell
   net start postgresql-x64-18
   ```
3. **Execute the Database Creation**:
   Ensure `yumsure_db` exists:
   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -p 5432 -c "CREATE DATABASE yumsure_db;"
   ```
4. **Apply Alembic Migrations**:
   ```powershell
   .\backend\venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
   ```
5. **Verify Live Tables**:
   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d yumsure_db -c "\dt"
   ```
   *(Verify that all 13 tables are present).*

---

## 13. Recommended Next Development Phase

Once Tejas applies the migrations to PostgreSQL, the project moves immediately into:
- **Phase 1B.4 (Reference Data Seeding)**: Inserting the official FSSAI Schedule I claims and ICMR Table 15.1/15.2 seed rows into `yumsure_db`.
- **Phase 2 (Deterministic Engines)**: Building `nutrition_engine.py` and `claims_engine.py` in `backend/app/services/` to evaluate products against these database rules.

