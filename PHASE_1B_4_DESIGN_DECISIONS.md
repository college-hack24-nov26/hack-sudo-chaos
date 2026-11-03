# YumSure — Phase 1B.4: Design Decisions & Tejas Collaboration Interface

**Document Version**: 1.0.0  
**Status**: ARCHITECTURAL AGREEMENT DOCUMENT  
**Author**: Senior Backend Architect & Nutrition Regulatory Intelligence Lead  
**Recipient / Collaborator**: Tejas (Backend Foundation Lead)  
**Governing Documents**:
- `ENGINE_CONTRACTS.md` (v1.0.0)
- `RULE_SEED_DATA_SCHEMA.md` (v1.0.0)
- `ENGINE_SAMPLE_CASES.md` (v1.0.0)
- `REGULATORY_PROVENANCE_AND_AMBIGUITIES.md` (v1.0.0)

---

## 1. Division of Responsibilities Ledger

To accelerate delivery and guarantee clean separation of concerns, the technical responsibilities between the **Nutrition & Regulatory Intelligence Lead (Abhishek)** and the **Backend Foundation Lead (Tejas)** are codified below:

```mermaid
flowchart LR
    subgraph Abhishek_Domain ["Abhishek: Regulatory & Nutrition Intelligence"]
        R1[Regulatory Research & Audits]
        R2[Source-Verified Seed Datasets]
        R3[Deterministic Evaluation Engines]
        R4[Pydantic Contract DTOs]
        R5[Engine Unit & Fuzz Tests]
    end

    subgraph Tejas_Domain ["Tejas: Backend Core & Data Pipelines"]
        T1[PostgreSQL 18 & Alembic Migrations]
        T2[SQLAlchemy Repositories]
        T3[Open Food Facts Ingestion]
        T4[FastAPI Routers & Endpoints]
        T5[Telemetry, Caching & Auth]
    end

    Abhishek_Domain ==>|Pure DTOs & Rule Seeds| Interface["Boundary: Engine Contracts & DTO Mappers"]
    Interface ==>|Batch Evaluation Calls| Tejas_Domain
```

| Component | Owner | Deliverables | Verification Strategy |
| :--- | :---: | :--- | :--- |
| **Domain Models & DDL** | **Tejas** | PostgreSQL tables, Alembic migrations, database connection pooling. | Alembic live migration execution (`upgrade head`). |
| **Nutrition Intelligence** | **Abhishek** | Pure deterministic engines (`nutrition_engine.py`, `claims_engine.py`, `icmr_hfss_engine.py`, `ingredient_engine.py`). | 100% offline unit tests against edge-case fixtures. |
| **Rule Seeds** | **Abhishek** | Five verified seed JSON files (`icmr_table_15_1`, `icmr_table_15_2`, `fssai_claims`, `fssai_synonyms`, `ingredient_rules`). | Provenance verification against FSSAI gazettes and ICMR 2024 PDF. |
| **Data Ingestion** | **Tejas** | Open Food Facts API v3 client, barcode lookup, normalization pipeline. | Integration tests against live barcode scans. |
| **API Endpoints** | **Tejas** | FastAPI routers (`/api/v1/products/{barcode}/evaluate`, `/claims`, `/hfss`). | Pytest HTTP client tests. |

---

## 2. Seven Core Architectural Design Decisions

### Decision 1: Pure Function Architecture with Zero Side-Effects
- **Rationale**: Engines are implemented as pure, deterministic Python functions. They take `ProductEvaluationInput` and rule lists as arguments and return `EngineBatchResult`.
- **Benefit**: Engines have zero database sessions, no network calls, and no threading locks. They can be unit-tested in milliseconds without setting up test databases or mock HTTP servers.

### Decision 2: Prohibition of Aggregated Health Scores
- **Rationale**: Some commercial apps generate an arbitrary "score out of 100" or single "red/amber/green" rating. Indian statutory law under the Food Safety and Standards Act contains **no legal definition of an overall health score**.
- **Decision**: YumSure strictly rejects composite scoring. An ultra-processed snack with low sugar or high protein must report its claims and its UPF status independently. Consumers and health professionals receive factual, granular evaluation breakdowns.

### Decision 3: Preservation of Four-State Nutrient Semantics
- **Rationale**: A missing nutrient declaration on an Indian label is legally and medically different from zero. Converting missing values to zero leads to false-negative alerts (e.g. assuming trans fat is zero when it was simply omitted).
- **Decision**: Tejas's `data_status IN ('PRESENT', 'EXPLICITLY_ZERO', 'NOT_DECLARED', 'UNKNOWN')` is preserved end-to-end through the DTO layers into engine calculations.

### Decision 4: Standardized Five Evaluation Outcomes
- **Rationale**: Binary `True/False` or `PASS/FAIL` cannot represent real-world regulatory compliance where mandatory facts are missing or guidelines do not apply.
- **Decision**: Every rule yields:
  - `PASS`: Condition conclusively satisfied.
  - `FAIL`: Condition conclusively breached.
  - `INSUFFICIENT_DATA`: Mandatory declaration missing.
  - `INDETERMINATE`: Ambiguous scientific evidence (e.g. recipe audit needed).
  - `NOT_APPLICABLE`: Out of scope (e.g. liquid beverage on solid-only matrix).

### Decision 5: Dedicated AST for FSSAI Schedule I Claims
- **Rationale**: FSSAI claims require complex boolean combinations: multi-base OR alternatives (e.g. Protein $\ge 5.4\text{g/100g}$ OR $\ge 2.7\text{g/100ml}$ OR $\ge 2.7\text{g/100 kcal}$) and secondary percentage-of-energy AND conditions (e.g. Trans Fat Free requiring $< 0.2\text{g}$ AND sat fat $\le 1.5\text{g}$ AND sat fat $\le 10\%$ energy).
- **Decision**: Stored as validated `condition_expression JSONB` using Pydantic `ClaimConditionGroup` with allowlisted operators (`LT`, `LTE`, `GT`, `GTE`, `EQ`) and maximum depth $\le 5$. Python `eval()` is strictly forbidden.

### Decision 6: Decoupling of Table 15.1 and Table 15.2
- **Rationale**: Table 15.1 contains product-level nutrient cutoffs; Table 15.2 contains a $3 \times 3$ matrix of food processing groups and calorific tiers. Binding Table 15.2 to a nutrient foreign key made the matrix unmodelable.
- **Decision**: Decoupled into `IcmrNutrientThresholdRule` (Table 15.1) and `IcmrMatrixRule` (Table 15.2). Table 15.2 has zero nutrient foreign keys and models UPF and HFSS as independent dimensions (Cell C1 = Non-HFSS UPF).

### Decision 7: Evidence-Based Ingredient Classification
- **Rationale**: Naive boolean flags falsely classify natural foods with single functional additives as UPF.
- **Decision**: Extended `Ingredient` with `processing_classification` and `sugar_classification`, defaulting strictly to `'UNKNOWN'`. Uncharacterized ingredients are never assumed to be additives.

---

## 3. Interface Agreements Submitted to Tejas for Sign-Off

We submit the following five implementation questions to Tejas for agreement before starting engine code implementation:

### Item 1: DTO Mapper Location in Backend
- **Question**: Should the DTO mapper converting SQLAlchemy ORM models (`Product`, `ProductNutrient`, `ProductIngredient`) into `ProductEvaluationInput` live in:
  - *Option A*: `backend/app/mappers/product_mapper.py` (Domain-driven approach)?
  - *Option B*: Inside the repository layer `backend/app/repositories/product_repository.py`?
  - *Architecture Recommendation*: Option A keeps repositories focused on SQL queries and provides a dedicated, testable mapping layer.

### Item 2: Seed Data Loading Strategy
- **Question**: How should the five seed JSON datasets be loaded in production?
  - *Option A*: Python CLI seeder script `backend/app/db/seeds/seed_regulatory_rules.py` executed once during deployment?
  - *Option B*: Alembic data migrations?
  - *Architecture Recommendation*: Option A. Data seeding should be decoupled from schema DDL migrations to allow independent updating of regulatory rules when FSSAI publishes gazette amendments.

### Item 3: Engine Module Placement
- **Proposal**: Place deterministic evaluation engines in `backend/app/engines/`:
  - `backend/app/engines/nutrition_engine.py`
  - `backend/app/engines/claims_engine.py`
  - `backend/app/engines/icmr_hfss_engine.py`
  - `backend/app/engines/ingredient_engine.py`
  - `backend/app/engines/contracts.py` (Pure DTOs from `ENGINE_CONTRACTS.md`)
  Does Tejas concur with this directory structure?

### Item 4: Liquid per-100ml Value Convention in `ProductNutrient`
- **Confirmation**: We confirmed that in PostgreSQL, column `per_100g_value` stores values for both solids (per 100g) and liquids (per 100ml) to avoid schema churn. The mapper will assign `per_100g_value` directly into `NutrientObservationInput.per_100g_value`, with `product.food_form` indicating liquid context. Does Tejas concur?

### Item 5: Caching of Engine Results
- **Proposal**: In `ai_explanations` / response cache, store the serialized `EngineBatchResult` JSON. If a product's barcode data has not changed (`updated_at` unchanged), return cached evaluation results to minimize server compute. Does Tejas concur?

---

## 4. Next Phase Readiness

All specifications, contracts, seed schemas, sample cases, and design rationale are now documented and saved:
- [`ENGINE_CONTRACTS.md`](file:///d:/Hackthon/hack-sudo-chaos/ENGINE_CONTRACTS.md)
- [`RULE_SEED_DATA_SCHEMA.md`](file:///d:/Hackthon/hack-sudo-chaos/RULE_SEED_DATA_SCHEMA.md)
- [`ENGINE_SAMPLE_CASES.md`](file:///d:/Hackthon/hack-sudo-chaos/ENGINE_SAMPLE_CASES.md)
- [`REGULATORY_PROVENANCE_AND_AMBIGUITIES.md`](file:///d:/Hackthon/hack-sudo-chaos/REGULATORY_PROVENANCE_AND_AMBIGUITIES.md)
- [`PHASE_1B_4_DESIGN_DECISIONS.md`](file:///d:/Hackthon/hack-sudo-chaos/PHASE_1B_4_DESIGN_DECISIONS.md)

Awaiting Tejas's review and sign-off on the interface agreements before implementing engine modules.

