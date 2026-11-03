# YumSure — Phase 3: Domain Evaluation DTO Contract & Integration Specification

**Document Version**: 1.1.0  
**Phase**: Phase 3 — Backend Service & Engine Integration  
**Lead Authors**: Senior Backend Architect & Nutrition Regulatory Intelligence Lead (Abhishek)  
**Collaborator & Approver**: Tejas (Backend Foundation & Database Lead)  
**Target Repository**: `d:\Hackthon\hack-sudo-chaos`  
**Status**: REVISED SPECIFICATION BASED ON ARCHITECTURAL DECISIONS  

---

## 1. Ownership Division & Architectural Boundaries

In accordance with the agreed team ownership split:

| Layer / Responsibility | Owner | Boundary & Guarantees |
| :--- | :---: | :--- |
| **Domain Evaluation Contracts (`contracts.py`)** | Abhishek | Pure Python / Pydantic V2 DTOs. Zero framework dependencies (no FastAPI, no SQLAlchemy ORM). Location preserved at `backend/app/domain/engines/contracts.py`. |
| **Evaluation Rules Bundle (`EvaluationRulesBundle`)** | Abhishek | Typed immutable container for all static & database-backed regulatory rules matching the four engine signatures. |
| **Unified Result DTO (`UnifiedProductEvaluationResult`)** | Abhishek | Aggregates all four engine results without fabricating a composite health score, letter grade, or star rating. |
| **Domain Engine Coordinator (`coordinator.py`)** | Abhishek | Pure domain function coordinating `nutrition_engine`, `icmr_hfss_engine`, `claims_engine`, and `ingredient_engine`. *(Not implemented yet; contract only).* |
| **Engine-Level Deterministic Tests** | Abhishek | 100% in-memory deterministic test fixtures covering all regulatory scenarios. |
| **ORM Models & Migrations** | **Tejas** | Preserves existing tables, foreign keys, and migration history (0001, 0002, 0003). No database migrations required for Phase 3 DTO alignment. |
| **ProductRepository & Data Access** | **Tejas** | Eager-loading queries for `Product`, `ProductNutrient`, `ProductIngredient`, and `DataSource`. |
| **ORM-to-Domain Mapping Layer** | **Tejas** | Maps SQLAlchemy ORM entities to `ProductEvaluationInput`. Explicitly handles nutrient measurement basis and declared claims. |
| **FastAPI Routes & API Schemas** | **Tejas** | Endpoints under `/api/v1/products/...` delivering unified JSON responses. |
| **Database & API Integration Tests** | **Tejas** | End-to-end API integration tests using test database or client fixtures. |

---

## 2. Preserved Enumerations & Exact Semantics

All existing domain enumerations defined in [`backend/app/domain/engines/contracts.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/engines/contracts.py) are preserved without modification.

### 2.1 `FoodForm`
```python
class FoodForm(str, Enum):
    SOLID = "solid"
    LIQUID = "liquid"
```
- Physical state of the food as declared or legally categorized. Controls solid vs. liquid threshold branches in regulatory rules.

### 2.2 `NutrientDataStatus`
```python
class NutrientDataStatus(str, Enum):
    PRESENT = "PRESENT"
    EXPLICITLY_ZERO = "EXPLICITLY_ZERO"
    NOT_DECLARED = "NOT_DECLARED"
    UNKNOWN = "UNKNOWN"
```
- **Strict Semantic Guarantees**:
  - `PRESENT`: Explicit positive numeric value extracted from the packaging nutrition table (e.g., Protein: 8.0g).
  - `EXPLICITLY_ZERO`: Explicitly declared as zero on the packaging label (e.g., "Trans Fat: 0g", "Sugar: Nil"). Essential for substantiating FSSAI claims such as "Trans Fat Free" and "No Added Sugar".
  - `NOT_DECLARED`: Omitted entirely from the packaging nutrition table. **STRICT PROHIBITION**: Must never be silently coerced to numeric `0.0`. Triggers `EvaluationStatus.INSUFFICIENT_DATA` in engines.
  - `UNKNOWN`: Unreadable, damaged, or corrupted OCR/source data.

### 2.3 `MeasurementBasis`
```python
class MeasurementBasis(str, Enum):
    PER_100G = "PER_100G"
    PER_100ML = "PER_100ML"
    PER_100KCAL = "PER_100KCAL"
    PER_SERVING = "PER_SERVING"
    PCT_TOTAL_ENERGY = "PCT_TOTAL_ENERGY"
    PCT_TOTAL_FAT = "PCT_TOTAL_FAT"
```
- **Crucial Distinction**: `PER_100G` (mass basis) and `PER_100ML` (volume basis) represent fundamentally distinct physical measurement frames and must never be conflated.

### 2.4 `IngredientProcessingClass`
```python
class IngredientProcessingClass(str, Enum):
    WHOLE_FOOD = "WHOLE_FOOD"
    CULINARY_PROCESSED = "CULINARY_PROCESSED"
    FUNCTIONAL_ADDITIVE = "FUNCTIONAL_ADDITIVE"
    COSMETIC_ADDITIVE = "COSMETIC_ADDITIVE"
    INDUSTRIAL_FRACTION = "INDUSTRIAL_FRACTION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNKNOWN = "UNKNOWN"
```

### 2.5 `IngredientSugarClass`
```python
class IngredientSugarClass(str, Enum):
    NOT_SUGAR = "NOT_SUGAR"
    INTRINSIC_SUGAR = "INTRINSIC_SUGAR"
    ADDED_FREE_SUGAR = "ADDED_FREE_SUGAR"
    SUGAR_SUBSTITUTE_SWEETENER = "SUGAR_SUBSTITUTE_SWEETENER"
    NON_NUTRITIVE_SWEETENER = "NON_NUTRITIVE_SWEETENER"
    POLYOL = "POLYOL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNKNOWN = "UNKNOWN"
```

### 2.6 `EvaluationStatus`
```python
class EvaluationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INDETERMINATE = "INDETERMINATE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
```
- **Evaluation Status Definitions**:
  - `PASS`: Factually compliant with the specific statutory rule or guideline.
  - `FAIL`: Statutorily non-compliant or breaches a regulatory limit.
  - `INSUFFICIENT_DATA`: Mandatory factual evidence (e.g. undeclared nutrient, missing serving size) is absent.
  - `INDETERMINATE`: Scientific ambiguity prevents definitive classification (e.g., conflicting additive classifications).
  - `NOT_APPLICABLE`: Rule scope does not apply to this food form, category, or claim type.

---

## 3. Disambiguation of Nutrient Measurement Basis

### 3.1 The Problem
In the database schema (`product_nutrients.per_100g_value Numeric(10,3)`), the column name hardcodes `per_100g_value`. For liquid products (beverages, syrups), the reference declaration on Indian packaging is almost universally **per 100 ml**, yet the value was stored in `per_100g_value`.
Previously, engines or consumers assumed that if `product.food_form == FoodForm.LIQUID`, the basis was implicitly `PER_100ML`.
However:
1. Viscous or dense liquids (e.g., condensed milk, honey, ghee, edible oils) are often declared **per 100 g** rather than per 100 ml.
2. Powders meant for reconstitution as liquids (e.g., drink mixes, soup powders) may have declarations per 100 g dry powder or per 100 ml reconstituted liquid.
3. Silent inference of measurement basis from `product.food_form` creates dangerous false equivalences because 100 ml $\neq$ 100 g unless density is exactly 1.0 g/ml.

### 3.2 Resolution: Explicit Measurement Basis in `NutrientObservationInput`
We add an explicit, required field `measurement_basis` to `NutrientObservationInput`:
```python
class NutrientObservationInput(BaseModel):
    nutrient_code: str = Field(..., description="Canonical nutrient identifier code")
    measurement_basis: MeasurementBasis = Field(
        default=MeasurementBasis.PER_100G,
        description="Explicit measurement basis for the reference value: strictly PER_100G or PER_100ML"
    )
    per_100g_value: Optional[Decimal] = Field(
        None,
        description="Standard reference quantity (per 100g if measurement_basis==PER_100G, or per 100ml if measurement_basis==PER_100ML)"
    )
    per_serving_value: Optional[Decimal] = Field(
        None,
        description="Numeric value per declared serving (measurement basis PER_SERVING)"
    )
    unit: str = Field(..., description="Measurement unit (e.g. 'g', 'mg', 'kcal')")
    data_status: NutrientDataStatus = Field(..., description="Four-state declaration status")
```

### 3.3 Database Preservation & Mapper Translation
- **Zero Schema Migrations**: The PostgreSQL table `product_nutrients` remains unchanged. The column `per_100g_value` continues to store the 100-unit reference numeric value.
- **How Tejas's Mapper Maps to Domain Basis**:
  When mapping `ProductNutrient` $\rightarrow$ `NutrientObservationInput`:
  1. **Primary Check**: The mapper inspects `product.package_size`, `product.serving_size_unit`, or metadata inside `product.raw_source_payload` to check whether the nutrition table declares per 100g or per 100ml.
  2. **Fallback**: If `product.food_form == "liquid"` and `product.serving_size_unit in ("ml", "l", "L")`, the mapper sets `measurement_basis = MeasurementBasis.PER_100ML`. If solid, it sets `measurement_basis = MeasurementBasis.PER_100G`.
  3. **Explicit Storage**: The resulting `NutrientObservationInput.measurement_basis` explicitly communicates whether the value in `per_100g_value` is `PER_100G` or `PER_100ML`.
  4. **Prohibition**: Downstream engines must read `obs.measurement_basis` directly and must **never** infer it from `product.food_form`.

### 3.4 Identified Engine Changes Required for Measurement Basis Validation
*(Documented for implementation phase; no engine code modified during this contract phase)*:

1. **`claims_engine.py`**:
   - In AST evaluation for `NUTRIENT_THRESHOLD`:
     ```python
     rule_basis = node.get("measurement_basis", "PER_100G")
     ```
   - Currently, `claims_engine.py` checks `req_form != product.food_form.value`, but does not verify `obs.measurement_basis`.
   - **Required update**: If `rule_basis in ("PER_100G", "PER_100ML")` and `obs.measurement_basis.value != rule_basis`:
     - Because density is not known without volumetric mass declaration, the engine cannot convert between mass and volume.
     - The engine must return `EvaluationStatus.INDETERMINATE` with an explanation: `"Rule requires evaluation on a {rule_basis} basis, but nutrient declaration is on a {obs.measurement_basis.value} basis with unknown density."`
2. **`icmr_hfss_engine.py`**:
   - In Table 15.1 evaluation:
     - Solid thresholds require `PER_100G`.
     - Liquid thresholds require `PER_100ML`.
   - **Required update**: If a liquid product has `obs.measurement_basis == MeasurementBasis.PER_100G`, Table 15.1 cannot be evaluated directly against liquid ml thresholds. The engine must emit an `INDETERMINATE` or `INSUFFICIENT_DATA` rule result.
3. **`nutrition_engine.py`**:
   - Audit checks whether values are per 100g or per 100ml for daily reference calculations.

---

## 4. Exact Typed `EvaluationRulesBundle`

Grounded strictly in the existing signatures and dependencies of all four engines:

```python
class EvaluationRulesBundle(BaseModel):
    """
    Immutable bundle encapsulating all verified regulatory rule sets and catalogues
    required across all four deterministic engines.
    
    Field names and types correspond exactly to the parameters required by:
    1. evaluate_nutrition(product, custom_reference_catalogue)
    2. evaluate_icmr_hfss(product, threshold_rules, matrix_rules)
    3. evaluate_claims(product, rules, synonym_registry)
    4. evaluate_ingredients(product, ingredient_rules, ingredient_catalogue)
    """
    # 1. Nutrition Engine dependencies
    # evaluate_nutrition(product, custom_reference_catalogue=...)
    nutrition_catalogue: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional custom daily RDI reference catalogue mapping nutrient codes to {'rdi_value': Decimal, 'unit': str, 'display_name': str}. If None, engine uses FSSAI_STANDARD_DAILY_RDI."
    )
    
    # 2. ICMR-NIN HFSS Engine dependencies
    # evaluate_icmr_hfss(product, threshold_rules=..., matrix_rules=...)
    icmr_threshold_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="ICMR Table 15.1 nutrient thresholds of concern (8 seed records). Keys accessed: rule_id, rule_code, nutrient_code, food_form, threshold_value, threshold_operator, guideline_reference, official_source_url, source_version, notes_and_limitations."
    )
    icmr_matrix_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="ICMR Table 15.2 2D food classification matrix rules (9 seed records: A1-C3). Keys accessed: rule_id, processing_group, nutritional_category, classification_result, guideline_reference, official_source_url, source_version."
    )
    
    # 3. FSSAI Statutory Claims Engine dependencies
    # evaluate_claims(product, rules=..., synonym_registry=...)
    claims_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="FSSAI Schedule I statutory claim rules with AST conditions (14 seed records). Keys accessed: claim_id, claim_code, claim_title, claim_family, condition_expression, regulatory_reference, official_source_url, source_version."
    )
    synonym_registry: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="FSSAI Schedule II authorized synonyms mapping (9 claim codes mapping to permitted synonym string lists)."
    )
    
    # 4. Ingredient & Allergen Engine dependencies
    # evaluate_ingredients(product, ingredient_rules=..., ingredient_catalogue=...)
    ingredient_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Statutory ingredient rules for warnings and additive limits (6 seed records). Keys accessed: rule_id, rule_type, target_ingredient_code, target_food_category, warning_statement_mandated, max_permissible_ppm, regulatory_reference, consumer_guidance."
    )
    ingredient_catalogue: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Canonical ingredient catalogue lookup dictionary mapping ingredient codes to properties."
    )
```

---

## 5. Unified Product Evaluation Result DTO

```python
from datetime import datetime, timezone

class DataQualitySeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    DEFECT = "DEFECT"


class DataQualityNotice(BaseModel):
    """Factual telemetry regarding missing, corrupted, or uncharacterized input data."""
    severity: DataQualitySeverity = Field(..., description="Notice severity level")
    field_name: str = Field(..., description="Target field with data quality observation")
    message: str = Field(..., description="Factual description of data quality condition")
    impact: str = Field(..., description="Direct consequence on engine evaluation completeness")


class EvaluationSummaryCounts(BaseModel):
    """
    Aggregated rule outcome frequency counts across all four engines.
    
    STRICT PROHIBITION:
    This DTO contains only objective counts of evaluated rules by status.
    It does NOT compute, represent, or imply an overall health score, grade,
    traffic-light summary, or star rating.
    """
    total_rules_evaluated: int = Field(..., description="Total atomic rules evaluated across all engines")
    by_outcome: Dict[EvaluationStatus, int] = Field(
        default_factory=dict,
        description="Outcome counts broken down strictly by EvaluationStatus enum keys"
    )


class UnifiedProductEvaluationResult(BaseModel):
    """
    Unified product evaluation response combining independent evaluations from all four engines.
    
    Preserves complete engine isolation and audit trails.
    STRICT PROHIBITION: Never calculates an overall product grade, star rating, or health score.
    """
    product_id: Optional[str] = Field(None, description="Product identifier / UUID string")
    product_name: str = Field(..., description="Commercial product name")
    brand_name: Optional[str] = Field(None, description="Commercial brand name")
    food_form: FoodForm = Field(..., description="Physical state: 'solid' or 'liquid'")
    food_category: Optional[str] = Field(None, description="Food category (e.g. 'BEVERAGE', 'CEREAL')")
    package_size: Optional[str] = Field(None, description="Package declaration")
    serving_size_value: Optional[Decimal] = Field(None, description="Serving size value")
    serving_size_unit: str = Field("g", description="Serving size unit")
    data_source_id: Optional[str] = Field(None, description="Provenance source ID")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of evaluation execution"
    )
    
    # 1. Independent Engine Batch Results
    nutrition_evaluation: EngineBatchResult = Field(
        ...,
        description="Complete result from nutrition_engine.evaluate_nutrition"
    )
    icmr_hfss_evaluation: EngineBatchResult = Field(
        ...,
        description="Complete result from icmr_hfss_engine.evaluate_icmr_hfss"
    )
    claims_evaluation: EngineBatchResult = Field(
        ...,
        description="Complete result from claims_engine.evaluate_claims"
    )
    ingredient_evaluation: EngineBatchResult = Field(
        ...,
        description="Complete result from ingredient_engine.evaluate_ingredients"
    )
    
    # 2. Transparent Data Quality Telemetry
    data_quality_notices: List[DataQualityNotice] = Field(
        default_factory=list,
        description="List of factual data quality notices (missing mandatory nutrients, indeterminate groups, etc.)"
    )
    
    # 3. Objective Outcome Count Summary
    summary: EvaluationSummaryCounts = Field(
        ...,
        description="Aggregated rule outcome counts across all engines (no composite score)"
    )
```

---

## 6. Declared Claims Representation & Mapper Responsibilities

### 6.1 Domain Representation
Declared marketing claims are represented via `DeclaredClaimInput`:
```python
class DeclaredClaimInput(BaseModel):
    claim_code: str = Field(..., description="Target claim code to evaluate (e.g. 'TRANS_FAT_FREE', 'HIGH_PROTEIN')")
    raw_label_statement: str = Field(..., description="Verbatim marketing claim text found on product packaging")
```

### 6.2 Database Reality & Ingestion Boundaries
1. **Database Truth**: The PostgreSQL schema has NO `product_claims` table or foreign key. The `Product` model has a nullable `raw_source_payload: Optional[Any] = mapped_column(JSONB, nullable=True)`.
2. **Do Not Assume `raw_source_payload` Structure**:
   `raw_source_payload` may be null, or may contain vendor-specific data (e.g. OpenFoodFacts JSON, scraped HTML, or unparsed text). The mapper must **never** assume a specific unverified dictionary structure.
3. **Mapper Contract for Tejas**:
   - The ORM-to-domain mapper must support receiving declared claims from two verified sources:
     - **Source A (API Request Body / Parameters)**: When a client calls `/api/v1/products/{id}/evaluate`, the client may provide an optional list of declared claims: `declared_claims: Optional[List[DeclaredClaimSchema]] = None`. If provided, the mapper/service passes these directly into `ProductEvaluationInput.declared_claims`.
     - **Source B (Explicit Payload Inspection)**: If `product.raw_source_payload` is a `dict` AND contains an explicit key `"declared_claims"` formatted as a list of objects with `"claim_code"` and `"raw_label_statement"`, the mapper extracts them.
     - **Default Fallback**: If neither Source A nor Source B provides declared claims, the mapper sets `declared_claims = []`.
   - When `declared_claims` is empty, `claims_engine.evaluate_claims` will cleanly evaluate zero on-pack claims, returning an `EngineBatchResult` with an empty `results` list and zero counts. This is completely safe, valid, and deterministic.

---

## 7. Complete Exact DTO Field Specifications & Mapper Responsibilities

### 7.1 `ProductEvaluationInput`
- **Location**: `backend/app/domain/engines/contracts.py`

| Field Name | Type | Default | Required? | Nullable? | Mapper Responsibility & Source Column |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `product_id` | `Optional[str]` | `None` | No | **Yes** | `str(product.id)` if `product.id` else `None` |
| `product_name` | `str` | *None* | **Yes** | No | `str(product.product_name)` (Must not be empty) |
| `brand_name` | `Optional[str]` | `None` | No | **Yes** | `product.brand_name` |
| `food_form` | `FoodForm` | *None* | **Yes** | No | `FoodForm(product.food_form.lower())` |
| `food_category` | `Optional[str]` | `None` | No | **Yes** | `product.food_category` |
| `package_size` | `Optional[str]` | `None` | No | **Yes** | `product.package_size` |
| `serving_size_value` | `Optional[Decimal]` | `None` | No | **Yes** | `Decimal(str(product.serving_size_value))` if not None else `None` |
| `serving_size_unit` | `str` | `"g"` | No | No | `product.serving_size_unit or "g"` |
| `nutrients` | `Dict[str, NutrientObservationInput]` | `Field(default_factory=dict)` | No | No | Eager-loaded `product.nutrients` mapped by `nutrient_code` (see §7.2) |
| `ingredients` | `List[IngredientObservationInput]` | `Field(default_factory=list)` | No | No | Eager-loaded `product.ingredients` ordered by `sequence_order` (see §7.3) |
| `declared_claims` | `List[DeclaredClaimInput]` | `Field(default_factory=list)` | No | No | Ingested via API request body or verified payload key (see §6.2) |
| `data_source_id` | `Optional[str]` | `None` | No | **Yes** | `product.source_id` |

### 7.2 `NutrientObservationInput`
| Field Name | Type | Default | Required? | Nullable? | Mapper Responsibility & Source Column |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `nutrient_code` | `str` | *None* | **Yes** | No | `pn.nutrient_code` |
| `measurement_basis` | `MeasurementBasis` | `MeasurementBasis.PER_100G` | No | No | Determined per §3.3 (strictly `PER_100G` or `PER_100ML`) |
| `per_100g_value` | `Optional[Decimal]` | `None` | No | **Yes** | `Decimal(str(pn.per_100g_value))` if `pn.per_100g_value is not None` else `None` |
| `per_serving_value` | `Optional[Decimal]` | `None` | No | **Yes** | `Decimal(str(pn.per_serving_value))` if `pn.per_serving_value is not None` else `None` |
| `unit` | `str` | *None* | **Yes** | No | `pn.unit` (e.g. `'g'`, `'mg'`, `'kcal'`) |
| `data_status` | `NutrientDataStatus` | *None* | **Yes** | No | `NutrientDataStatus(pn.data_status)`. Never map `NOT_DECLARED` to `0.0`. |

#### Mandatory Nutrients Fallback Rule:
For any of the 9 FSSAI mandatory nutrients (`energy`, `protein`, `carbohydrates`, `total_sugars`, `added_sugars`, `total_fat`, `saturated_fat`, `trans_fat`, `sodium`) absent from `product.nutrients`:
The mapper must insert a stub observation:
```python
NutrientObservationInput(
    nutrient_code=missing_code,
    measurement_basis=determined_basis,
    per_100g_value=None,
    per_serving_value=None,
    unit=FSSAI_STANDARD_UNITS[missing_code],
    data_status=NutrientDataStatus.NOT_DECLARED
)
```

### 7.3 `IngredientObservationInput`
| Field Name | Type | Default | Required? | Nullable? | Mapper Responsibility & Source Column |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `ingredient_code` | `str` | *None* | **Yes** | No | `pi.ingredient_code` |
| `declared_label_text` | `str` | *None* | **Yes** | No | `pi.declared_label_text or pi.ingredient.canonical_name` |
| `sequence_order` | `int` | *None* | **Yes** | No | `pi.sequence_order` (1-based ascending weight order) |
| `declared_percentage` | `Optional[Decimal]` | `None` | No | **Yes** | `Decimal(str(pi.declared_percentage))` if not None else `None` |
| `ins_number` | `Optional[str]` | `None` | No | **Yes** | `pi.ingredient.ins_number` if relationship loaded else `None` |
| `is_fssai_major_allergen` | `bool` | `False` | No | No | `pi.ingredient.is_fssai_major_allergen` or `pi.is_allergen_declared` |
| `processing_classification` | `IngredientProcessingClass` | `UNKNOWN` | No | No | `IngredientProcessingClass(pi.ingredient.processing_classification)` if available else `UNKNOWN` |
| `sugar_classification` | `IngredientSugarClass` | `UNKNOWN` | No | No | `IngredientSugarClass(pi.ingredient.sugar_classification)` if available else `UNKNOWN` |
| `classification_evidence` | `Optional[str]` | `None` | No | **Yes** | `pi.ingredient.classification_evidence` if available else `None` |

---

## 8. Unresolved Questions Submitted to Tejas

Instead of making unverified assumptions, the following open questions are submitted for Tejas's review:

1. **Declared Claims Input Channel**:
   - Since the database has no `product_claims` table, does Tejas plan to:
     - **Option 1**: Accept declared claims exclusively via the API request body when calling the evaluation endpoint (e.g. `POST /api/v1/products/{id}/evaluate` with `{ "declared_claims": [...] }`)?
     - **Option 2**: Ingest and persist declared claims inside `Product.raw_source_payload["declared_claims"]` during product creation/OCR?
     - **Option 3**: Add a dedicated `product_claims` table in a future migration?
2. **Measurement Basis Resolution for Ambiguous Liquids**:
   - For liquid products where `serving_size_unit` is not declared or missing, what is Tejas's preferred fallback in the mapper:
     - Assume `MeasurementBasis.PER_100ML` by default for all `food_form == LIQUID` unless `package_size` explicitly contains `"g"` / `"kg"`?
     - Or flag a `DataQualityNotice` whenever liquid density cannot be verified from the unit?
3. **Evaluation Rules Caching vs Database Lookup**:
   - Does Tejas prefer:
     - **Option A (In-memory singleton)**: `EvaluationRulesBundle` pre-loaded once at FastAPI startup from verified seed data or initial DB query (maximum performance, zero per-request DB queries for static rules)?
     - **Option B (Repository-backed)**: A `RuleRepository` querying `regulatory_claim_rules`, `icmr_threshold_rules`, and `icmr_matrix_rules` per evaluation request (supports dynamic rule updates in database without restarting the server)?
