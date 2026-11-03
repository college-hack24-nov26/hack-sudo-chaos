# YumSure — Indian Packaged-Food Nutrition Intelligence Application

YumSure is a production-grade, consumer-first nutrition intelligence platform designed specifically for the Indian packaged-food ecosystem. It empowers Indian shoppers to scan packaged food barcodes and receive instant, regulation-backed nutritional breakdowns, ingredient analyses, allergen disclosures, and statutory claim validations.

---

## 1. Executive Summary & Value Proposition

Packaged food labels in India are frequently opaque, featuring aggressive marketing claims ("High Protein", "Zero Added Sugar", "Low Fat") that mislead consumers. YumSure bridges this trust gap by combining:
- **Strict FSSAI Regulatory Alignment**: Validates on-pack marketing claims against the Food Safety and Standards Authority of India (Advertising and Claims) Regulations, 2018 and (Labelling and Display) Regulations, 2020.
- **Three Separate Deterministic Engines**:
  1. **Nutritional Interpretation Engine**: Classifies nutrient density (Low / Moderate / High) against ICMR-NIN 2020 daily allowances without inventing subjective "health scores".
  2. **Regulatory Claims Engine**: Computes strict pass/fail validations on manufacturer claims.
  3. **Ingredient Interpretation Engine**: Flags allergens, functional additives (preservatives, emulsifiers, artificial sweeteners), refined carbs, and added sodium/sugars with clear functional explanations.
- **Deterministic-First AI Intelligence**: Leverages Grok (xAI) or NVIDIA NIM text-only LLMs solely to synthesize pre-computed calculations into everyday consumer language, backed by an immutable local deterministic fallback.

---

## 2. Technology Stack

| Layer | Technology | Version / Specification | Role |
| :--- | :--- | :--- | :--- |
| **Backend** | Python / FastAPI | Python 3.14+ / FastAPI 0.115+ | High-throughput asynchronous REST API & deterministic engines |
| **Database** | PostgreSQL | PostgreSQL 18+ | Normalized relational storage for products, nutrients, rules, logs |
| **ORM & Migrations** | SQLAlchemy & Alembic | 2.0+ / 1.13+ | Type-safe schema definition and relational integrity |
| **External API** | Open Food Facts API v3 | REST JSON | Primary external barcode catalog with ODbL compliance |
| **AI Synthesis** | Grok (xAI) / NVIDIA NIM | Text-only LLM APIs | Explain pre-computed results in simple vernacular |
| **Frontend** | Flutter / Dart | Flutter 3.32+ / Dart 3.8+ | Cross-platform Android application with barcode scanning UI |

---

## 3. Core Architecture Principles

1. **No Fabricated Health Scores**: We do not assign arbitrary 1-100 or letter grade scores to products. Every nutrient and claim is interpreted independently using defensible statutory thresholds.
2. **Deterministic Precedence**: All nutritional classifications, allergen detections, and claim verifications are computed in deterministic Python services before any AI layer is engaged. The AI is never permitted to invent numbers or alter verdicts.
3. **Auditability & Provenance**: Every data field records its source (`OFF_API_V3`, `VERIFIED_INTERNAL`, `KAGGLE_AUDITED`), retrieval timestamp, and raw payload hash. Verified records are immutable against partial external updates.
4. **Resilience & Offline Grace**: If external APIs or AI endpoints fail or throttle, the application seamlessly serves deterministic database results and rule-based explanations.

---

## 4. Repository Structure

```
hack-sudo-chaos/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/      # Product lookup, claims, AI explain endpoints
│   │   │       └── router.py       # API router registration
│   │   ├── core/
│   │   │   ├── config.py           # Environment variables & runtime settings
│   │   │   └── security.py         # API key validation & headers
│   │   ├── db/
│   │   │   ├── base.py             # SQLAlchemy base models
│   │   │   └── session.py          # Asynchronous PostgreSQL session pooling
│   │   ├── models/                 # Normalized relational DB models
│   │   ├── schemas/                # Pydantic v2 data transfer schemas
│   │   ├── services/
│   │   │   ├── nutrition_engine.py # Nutrient threshold interpreter (ICMR-NIN)
│   │   │   ├── claims_engine.py    # FSSAI claims validator
│   │   │   ├── ingredient_engine.py# Ingredient function & allergen parser
│   │   │   ├── openfoodfacts.py    # Open Food Facts API v3 client
│   │   │   └── ai_explainer.py     # Grok/NVIDIA AI service with fallback
│   │   └── main.py                 # FastAPI application factory
│   ├── pyproject.toml / requirements.txt
│   └── venv/
├── frontend/
│   ├── lib/
│   │   ├── core/                   # Theme, constants, API client
│   │   ├── models/                 # Dart entity classes matching API schemas
│   │   ├── services/               # Product repository, camera scanner
│   │   └── ui/
│   │       ├── screens/            # Home, Scanner, Product Detail, Explainer
│   │       └── widgets/            # Nutrient cards, Claims badges, Ingredient tags
│   ├── pubspec.yaml
│   └── assets/
└── documentation/ (and root architecture docs)
    ├── PROJECT_ARCHITECTURE.md
    ├── DATABASE_DESIGN.md
    ├── API_DOCUMENTATION.md
    ├── NUTRITION_RULES.md
    ├── INGREDIENT_CATALOGUE.md
    ├── DATA_SOURCES_AND_LICENCES.md
    ├── IMPLEMENTATION_PROGRESS.md
    ├── JUDGE_PRESENTATION_GUIDE.md
    └── KNOWN_LIMITATIONS.md
```

---

## 5. Quick Start (Development)

### Prerequisites
- Python 3.12+ (Python 3.14 supported)
- PostgreSQL 15+ installed and running on port 5432
- Flutter 3.24+ with Android SDK

### Backend Setup
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Interactive documentation available at `http://localhost:8000/docs`.

### Frontend Setup
```powershell
cd frontend
flutter pub get
flutter run -d android
```

---

## 6. Regulatory & Statutory References
- FSSAI (Labelling and Display) Regulations, 2020 (Gazette Notification F. No. 1-94/FSSAI/SP(L&C/A)/2009)
- FSSAI (Advertising and Claims) Regulations, 2018 (Gazette Notification F. No. 1-4/Standards/SP(L&M)/FSSAI-2018)
- ICMR-National Institute of Nutrition (NIN) 2020: Recommended Dietary Allowances (RDA) for Indians
