# YumSure — Project Architecture & System Design

This document details the complete end-to-end architecture, information flow, component interaction patterns, and failure mode design for YumSure.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Client["Flutter Android Application"]
        UI[User Interface & Barcode Scanner]
        State[State Management / Bloc / Provider]
        ApiClient[YumSure HTTP Client]
        UI --> State
        State --> ApiClient
    end

    subgraph BackendGateway["FastAPI Gateway & Core"]
        FastAPI[FastAPI Application Instance]
        AuthSec[Security & Request Middleware]
        Router[API v1 Routers]
        FastAPI --> AuthSec --> Router
    end

    subgraph DeterministicEngines["Deterministic Evaluation Core"]
        NutriEngine[Nutritional Interpretation Engine\n(ICMR-NIN 2020 RDA)]
        ClaimsEngine[FSSAI Claims Engine\n(Advertising & Claims Regs 2018)]
        IngredEngine[Ingredient & Allergen Engine\n(FSSAI Labelling 2020)]
    end

    subgraph ExternalServices["External APIs & AI Layer"]
        OFF[Open Food Facts API v3\n(Product-Opener ODbL)]
        AIProvider[xAI Grok / NVIDIA NIM API\n(Text-Only LLM)]
        AIFallback[Local Deterministic Explainer Fallback]
    end

    subgraph Persistence["Storage & Caching Layer"]
        PG[(PostgreSQL 18 Normalized DB)]
        SchemaProd[Products & Ingredients]
        SchemaNutri[Nutrient Values & Reference Rules]
        SchemaClaims[Statutory Claim Thresholds]
        SchemaAudit[Audit & AI Generation Logs]
        PG --> SchemaProd
        PG --> SchemaNutri
        PG --> SchemaClaims
        PG --> SchemaAudit
    end

    ApiClient -->|HTTP JSON /api/v1| FastAPI
    Router -->|1. Check Existing| PG
    Router -->|2. If Absent, Fetch| OFF
    Router -->|3. Feed Normalized Data| DeterministicEngines
    NutriEngine -->|Rule Evaluation| Router
    ClaimsEngine -->|Rule Evaluation| Router
    IngredEngine -->|Rule Evaluation| Router
    Router -->|4. Persist Product & Evaluation| PG
    Router -->|5. Synthesize Explanation| AIProvider
    AIProvider -.->|Fallback on error/timeout| AIFallback
    AIFallback --> Router
    Router -->|6. Return Unified Intelligence| ApiClient
```

---

## 2. End-to-End Barcode Lookup & Processing Flow

When a user scans a packaged product barcode (EAN-13, UPC-A, etc.), the processing lifecycle follows a rigorous deterministic pipeline:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant App as Flutter Mobile App
    participant API as FastAPI Backend
    participant DB as PostgreSQL 18
    participant OFF as Open Food Facts v3
    participant Engine as Deterministic Engines
    participant AI as AI Explainer Service

    User->>App: Scan or Enter Barcode
    App->>API: GET /api/v1/products/{barcode}
    API->>DB: Query product by barcode
    alt Product exists in DB and is VERIFIED
        DB-->>API: Return existing normalized record
    else Product missing or unverified
        API->>OFF: GET /api/v3/product/{barcode}.json
        alt Product found in OFF
            OFF-->>API: 200 OK (Raw OFF v3 JSON)
            API->>API: Validate schema & Normalize units (per 100g/ml)
            API->>DB: Insert Product & raw payload (Provenance: OFF_API_V3)
        else Product not found in OFF
            OFF-->>API: 404 Not Found
            API-->>App: 404 (Product unknown; prompt manual upload)
        end
    end
    API->>Engine: Run Nutritional Interpretation (ICMR-NIN)
    API->>Engine: Run Claims Validation (FSSAI 2018)
    API->>Engine: Run Ingredient & Allergen Parser (FSSAI 2020)
    Engine-->>API: Structured Evaluation Results
    opt User requests AI explanation or detailed synthesis
        API->>AI: Synthesize plain English summary (Pass evaluation only)
        alt LLM call succeeds
            AI-->>API: Plain-English contextual summary
        else LLM call fails / throttled / offline
            API->>API: Invoke Rule-Based Local Template Explainer
        end
    end
    API->>DB: Update/Record Scan History & Explanation Cache
    API-->>App: Complete Product Intelligence Response
    App-->>User: Render Nutrient Cards, Claims Badges, Allergen Warnings
```

---

## 3. Component Architecture

### 3.1 Backend Application (`FastAPI`)
- **Framework Choice**: FastAPI provides native Python 3.12+ async support, automatic OpenAPI/Swagger schema validation via Pydantic v2, and high request throughput.
- **Layered Structure**:
  - `app/api/v1/`: Endpoint routing, path parameter validation, response serialization.
  - `app/core/`: Configuration (`pydantic-settings`), environment secrets, logging, security headers.
  - `app/db/`: Async SQLAlchemy 2.0 session factory, database connection lifecycle.
  - `app/models/`: Declarative relational tables with foreign keys and index constraints.
  - `app/schemas/`: Pydantic input/output contracts maintaining strict data types.
  - `app/services/`:
    - `nutrition_engine.py`: Encapsulates ICMR-NIN RDA thresholds per 100g/100ml.
    - `claims_engine.py`: Encapsulates FSSAI Schedule II claims validation.
    - `ingredient_engine.py`: Performs lexical parsing, additive mapping (INS numbers), and allergen detection.
    - `openfoodfacts.py`: HTTPX client with custom User-Agent, timeouts (5s), and retry limits.
    - `ai_explainer.py`: Abstract LLM interface supporting Grok (xAI) and NVIDIA NIM text endpoints with deterministic fallback.

### 3.2 Mobile Client (`Flutter / Android`)
- **Design Philosophy**: Minimalistic, high-legibility interface designed for grocery store lighting and quick glance decisions.
- **Subsystems**:
  - `Barcode Scanner`: Mobile scanner widget utilizing camera feed to decode EAN-13, EAN-8, UPC-A. Includes manual barcode entry fallback.
  - `Nutrition Card View`: Color-coded nutrient indicators (Green: Positive/Low-concern, Amber: Moderate, Red: High-concern for negative nutrients like Sodium, Added Sugar, Saturated Fat).
  - `Claims Verification Banner`: Visual badges for verified manufacturer claims (e.g., green checkmark for valid "High Fibre", red warning for invalid claims).
  - `Ingredient & Allergen Drawer`: Highlights critical allergens in bold warning badges, groups ingredients into functional categories (sweeteners, preservatives, emulsifiers).
  - `AI Vernacular Assistant`: "Explain in simple terms" sheet that displays plain English explanations synthesized from deterministic results.

### 3.3 Database (`PostgreSQL 18`)
- **ACID Integrity**: Foreign keys ensure product nutrient values and ingredient mappings cannot be orphaned.
- **Provenance Logging**: Every record stores `source_type` (`OFF_API_V3`, `USER_CONTRIBUTED`, `FSSAI_OFFICIAL`, `KAGGLE_VERIFIED`), `source_url`, and `retrieval_date`.
- **Verified Record Protection**: An update trigger prevents automated external scrapers from overwriting rows marked `is_verified = TRUE`.

---

## 4. Resilience & Operational Security

1. **AI Safety Firewall**:
   - The AI service is strictly downstream of the deterministic engines.
   - The prompt contains only pre-computed facts: `"{ 'protein_classification': 'High', 'fssai_claim_high_protein': 'VALID', 'allergens': ['Milk'] }"`.
   - The system prompt forbids the AI from emitting medical diagnoses, recommending treatments, or asserting factual numbers not present in the input.
2. **Deterministic Fallback Engine**:
   - If Grok or NVIDIA NIM APIs are unreachable (HTTP 429, 500, network loss), YumSure automatically assembles a pre-compiled textual template:
     `"This product contains [X]g of protein, qualifying as a Source of Protein under FSSAI rules. It contains [Y]g of added sugar, which is classified as High. Contains declared allergen: [Milk]."`
3. **Open Food Facts Rate-Limiting**:
   - Open Food Facts requests are throttled and include the required custom User-Agent: `YumSure-App/1.0 (contact: support@yumsure.in)`.
   - Cached products in PostgreSQL bypass external calls entirely.

