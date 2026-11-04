# YumSure — Individual Technical Contribution Report: Abhishek Mahadik

**Author:** Abhishek Mahadik (`abhimahadik30` / `mahadikabhishek030@gmail.com`)  
**Project:** YumSure (Regulation-Backed Packaged Food Nutrition Intelligence)  
**Role:** Domain Architecture, Deterministic Evaluation Engines & Regulatory Data Integrity Lead  
**Branch Context:** `develop` & `feature/evaluation-coordinator`  
**Repository Working Status:** Clean (`d0bbc9a` / `7d126f6`)  
**Verification Date:** November 4, 2026  

---

## 1. Executive Summary: Abhishek's Role in Simple Language

### What Was Abhishek's Role in YumSure?
In YumSure, **Abhishek was the Core Domain Architect and Regulatory Evaluation Lead**. 

While teammate **Tejas** built the database repositories, FastAPI endpoints, and external Open Food Facts client, and teammate **Ubaid** built the Flutter mobile user interface, **Abhishek personally designed and built the "brain" and "clinical/regulatory engine" of YumSure**:

1. **The Four Deterministic Evaluation Engines**: The mathematical and rule-based code that inspects food data against Indian statutory laws (FSSAI) and medical nutrition guidelines (ICMR-NIN).
2. **The Evaluation Coordinator**: The framework-independent master controller that safely orchestrates all four engines in parallel with zero-crash fault isolation and zero arbitrary health scores.
3. **The Regulatory Seed Database & AST Compiler**: Standardized Indian statutory datasets (FSSAI Schedules I & II, ICMR-NIN Tables 15.1 & 15.2, additive limits, mandatory allergen warnings) and an Abstract Syntax Tree (AST) parser to verify complex multi-condition marketing claims.
4. **Nutrition Data Integrity & Measurement-Basis Engine**: The mathematical algorithms and guardrails that prevent false health claims, eliminate dangerous fallbacks (e.g. displaying per-100g numbers on per-serving views), and enforce strict dimensional physics (distinguishing grams from millilitres).

### What Specific Problem Was Abhishek Trying to Solve?
Every day, packaged foods in India display misleading marketing claims like *"High Fibre"*, *"Zero Sugar"*, or *"Immunity Booster"*. Generic health apps either:
- Rely on Western standards (US FDA or European Nutri-Score) that do not fit Indian dietary realities (e.g. maida, palmolein, Indian RDAs).
- Invent arbitrary composite "health scores" (e.g. 72/100 or green stars) that are legally indefensible and conceal high sodium or trans fats behind high protein.
- Let Generative AI / LLMs "guess" or calculate compliance, which produces statistical hallucinations and dangerous medical errors.

Abhishek solved this by engineering a **100% deterministic, regulation-backed evaluation core** where:
- No LLM ever calculates numbers or legal compliance.
- Every verdict cites the exact statutory Gazette clause.
- Missing data is never silently assumed to be zero.
- Physics and units (solid vs. liquid, per 100g vs. per serving) are mathematically guaranteed.

---

## 2. Team Ownership Boundaries: What Abhishek Owned vs. Teammates

To maintain complete academic and engineering integrity for hackathon judges, here is the exact division of responsibilities verified against the repository Git commit history:

```mermaid
flowchart TD
    subgraph Abhishek["Abhishek Mahadik (Domain Engine & Clinical Core)"]
        A1["Four Deterministic Regulatory Engines<br/>(Nutrition, ICMR HFSS, Claims, Ingredients)"]
        A2["EvaluationCoordinator Orchestrator"]
        A3["Domain DTO Contracts & Rules Bundle"]
        A4["Statutory Rule Seeds & AST Schema"]
        A5["Measurement Basis & Data Integrity Architecture"]
        A6["Engine Unit & Integration Test Suites<br/>(114 passing tests)"]
    end

    subgraph Tejas["Tejas Devgharkar (Backend & Infrastructure)"]
        T1["PostgreSQL Models & Alembic Migrations"]
        T2["SQLAlchemy 3NF Repositories"]
        T3["ProductService Application Layer"]
        T4["Open Food Facts API Client & Caching"]
        T5["FastAPI v1 REST Endpoints & Routers"]
    end

    subgraph Ubaid["Ubaid Jasnaik (Mobile & Design Experience)"]
        U1["Flutter UI Screens (Scanner, Search, Details)"]
        U2["State Management Providers"]
        U3["Design System & Theme Tokens"]
        U4["Hackathon Presentation Guide"]
    end

    Abhishek -->|"Pure Domain DTOs"| Tejas
    Tejas -->|"JSON REST API"| Ubaid
```

| Area | Primary Owner | Abhishek's Exact Boundary | Evidence / Commits |
| :--- | :---: | :--- | :--- |
| **Deterministic Engines** | **Abhishek** | 100% owned, designed, and implemented all 4 engines from scratch. | `ca1d803`, `5e1cd57` |
| **Evaluation Coordinator** | **Abhishek** | 100% owned, designed, and implemented framework-independent orchestrator. | `781151c`, `5e1cd57` |
| **Statutory Rule Seeds** | **Abhishek** | Researched, structured, and compiled all 7 canonical FSSAI/ICMR JSON seed datasets. | `ca1d803`, `fe6fa6d` |
| **Domain Contracts (DTOs)** | **Abhishek** | Designed `contracts.py` and `PHASE_3_DOMAIN_DTO_CONTRACT.md`. | `781151c`, `5e1cd57` |
| **Data Integrity & Conversions** | **Abhishek** | Audited data pipeline, fixed serving conversions, added Atwater checks. | `7d126f6` |
| **Database Repositories** | Tejas | Abhishek designed the contracts; Tejas implemented repository logic. | `acbead3`, `f8924ff` |
| **FastAPI REST Endpoints** | Tejas | Abhishek provided the payload adapter schemas; Tejas implemented route handlers. | `3f1603b`, `217bc2a` |
| **Flutter Mobile UI** | Ubaid | Abhishek diagnosed and patched model/widget unit calculation bugs; Ubaid built screens. | `dfafaee`, `7d126f6` |

---

## 3. Chronological Breakdown of Abhishek's Contributions

| # | Work / Milestone | Problem Addressed | What Abhishek Personally Did | Technology Used | Current Status | Commit / Git Evidence |
| :-: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | **Regulatory Research & Database Models** | FSSAI 2018/2020 regulations and ICMR 2020 guidelines lacked relational schemas. | Researched regulations, authored 8 architectural audit reports, and designed ORM schemas for claim ASTs, ICMR thresholds, and ingredient rules. | Python, SQLAlchemy, Markdown, Statutory Gazettes | **Completed** | Commit `bf3dab8` |
| **2** | **Alembic Database Seed Datasets** | Engines need verified rule tables for 54+ statutory parameters. | Compiled 7 canonical JSON seed files covering FSSAI Schedule I/II, ICMR Tables 15.1/15.2, additives, and allergen warnings. | JSON, Alembic, PostgreSQL | **Completed** | Commit `ca1d803` |
| **3** | **Phase 2: Four Deterministic Engines** | GenAI cannot be trusted to evaluate food laws; requires pure deterministic execution. | Authored `nutrition_engine.py`, `icmr_hfss_engine.py`, `claims_engine.py`, and `ingredient_engine.py`. | Python 3.14, Decimal, AST Evaluator, RegEx | **Completed** | Commit `ca1d803` |
| **4** | **Engine Unit Test Suite** | Engine logic must be mathematically and legally provable across edge cases. | Wrote comprehensive test suite with 17 scenarios covering AST depth limits, missing nutrients, and additive warnings. | Python `unittest` | **Completed** | Commit `ca1d803` (`test_engines.py`) |
| **5** | **FSSAI Schedule II Synonym Fixes** | Commercial liquid drinks use synonyms like "Zero Trans Fat" that need AST expansion. | Corrected Schedule II authorized synonym registry and added liquid trans-fat-free AST rules. | Python, JSON | **Completed** | Commit `fe6fa6d` |
| **6** | **Phase 3: Domain DTOs & Evaluation Coordinator** | Four separate engines needed a unified, isolated orchestrator that never crashes the app. | Implemented `EvaluationCoordinator`, pure domain DTOs, and rules bundle with runner-mocking capability. | Python, Pydantic v2, Dataclasses | **Completed** | Commit `781151c` (`coordinator.py`) |
| **7** | **Coordinator Integration Tests** | Multi-engine execution must guarantee fault isolation, immutability, and score prohibition. | Wrote 14 integration test scenarios verifying engine crash isolation, empty inputs, and absence of composite health scores. | Python `unittest`, Mock | **Completed** | Commit `781151c` (`test_evaluation_integration.py`) |
| **8** | **Measurement Basis Integration** | Silently mixing per-100g and per-serving numbers causes false legal passes. | Refactored all 4 engines to enforce explicit `MeasurementBasis` (`PER_100G`, `PER_100ML`, `PER_SERVING`), rejecting unresolved bases. | Python, Enums, Decimal | **Completed** | Commit `5e1cd57` on `feature/evaluation-coordinator` |
| **9** | **Curated Packaging Catalog Calibration** | Missing local DB or OFF API offline would break live demonstration. | Calibrated 5 real Indian packaged foods (`curated_catalog.py`) with all 10 canonical nutrients and serving values. | Python, Domain DTOs | **Completed** | Commit `7d126f6` |
| **10** | **Nutrition Data Integrity Remediation** | Britannia Nutri-Choice biscuits had missing carbs, false per-serving fallbacks, and scale bar bugs. | Diagnosed full pipeline, restored packaging carbs (68g), fixed bidirectional conversions, and patched Flutter widgets. | Python, Dart, Flutter, Regex | **Completed** | Commit `7d126f6` |
| **11** | **Data Consistency & Atwater Energy Engine** | Impossible manufacturer declarations (e.g. added sugar > total sugar) pass unnoticed. | Implemented `validate_nutrient_consistency` checking negative quantities, fat/sugar hierarchies, and Atwater energy sum plausibility. | Python, Decimal | **Completed** | Commit `7d126f6` |
| **12** | **Technical Review & Handover Package** | Needed clean architectural documentation and proof for Tejas before merging shared files. | Created comprehensive review package with untruncated diffs, test reconciliation, and barcode provenance evidence. | Markdown, Git | **Completed** | Commit `7d126f6` (`TEJAS_REVIEW_PACKAGE.md`) |

---

## 4. In-Depth Explanation of Major Technical Contributions

### A. The Four Deterministic Evaluation Engines
*Files:* [`backend/app/domain/engines/`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/engines/) (`nutrition_engine.py`, `icmr_hfss_engine.py`, `claims_engine.py`, `ingredient_engine.py`)

#### 1. What problem existed?
If you ask an LLM: *"Does this biscuit qualify for a 'High Fibre' claim under FSSAI?"*, the LLM will hallucinate. It might confuse Indian FSSAI laws with US FDA laws, or fail to check whether the product secretly breaches saturated fat limits.

#### 2. What approach did Abhishek take?
Abhishek authored four **pure mathematical engines** in Python with zero external API dependencies:
1. **NutritionEngine**: Calculates `% Daily Value` (% DV) against ICMR-NIN 2020 Recommended Dietary Allowances (RDA) for adult sedentary males ($2,000\text{ kcal}$, $54\text{g}$ protein, $2,000\text{mg}$ sodium, etc.). Checks for mandatory statutory nutrient declarations.
2. **ClaimsEngine**: Evaluates voluntary marketing claims (e.g. *"Low Fat"*, *"Trans Fat Free"*) against FSSAI (Advertising and Claims) Regulations, 2018 Schedule I. Uses an Abstract Syntax Tree (AST) evaluator with compound boolean logic (`AND`, `OR`, `NOT`) bounded to a maximum recursion depth of 5 to prevent stack overflow.
3. **ICMRHFSSEngine**: Implements the Indian Council of Medical Research (ICMR-NIN) 2024 Dietary Guidelines:
   - **Table 15.1 Thresholds**: Flags products high in fat, sugar, or sodium (HFSS).
   - **Table 15.2 Processing-Nutrient Matrix**: Maps solid foods into a 9-cell matrix (Rows: NOVA Processing Classes 1–3; Columns: Nutrient Density Classes 1–3) to evaluate Ultra-Processed Food (UPF) status independently from nutrient thresholds.
4. **IngredientEngine**: Inspects food additive limits (e.g. Caffeine maximum $300\text{ ppm}$ in carbonated beverages), triggers statutory label warnings (e.g. *"CONTAINS ARTIFICIAL SWEETENER AND FOR CHILDREN: NOT RECOMMENDED"* for Aspartame INS 951), and alerts consumers to uncharacterized cosmetic additives.

#### 3. How does the AST evaluator work? (Simple Example)
To claim *"Trans Fat Free"* in India, FSSAI law requires two simultaneous conditions:
1. Trans fat must be less than $0.2\text{ g}$ per $100\text{ g}$.
2. **AND** Saturated fat must not exceed $6.0\text{ g}$ per $100\text{ g}$ (solid food).

Abhishek's Claims Engine parses this as a tree:
```json
{
  "operator": "AND",
  "conditions": [
    {"field": "trans_fat", "comparator": "LT", "threshold": 0.2, "unit": "g"},
    {"field": "saturated_fat", "comparator": "LTE", "threshold": 6.0, "unit": "g"}
  ]
}
```
If a product has $0.0\text{g}$ trans fat but $10.0\text{g}$ saturated fat, Abhishek's AST returns `FAIL`, preventing illegal marketing claims from deceiving consumers.

---

### B. The Evaluation Coordinator
*File:* [`backend/app/domain/engines/coordinator.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/engines/coordinator.py)

#### 1. What problem existed?
If an application runs four engines in a basic loop, an unexpected bug or null pointer in one engine (e.g. an unreadable OCR ingredient) crashes the entire HTTP request, returning a blank screen or a 500 error to the mobile user.

#### 2. What did Abhishek implement?
Abhishek built a master framework-independent `EvaluationCoordinator` guaranteeing:
1. **Isolated Fault Tolerance**: Each engine runs inside a protected execution boundary. If Engine 2 throws an unexpected exception, Engines 1, 3, and 4 continue running, and the crash is cleanly captured in `engine_failures` without compromising user results.
2. **Zero Composite Health Score**: In alignment with clinical guidelines and Section 2 of `JUDGE_PRESENTATION_GUIDE.md`, Abhishek strictly banned calculating an arbitrary "overall 1-to-100 score" or letter grade, instead aggregating objective counts (`total_rules_evaluated`, `total_passed`, `total_failed`, `total_insufficient_data`).
3. **Immutability**: Neither the product DTO nor the regulatory rules bundle is mutated during evaluation; identical inputs produce byte-for-byte identical results.

---

### C. Strict Missing-Data vs. Explicit-Zero Handling
*Files:* [`contracts.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/engines/contracts.py), [`external_normalizer.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/mappers/external_normalizer.py)

#### 1. What problem existed?
In amateur coding projects, missing nutrient data is commonly defaulted to zero (`val or 0.0`). In nutritional law, **this is fatal**:
- If a manufacturer prints `"Trans Fat: 0g"` on the pack, it is an **Explicit Zero**. The product legally earns a *"Trans Fat Free"* badge.
- If a crowdsourced database entry simply omitted trans fat because the contributor forgot to type it, the value is **Missing (`None`)**.
- If missing is converted to zero, the app will falsely tell a consumer that an unmeasured biscuit is completely trans-fat-free!

#### 2. How did Abhishek solve it?
Abhishek introduced a strict four-state regulatory enum:
```python
class NutrientDataStatus(str, Enum):
    PRESENT = "PRESENT"                  # Declared on pack with measured value > 0
    EXPLICITLY_ZERO = "EXPLICITLY_ZERO"  # Declared on pack as exactly 0 / 0.0
    NOT_DECLARED = "NOT_DECLARED"        # Omitted from packaging table
    UNKNOWN = "UNKNOWN"                  # Unreadable OCR or corrupted unit
```
- When trans fat is `EXPLICITLY_ZERO`, claims evaluate to `PASS`.
- When trans fat is `NOT_DECLARED` or `UNKNOWN`, the claim evaluator strictly halts and returns `INSUFFICIENT_DATA`, protecting consumer safety.

---

### D. Explicit Measurement-Basis Architecture (Grams vs. Millilitres)
*Files:* [`icmr_hfss_engine.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/engines/icmr_hfss_engine.py), [`claims_engine.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/engines/claims_engine.py), [`contracts.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/engines/contracts.py)

#### 1. What problem existed?
Indian food laws set completely different thresholds for solids vs liquids:
- FSSAI Low Sugar threshold for **solids**: $\le 5.0\text{g} / 100\text{g}$.
- FSSAI Low Sugar threshold for **liquids**: $\le 2.5\text{g} / 100\text{ml}$.

Furthermore, food packaging frequently declares nutrients "Per Serving" (e.g. 25g), while statutory thresholds are strictly "Per 100g". If an engine compares a 25g serving value (e.g. 3.25g sugar) against a 100g threshold (5.0g), the product falsely passes as "Low Sugar" when it is actually an ultra-high sugar product!

#### 2. What did Abhishek implement?
Abhishek enforced explicit `MeasurementBasis` enums across all observations:
```python
class MeasurementBasis(str, Enum):
    PER_100G = "PER_100G"
    PER_100ML = "PER_100ML"
    PER_SERVING = "PER_SERVING"
```
1. **No Silent Inference**: An engine never guesses whether a product is measured in grams or millilitres based solely on whether it is marked "liquid" or "solid".
2. **Strict Incompatibility Rejection**: If an engine rule expects `PER_100ML` but the observation is `PER_100G`, or the basis is unresolved (`None`), the engine rejects the comparison as `INSUFFICIENT_DATA` rather than calculating false verdicts.
3. **Bidirectional Conversion**: Converted per-serving values to per-100g only when a verified serving weight exists and units dimensionally match.

---

### E. Nutrition Data Integrity Remediation & Flutter UI Fixes
*Files:* [`curated_catalog.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/domain/curated_catalog.py), [`frontend_adapter.py`](file:///d:/Hackthon/hack-sudo-chaos/backend/app/schemas/frontend_adapter.py), [`nutrient_row_card.dart`](file:///d:/Hackthon/hack-sudo-chaos/frontend/lib/features/product_details/presentation/widgets/nutrient_row_card.dart)

#### 1. What problem existed?
On the live mobile screen for Britannia Nutri-Choice Digestive Biscuits:
- Carbohydrates displayed as `'—'` (missing).
- When users tapped the "Per serving (25 g)" toggle, the app showed $482\text{ kcal}$ and $14.5\text{ g}$ sugar (the 100g numbers!) because of a flawed fallback: `nutrient.valuePerServing ?? nutrient.valuePer100g`.
- The visual threshold bar plotted the per-serving value against 100g thresholds, placing a "High Sugar" product in the green "Low" zone!

#### 2. How did Abhishek solve it?
1. **Restored Official Packaging Facts**: Verified physical packaging records (`8901063142015` / `8901030383701`) and added declared carbohydrates ($68.0\text{g} / 100\text{g}$, $17.0\text{g} / 25\text{g}$ serving) to `curated_catalog.py`.
2. **Atwater Energy Plausibility Check**: Implemented automated checks comparing declared energy against macronutrient sums:
   $$\text{Energy} \approx (4 \times \text{Protein}) + (9 \times \text{Fat}) + (4 \times \text{Available Carbs}) + (2 \times \text{Fibre})$$
   Proved that Nutri-Choice's $482\text{ kcal}$ matches the macronutrient sum ($480.6\text{ kcal}$) to within $<0.3\%$.
3. **Eliminated Flawed UI Fallbacks**: Removed `?? nutrient.valuePer100g` from `nutrient_row_card.dart`.
4. **Synchronized Threshold Scale Bar**: Added dynamic scale-factor logic in Flutter so that when viewing per serving, scale markers and statutory classification badges ("High") never contradict each other.

---

## 5. Work Completed vs. Pending Integration

| Contribution Item | Implemented by Abhishek | Unit Tested | Application Integration Status | Remaining Work (Next Steps) |
| :--- | :---: | :---: | :--- | :--- |
| **Four Deterministic Engines** | **Yes** | **Yes** (17 engine tests) | Fully integrated into `EvaluationCoordinator`. | None; complete and frozen. |
| **Evaluation Coordinator** | **Yes** | **Yes** (14 integration tests) | Merged into `develop` (`8d13c23`, `f785919`). | None; complete and frozen. |
| **FSSAI / ICMR Rule Seed Datasets** | **Yes** | **Yes** (9 seed tests) | Embedded in `backend/app/data/seeds/`. | None; verified against Gazettes. |
| **Measurement Basis Enforcement** | **Yes** | **Yes** (Regression suite) | Active in all 4 engines. | None; complete. |
| **Curated Demo Packaging Catalog** | **Yes** | **Yes** (12 data integrity tests) | Active fallback in `product_service.py`. | None; calibrated for 5 demo products. |
| **Nutrition Data Integrity Engine** | **Yes** | **Yes** (12 dedicated tests) | Implemented in `frontend_adapter.py`. | Fully implemented; pending Tejas's final sign-off. |
| **Flutter Widget Calculations** | **Yes** | Statically verified | Patched in `nutrient_row_card.dart` & `product_identity_card.dart`. | Live testing on Flutter device/emulator. |
| **FastAPI REST Routes** | No | Yes | Implemented by Tejas (`product_service.py`). | Owned by Tejas. |
| **Database Repositories & Migrations**| No | Yes | Implemented by Tejas (`repositories/`). | Owned by Tejas. |
| **Mobile UI Screens & Scanning** | No | Statically verified | Implemented by Ubaid (`frontend/lib/`). | Owned by Ubaid. |

---

## 6. Abhishek's Contribution to Project Quality

1. **Elimination of Hallucinations**: Replaced probabilistic AI with 100% deterministic, reproducible Python execution for all statutory legal checks.
2. **Defensible Legal Truth**: Every failure returned to the consumer cites the exact Indian Gazette notification (e.g. *"FSSAI (Advertising and Claims) Regulations, 2018 - Schedule II, Entry 4"*), making YumSure clinically and legally defensible.
3. **Medical Safety Safeguards**: Enforcing `EXPLICITLY_ZERO` vs. `NOT_DECLARED` guarantees that missing data never masquerades as zero trans fats or zero added sugars.
4. **Dimensional Physics Protection**: Guarantees that liquid beverages ($100\text{ml}$) and solid snacks ($100\text{g}$) cannot be cross-evaluated against incorrect statutory thresholds.
5. **Massive Test Coverage**: Authored **69 dedicated unit and integration tests** across the engine, coordinator, and data integrity suites, ensuring zero regressions across all 114 executed backend tests.

---

## 7. Hackathon Judge-Ready Explanations

### A. My Role in 20 Seconds
> *"I was the Domain and Regulatory Evaluation Engine Lead for YumSure. I personally designed and built the deterministic evaluation core that verifies food packaging against official FSSAI laws and ICMR-NIN dietary guidelines, ensuring our app delivers legally and clinically provable truth without relying on Generative AI to guess nutrition facts."*

### B. My Contribution in 1 Minute
> *"In YumSure, while Tejas built our backend database infrastructure and Ubaid developed our mobile UI, I was responsible for the evaluation core. I personally engineered our four deterministic engines: the FSSAI Claims Engine with an Abstract Syntax Tree parser, the ICMR-NIN Nutrition Engine with its 9-cell processing matrix, the Ingredient Warning Engine, and the Nutrition Engine.*
>
> *I also built the Evaluation Coordinator that runs all four engines safely with complete crash isolation, and I solved our most difficult data integrity challenge: ensuring that missing nutrients are never converted to zero, distinguishing solid grams from liquid millilitres, and eliminating misleading UI fallbacks. Across this core, I authored 69 unit tests that keep our entire backend 100% verified."*

### C. My Contribution in 3 Minutes (Presentation Script)
> *"Good morning, judges. When a consumer picks up a box of biscuits in a supermarket and reads 'High Fibre' or 'Zero Trans Fat', they have no simple way to know whether that claim is legally valid or dangerously misleading.*
>
> *When our team began building YumSure, the biggest architectural question was: 'How do we evaluate food products accurately?' Many hackathon teams would simply send the nutrition label to an LLM like GPT-4 and ask it to rate the product. We knew that approach was clinically and legally unacceptable—LLMs hallucinate, they confuse US and Indian standards, and their calculations are not reproducible.*
>
> *My role was to design and implement YumSure's deterministic evaluation core. First, I compiled and structured India's statutory regulations—FSSAI Schedules I and II, and ICMR-NIN 2024 Dietary Guidelines—into canonical rule datasets. Second, I authored four independent engines in Python. For marketing claims, I built an Abstract Syntax Tree compiler that evaluates compound conditions—for instance, verifying that a 'Trans Fat Free' claim only passes if saturated fat is also strictly below 6 grams.*
>
> *Third, I engineered our master Evaluation Coordinator. It executes all four engines in parallel, guarantees that a failure in one engine never crashes the app, and strictly prohibits arbitrary composite health scores. We don't give products a fake score like 72/100; we give transparent, clinical evaluations for individual nutrients so a hypertensive consumer can track sodium while a diabetic monitors added sugars.*
>
> *Finally, I led our nutrition data integrity remediation. I audited our data pipeline to ensure missing nutrients are never silently converted to zero, enforced dimensional compatibility so grams and millilitres are never swapped, and resolved visual threshold bugs on our mobile screens. Every result our engine outputs cites the exact statutory Gazette clause. Thank you."*

---

### D. Five Strongest Individual Contributions (Ranked)

1. **The Four Deterministic Evaluation Engines (`ca1d803`)**: Built the complete regulatory logic verifying FSSAI claims (AST parser), ICMR Table 15.1/15.2 matrices, additive statutory warnings, and nutrient RDA percentages.
2. **The Fault-Isolated Evaluation Coordinator (`781151c`)**: Designed the framework-independent master orchestrator with runner dependency injection, complete crash isolation, immutability, and zero composite health scores.
3. **Four-State Nutrient Declaration Semantics (`ca1d803`, `5e1cd57`)**: Solved the dangerous `0` vs `None` ambiguity by implementing `PRESENT`, `EXPLICITLY_ZERO`, `NOT_DECLARED`, and `UNKNOWN`.
4. **Strict Measurement Basis Dimensional Physics (`5e1cd57`, `7d126f6`)**: Prevented false legal passes by separating `PER_100G`, `PER_100ML`, and `PER_SERVING`, disallowing silent cross-unit conversions.
5. **Nutrition Data Integrity & Atwater Energy Validation (`7d126f6`)**: Engineered automated plausibility checks (sugar/fat hierarchies, Atwater macronutrient sum) and fixed mobile UI threshold bar mismatches.

---

### E. Ten Questions Judges May Ask Abhishek & Honest Answers

#### Q1: "Why did you build custom Python engines instead of using an LLM or prompt engineering?"
> **Answer:** *"Prompt engineering is stochastic—ask an LLM twice, and you may get two different compliance verdicts. In health and law, non-deterministic outputs are dangerous. By writing deterministic Python engines, our calculations are 100% reproducible, execute in under 1 millisecond, cite exact Gazette legal clauses, and require zero expensive API tokens."*

#### Q2: "Why didn't you give products an overall health score from 1 to 100 or a Nutri-Score grade?"
> **Answer:** *"Composite health scores are clinically misleading and legally indefensible in India. A high-protein protein bar loaded with 800mg of sodium could score '80/100 Green' under arbitrary scoring, misleading a hypertensive consumer. We present independent classifications for fat, sugar, sodium, and processing so consumers make informed decisions based on their specific medical needs."*

#### Q3: "What is the difference between missing data and explicit zero, and why does it matter?"
> **Answer:** *"If a package explicitly says 'Trans Fat: 0g', that is an evidence-backed declaration that legally qualifies for a 'Zero Trans Fat' claim. If a crowdsourced database entry omitted trans fat because someone forgot to type it, the value is missing (`None`). If our code defaulted `None` to `0`, we would falsely certify unmeasured products as trans-fat-free. We enforce a four-state enum to prevent this."*

#### Q4: "What happens if one of your engines crashes during evaluation?"
> **Answer:** *"Our Evaluation Coordinator wraps each engine in an isolated execution block. If the ingredient engine encounters a malformed input and crashes, the error is logged in an `engine_failures` array, while the nutrition, ICMR, and claims engines complete normally. The mobile user still receives their nutritional data instead of a blank screen."*

#### Q5: "How do you evaluate complex marketing claims like 'Low Saturated Fat and Rich in Fibre'?"
> **Answer:** *"I implemented an Abstract Syntax Tree (AST) evaluator in `claims_engine.py`. It parses boolean tree expressions with `AND`, `OR`, and `NOT` operators and numerical comparators (`LTE`, `GTE`), bounded to a recursion depth of 5. It evaluates compound conditions deterministically against declared nutrients."*

#### Q6: "Why can't you infer measurement basis from food form (solid vs liquid)?"
> **Answer:** *"Some liquid products (like syrups, condensed milk, or honey) are sold by weight in grams (per 100g), while some semi-solids or concentrates declare per 100ml. Silently guessing the basis based on whether a product is tagged 'liquid' or 'solid' causes dimensional errors. We mandate that the measurement basis must be explicitly declared or resolved from source metadata."*

#### Q7: "What did you do when you discovered carbohydrates were missing from the Nutri-Choice biscuits?"
> **Answer:** *"I traced the data pipeline and found that carbohydrates were omitted from our curated catalog entry. I cross-referenced the physical packaging records of barcode `8901063142015`, restored the verified $68.0\text{g} / 100\text{g}$ ($17.0\text{g}$ serving) declaration, and ran an Atwater energy plausibility check proving the declared 482 kcal matches the macronutrient sum to within 0.3%."*

#### Q8: "How does your code prevent per-serving values from showing per-100g numbers?"
> **Answer:** *"The mobile UI had a flawed fallback: `nutrient.valuePerServing ?? nutrient.valuePer100g`. When per-serving data was absent, it showed 100g numbers on the per-serving screen! I removed that fallback in Flutter and built bidirectional conversion in our backend adapter that only converts when a verified serving size and dimensionally compatible unit exist."*

#### Q9: "Did you build the database migrations and the API routes?"
> **Answer:** *"No. My teammate Tejas owns database migrations, SQLAlchemy repositories, ProductService, and FastAPI endpoints. My ownership boundary is the clinical and regulatory domain: the four engines, the coordinator, the AST compiler, the domain DTO contracts, and data integrity logic."*

#### Q10: "How do you know your engine implementations actually work?"
> **Answer:** *"We have 114 automated tests running in our backend suite. I authored 69 of these tests covering AST recursion limits, Schedule II authorized synonyms, ICMR Table 15.1 thresholds, Table 15.2 matrix mapping, coordinator fault isolation, and 12 dedicated nutrition data integrity scenarios. All 114 tests pass in 0.7 seconds."*

---

### F. Explaining Abhishek's Work: Technical vs. Non-Technical

| Major Contribution | Explanation for a Software / CS Judge | Explanation for a Non-Technical Judge |
| :--- | :--- | :--- |
| **Deterministic Engines** | *"Implemented pure domain functions with $O(N)$ time complexity and zero network I/O, decoupling regulatory logic from database ORMs and LLMs."* | *"We wrote strict mathematical calculators that check Indian food laws directly, instead of letting an AI guess or make up numbers."* |
| **Claims AST Evaluator** | *"Built a recursive descent boolean AST interpreter supporting compound logical gates (`AND`, `OR`, `NOT`) bounded to depth 5 to avoid call-stack overflow."* | *"We built a logic tree that verifies multi-part marketing claims, making sure a biscuit claiming 'Zero Trans Fat' doesn't secretly hide high saturated fat."* |
| **Evaluation Coordinator** | *"Engineered a framework-independent orchestrator using dependency injection, functional isolation, and immutable DTO returns with telemetry tracking."* | *"A master controller that runs all four nutrition checkers at once, making sure that if one checker has a glitch, the app never crashes for the user."* |
| **Missing vs. Zero Handling** | *"Enforced a 4-state algebraic sum type distinguishing explicit zero declarations from unobserved `None` values, preventing false-positive state transitions."* | *"We make sure that if a food package doesn't mention trans fat, the app doesn't assume it's zero and falsely tell you it's healthy."* |
| **Measurement-Basis Physics** | *"Enforced strict dimensional typing between mass (`PER_100G`), volume (`PER_100ML`), and discrete portions (`PER_SERVING`), rejecting mismatched comparator units."* | *"We made sure that drinks (millilitres) and snacks (grams) are never confused, and that a single biscuit's sugar isn't compared against a 100-gram limit."* |
| **Atwater Energy Validation** | *"Built an automated stoichiometric consistency validator calculating 4-9-4 Atwater caloric estimates from macronutrients to detect corrupted label data."* | *"A scientific sanity check: we multiply protein, fat, and carbs by their natural calorie values to make sure the manufacturer didn't print fake numbers."* |

---

## 8. Summary of Evidence & Verification Commands

All claims in this report are verifiable using the following repository commands:

- **Check Abhishek's Commits:**
  `git log --author="abhimahadik30" --oneline`
- **Run the Complete Backend Test Suite (114 tests, 0 failures):**
  `cd backend; .\venv\Scripts\python.exe -m unittest discover tests -v`
- **Run Abhishek's 12 Dedicated Nutrition Data Integrity Tests:**
  `cd backend; .\venv\Scripts\python.exe -m unittest tests/test_nutrition_data_integrity.py -v`
- **Run Abhishek's Evaluation Coordinator Tests (14 scenarios):**
  `cd backend; .\venv\Scripts\python.exe -m unittest tests/test_evaluation_integration.py -v`
- **Run Abhishek's Engine Tests (17 scenarios):**
  `cd backend; .\venv\Scripts\python.exe -m unittest tests/test_engines.py -v`

---

*Report authored for Abhishek Mahadik's hackathon jury presentation and individual evaluation.*

