# YumSure — Phase 1B.3 Independent Database Implementation Audit

**Document Version**: 1.0.0  
**Audit Date**: 3 November 2026  
**Auditor**: Senior Backend Architect & Nutrition Regulatory Intelligence Lead  
**Scope**: Technical audit of SQLAlchemy models, AST security schemas, and Alembic migrations (`0001_initial_foundation.py`, `0002_enhance_rules_and_ingredients.py`) prior to live database application.  
**Governing Documents**:
- `NUTRIENT_REFERENCE_AUDIT.md` (v3.0.0)
- `NUTRIENT_CLASSIFICATION_RESEARCH.md` (v4.0.0)
- `ICMR_TABLE_15_2_VERIFICATION.md` (v4.0.0)
- `SOURCE_PROVENANCE_REGISTER.md` (v4.0.0)
- `DATABASE_CONTRACT_PROPOSAL.md` (v1.0.0)
- `DATABASE_IMPLEMENTATION_REPORT.md` (v1.0.0)

---

## 1. Executive Verdict: FAIL — MIGRATION BLOCKED

> [!CAUTION]
> **AUDIT VERDICT: FAIL — MIGRATION BLOCKED (DO NOT APPLY MIGRATION)**  
> While the Python models compile, SQLAlchemy metadata registers cleanly, and Alembic offline SQL generates without syntax errors, the implementation contains **four critical architectural defects** that violate the approved research contract and risk database runtime errors.
> 
> **Live database migration MUST NOT be executed until the required fixes are applied.**

### Summary Scorecard

| Audit Dimension | Status | Key Risk / Defect |
| :--- | :---: | :--- |
| **1. Migration History Compatibility** | **FAIL** | Baseline `0001` assumes clean database; crashes if developer previously ran `create_all()`. `0002` injects invalid `{}` default into `condition_expression`. |
| **2. ICMR Data Model Correctness** | **FAIL** | `IcmrHfssRule` collapses Table 15.1 thresholds and Table 15.2 matrix into a nutrient-bound table, making the 9-cell A1–C3 matrix impossible to store. |
| **3. AST Security & Validation** | **CONDITIONAL PASS** | Zero `eval()`/`exec()` verified. Pydantic validator active. However, AST schema lacks maximum recursion depth protection against denial-of-service payloads. |
| **4. Nutrient & Ingredient Models** | **FAIL** | `processing_classification` and `sugar_classification` lack `UNKNOWN` / `INSUFFICIENT_EVIDENCE` states and default to `FUNCTIONAL_ADDITIVE`. |
| **5. Migration Safety & Reversibility** | **CONDITIONAL PASS** | Reversibility verified in offline SQL, but destructive data loss on downgrade and constraint name assumptions require hardening. |

---

## 2. Dimension 1: Migration History Compatibility

### 2.1 The "Unstamped Baseline" Conflict
- **File Reference**: [`backend/alembic/versions/0001_initial_foundation.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/alembic/versions/0001_initial_foundation.py#L22-L185)
- **Finding**: In Stage 5 & 6 of `documentation/DEVELOPER_EXECUTION_JOURNAL.md`, Tejas verified SQLAlchemy models and session creation. If a developer or automated test executed `Base.metadata.create_all(engine)` against a local PostgreSQL instance, tables `products`, `nutrients`, etc. already exist without an `alembic_version` tracking table.
- **Impact**: Running `alembic upgrade head` on such an initialized instance will fail immediately at Step 1 with `psycopg.errors.DuplicateTable: relation "data_sources" already exists`.
- **Required Resolution**: Alembic `env.py` and documentation must provide an explicit stamp check (`alembic stamp 0001_initial_foundation`) for pre-existing instances before applying `0002`.

### 2.2 Invalid AST Injected by Migration Default
- **File Reference**: [`backend/alembic/versions/0002_enhance_rules_and_ingredients.py:70`](file:///d:/Hackthon/hack-sudo-chaos/backend/alembic/versions/0002_enhance_rules_and_ingredients.py#L70)
- **Code**:
  ```python
  sa.Column('condition_expression', JSONB(astext_type=sa.Text()), nullable=False, server_default='{}')
  ```
- **Finding**: The migration sets `server_default='{}'`. However, [`backend/app/models/claim_ast_schema.py:126-129`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/models/claim_ast_schema.py#L126-L129) enforces:
  ```python
  @model_validator(mode="after")
  def validate_non_empty(self) -> "ClaimConditionGroup":
      if not self.conditions:
          raise ValueError("ClaimConditionGroup must contain at least one condition")
      return self
  ```
- **Impact**: Any pre-existing rows in `regulatory_claim_rules` that receive `{}` as `condition_expression` will fail validation upon being loaded or updated via the SQLAlchemy ORM (`pydantic.ValidationError: ClaimConditionGroup must contain at least one condition`).
- **Required Resolution**: Column `condition_expression` must either be `nullable=True` during initial addition, or populated with an allowlisted stub AST before enforcing `nullable=False`.

---

## 3. Dimension 2: ICMR Data Model Audit (Critical Defect)

### 3.1 Failure to Represent the 2D Matrix (Table 15.2 vs Table 15.1)
- **File Reference**: [`backend/app/models/icmr_hfss_rule.py:25-37`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/models/icmr_hfss_rule.py#L25-L37)
- **Code**:
  ```python
  class IcmrHfssRule(Base):
      __tablename__ = "icmr_hfss_rules"

      rule_id: Mapped[str] = mapped_column(String(100), primary_key=True)
      rule_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
      target_nutrient_code: Mapped[str] = mapped_column(
          String(50),
          ForeignKey("nutrients.nutrient_code"),
          nullable=False
      )
      food_form: Mapped[str] = mapped_column(String(20), nullable=False)

      table_15_1_threshold: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
      measurement_basis: Mapped[str] = mapped_column(String(30), nullable=False)

      cat_2_energy_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
      cat_3_energy_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
  ```
- **Finding**:
  1. **Strict Nutrient Foreign Key**: `target_nutrient_code` is `nullable=False` and bound to `nutrients.nutrient_code`. Table 15.2 is an independent $3 \times 3$ classification matrix of Food Processing Groups (A, B, C) and Nutritional Quality Categories (1, 2, 3). Cells in Table 15.2 (e.g. Cell C1 = Non-HFSS Ultra-Processed Food) **do not have a target nutrient**. They are product-level multi-nutrient evaluations.
  2. **Improper Colocation of Table 15.1 and 15.2**: Putting `cat_2_energy_min` and `cat_3_energy_min` on a *nutrient threshold* record is scientifically incorrect. Energy density tiers ($>250\text{ kcal}$ and $>500\text{ kcal}$) belong to the product as a whole, driven by added sugar or added fat, not to each individual nutrient threshold.
  3. **Complete Absence of Processing Groups (A, B, C)**: There are no fields for `processing_group`, `matrix_cell`, `group_description`, or `classification_criteria`.
  4. **Liquids Handled Incorrectly**: Table 15.2 explicitly applies only to solid foods. The model permits `food_form IN ('solid', 'liquid')` while leaving `cat_2_energy_min` nullable, but provides no relational structure to indicate that liquid matrix classification is unsupported by ICMR-NIN.
- **Impact**: It is currently impossible to store Table 15.2 rules in the database without inventing fake nutrient codes or abusing columns. The engine cannot classify a product into the A1–C3 matrix.
- **Required Resolution**:
  Decouple the ICMR entities into:
  1. `icmr_nutrient_threshold_rules` (Table 15.1: Nutrient thresholds for Added Sugar, Added Fat, Salt, Energy per solid/liquid).
  2. `icmr_matrix_rules` (Table 15.2: 9-cell matrix definition mapping `(processing_group, category_tier)` to consumer advisories and dietary guidance).

---

## 4. Dimension 3: AST Security & Validation Audit

### 4.1 Positive Security Guarantees
- **File Reference**: [`backend/app/models/claim_ast_schema.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/models/claim_ast_schema.py)
- **Verified**:
  - Zero dynamic code evaluation (`eval()`, `exec()`, `compile()`) exists anywhere in the codebase.
  - Comparison operators are restricted to strictly allowlisted enum: `LT`, `LTE`, `GT`, `GTE`, `EQ`.
  - Logical operators are restricted to `AND`, `OR`.
  - Supported measurement bases strictly reflect FSSAI claims: `PER_100G`, `PER_100ML`, `PER_100KCAL`, `PER_SERVING`, `PCT_TOTAL_ENERGY`, `PCT_TOTAL_FAT`.
  - SQLAlchemy model enforces `@validates("condition_expression")` on write.

### 4.2 AST Security Vulnerability: Unbounded Recursion Depth
- **File Reference**: [`backend/app/models/claim_ast_schema.py:89`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/models/claim_ast_schema.py#L89)
- **Code**:
  ```python
  nested_expression: Optional["ClaimConditionGroup"] = None
  ```
- **Finding**: There is no check limiting the depth of nested `EXPRESSION_GROUP` nodes. A deeply nested JSON payload (e.g. 500 levels of nested `AND` groups) will cause a `RecursionError` in Python during Pydantic traversal or evaluation, causing a Denial of Service (DoS) vulnerability on the API thread.
- **Required Fix**: Add a depth counter in `ClaimConditionGroup` validation restricting maximum AST depth to 5 levels (sufficient for all FSSAI Schedule I compound conditions).

---

## 5. Dimension 4: Nutrient and Ingredient Model Audit

### 5.1 Missing Unknown / Insufficient Data States in Ingredient Classifications
- **File Reference**: [`backend/app/models/ingredient.py:20-36, 54`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/models/ingredient.py#L20-L36)
- **Code**:
  ```python
  INGREDIENT_PROCESSING_CLASSES = (
      'WHOLE_FOOD',
      'CULINARY_PROCESSED',
      'FUNCTIONAL_ADDITIVE',
      'COSMETIC_ADDITIVE',
      'INDUSTRIAL_FRACTION'
  )

  INGREDIENT_SUGAR_CLASSES = (
      'NOT_SUGAR',
      'INTRINSIC_SUGAR',
      'ADDED_FREE_SUGAR',
      'SUGAR_SUBSTITUTE_SWEETENER',
      'NON_NUTRITIVE_SWEETENER',
      'POLYOL'
  )
  ...
  processing_classification: Mapped[str] = mapped_column(
      String(30),
      default="FUNCTIONAL_ADDITIVE",
      nullable=False
  )
  ```
- **Finding**:
  1. Neither `INGREDIENT_PROCESSING_CLASSES` nor `INGREDIENT_SUGAR_CLASSES` includes `'UNKNOWN'` or `'INSUFFICIENT_EVIDENCE'`.
  2. The column default for `processing_classification` is set to `'FUNCTIONAL_ADDITIVE'`.
- **Impact**:
  - If a packaged product contains an uncataloged ingredient, spice blend, or complex natural extract, it cannot be stored as `UNKNOWN` or `INSUFFICIENT_EVIDENCE`.
  - Defaulting to `FUNCTIONAL_ADDITIVE` falsely marks natural or uncharacterized ingredients as chemical additives, directly violating Guideline 15 research rules.
- **Required Fix**:
  1. Add `'UNKNOWN'` and `'INSUFFICIENT_EVIDENCE'` to `INGREDIENT_PROCESSING_CLASSES` and `INGREDIENT_SUGAR_CLASSES`.
  2. Change column defaults from `'FUNCTIONAL_ADDITIVE'` to `'UNKNOWN'`.

---

## 6. Dimension 5: Migration Safety & Reversibility Audit

### 6.1 Constraint Conflict on `ingredient_rules`
- **File Reference**: [`backend/alembic/versions/0002_enhance_rules_and_ingredients.py:117-121`](file:///d:/Hackthon/hack-sudo-chaos/backend/alembic/versions/0002_enhance_rules_and_ingredients.py#L117-L121)
- **Code**:
  ```python
  op.create_check_constraint(
      'chk_ingredient_rule_type',
      'ingredient_rules',
      "rule_type IN ('MANDATORY_LABEL_WARNING', 'MAX_PERMISSIBLE_LIMIT', 'POPULATION_PROHIBITION', 'SPECIAL_CONDITIONS')"
  )
  ```
- **Finding**: In Tejas's initial model [`backend/app/models/ingredient_rule.py:31`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/models/ingredient_rule.py#L31), the comment specified:
  ```python
  rule_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'WARNING_MANDATE', 'MAX_LIMIT'
  ```
  If any developer seeded test records using `'WARNING_MANDATE'` or `'MAX_LIMIT'`, applying migration `0002` will immediately fail with a `CheckConstraintViolation`.
- **Required Fix**: Include legacy rule types in the allowed set or provide a data migration `UPDATE` statement in `0002` prior to creating the constraint.

### 6.2 Data Loss on Downgrade
- **File Reference**: [`backend/alembic/versions/0002_enhance_rules_and_ingredients.py:133-180`](file:///d:/Hackthon/hack-sudo-chaos/backend/alembic/versions/0002_enhance_rules_and_ingredients.py#L133-L180)
- **Finding**: Running `alembic downgrade -1` will permanently drop all columns added to `nutrients` and `ingredients`, and drop table `icmr_hfss_rules`. While this is standard for a full rollback, developers must be warned that rollback destroys newly cataloged ingredient processing and sugar classifications.

---

## 7. Comprehensive Defect Ledger (Ranked by Severity)

| ID | Severity | File | Line(s) | Description | Required Action |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **DEF-01** | **CRITICAL** | `backend/app/models/icmr_hfss_rule.py` | 25–37 | Table 15.2 (3x3 Matrix) cannot be represented because table is constrained by non-null `target_nutrient_code`. | Refactor into two clean tables: `icmr_nutrient_threshold_rules` and `icmr_matrix_rules`. |
| **DEF-02** | **CRITICAL** | `backend/alembic/versions/0002_enhance_rules_and_ingredients.py` | 70 | Migration sets `server_default='{}'` on `condition_expression`, creating rows that fail Pydantic AST validation. | Make column initially nullable or provide a valid AST seed object before setting NOT NULL. |
| **DEF-03** | **HIGH** | `backend/app/models/ingredient.py` | 20–36, 54 | Missing `UNKNOWN` state in `processing_classification` and `sugar_classification`; dangerous default to `FUNCTIONAL_ADDITIVE`. | Add `UNKNOWN` to enum sets and change default from `FUNCTIONAL_ADDITIVE` to `UNKNOWN`. |
| **DEF-04** | **HIGH** | `backend/app/models/claim_ast_schema.py` | 89, 120 | No maximum nesting depth in AST parser, exposing system to DoS via deeply nested JSON expressions. | Add `@field_validator` or `@model_validator` enforcing `max_depth <= 5`. |
| **DEF-05** | **MEDIUM** | `backend/alembic/versions/0001_initial_foundation.py` | 22–185 | Baseline migration crashes if developer already created tables via `Base.metadata.create_all()`. | Add verification instructions for `alembic stamp 0001_initial_foundation`. |
| **DEF-06** | **MEDIUM** | `backend/alembic/versions/0002_enhance_rules_and_ingredients.py` | 117–121 | Check constraint `chk_ingredient_rule_type` breaks if existing rows used Tejas's example types (`WARNING_MANDATE`, `MAX_LIMIT`). | Add data migration update or include legacy terms in check constraint. |

---

## 8. Safe Local Verification Commands (Non-Destructive)

To verify the audit findings without executing migrations or connecting to a live database:

```powershell
# 1. Verify AST rejection of empty dictionary default (DEF-02 demonstration)
.\backend\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend'); from app.models.claim_ast_schema import validate_ast_structure; validate_ast_structure({})"

# 2. Verify inability to set UNKNOWN processing class (DEF-03 demonstration)
.\backend\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend'); from app.models.ingredient import INGREDIENT_PROCESSING_CLASSES; assert 'UNKNOWN' in INGREDIENT_PROCESSING_CLASSES"

# 3. Inspect offline DDL for server_default='{}'
Set-Location backend; .\venv\Scripts\python.exe -m alembic upgrade --sql 0001_initial_foundation:0002_enhance_rules_and_ingredients | Select-String "condition_expression"
```

---

## 9. Conclusion & Next Steps

Phase 1B.3 must **NOT** be applied to PostgreSQL in its current state. 

Before applying the migration, the team must address `DEF-01` through `DEF-04` by:
1. Updating `backend/app/models/ingredient.py` to support `UNKNOWN` states and eliminate the `FUNCTIONAL_ADDITIVE` default.
2. Updating `backend/app/models/claim_ast_schema.py` with maximum depth recursion protection.
3. Restructuring `icmr_hfss_rule.py` into dedicated Table 15.1 and Table 15.2 entities.
4. Regenerating `backend/alembic/versions/0002_enhance_rules_and_ingredients.py` with valid AST defaults and safe constraint transitions.

