# YumSure — REST API Specification & Contracts

This document specifies the RESTful API contracts implemented by the FastAPI backend (`/api/v1`).

---

## 1. Global Standards & Error Format

All error responses adhere to RFC 7807 (Problem Details for HTTP APIs):

```json
{
  "type": "https://yumsure.in/errors/PRODUCT_NOT_FOUND",
  "title": "Product Not Found",
  "status": 404,
  "detail": "Barcode 8901030000000 is not in the local database and could not be resolved from Open Food Facts.",
  "instance": "/api/v1/products/8901030000000",
  "timestamp": "2026-11-03T12:00:00Z"
}
```

---

## 2. API Endpoints

### 2.1 Health & Diagnostics
`GET /health`

**Response (200 OK):**
```json
{
  "status": "HEALTHY",
  "database": "CONNECTED",
  "open_food_facts": "REACHABLE",
  "ai_provider": "AVAILABLE",
  "version": "1.0.0",
  "timestamp": "2026-11-03T12:00:00Z"
}
```

---

### 2.2 Product Nutrition Intelligence Lookup
`GET /api/v1/products/{barcode}`

Retrieves product profile, normalized nutrients, statutory claim validations, and ingredient breakdown.

**Parameters:**
- `barcode` (string, path, required): 8, 12, 13, or 14-digit GTIN / EAN barcode (e.g. `8901030383701`).
- `include_ai_explanation` (boolean, query, optional, default: `true`): Whether to include the synthesized summary.

**Response (200 OK):**
```json
{
  "product": {
    "barcode": "8901030383701",
    "product_name": "Nutri-Choice Digestive Biscuits",
    "brand_name": "Britannia",
    "package_size": "100 g",
    "serving_size_value": 25.0,
    "serving_size_unit": "g",
    "food_form": "solid",
    "food_category": "Biscuits & Bakery",
    "is_verified": true,
    "source_provenance": "OFF_API_V3",
    "source_retrieval_date": "2026-11-03T10:15:00Z"
  },
  "nutritional_interpretation": {
    "basis": "per_100g",
    "reference_standard": "ICMR-NIN 2020 RDA (2000 kcal standard adult diet)",
    "nutrients": [
      {
        "nutrient_code": "energy",
        "display_name": "Energy",
        "value_per_100g": 482.0,
        "value_per_serving": 120.5,
        "unit": "kcal",
        "rda_percentage": 24.1,
        "classification": "Moderate",
        "concern_level": "NEUTRAL",
        "status": "PRESENT"
      },
      {
        "nutrient_code": "protein",
        "display_name": "Protein",
        "value_per_100g": 8.0,
        "value_per_serving": 2.0,
        "unit": "g",
        "rda_percentage": 14.8,
        "classification": "High",
        "concern_level": "POSITIVE",
        "status": "PRESENT"
      },
      {
        "nutrient_code": "total_sugars",
        "display_name": "Total Sugars",
        "value_per_100g": 14.5,
        "value_per_serving": 3.6,
        "unit": "g",
        "rda_percentage": null,
        "classification": "Moderate",
        "concern_level": "CONCERN",
        "status": "PRESENT"
      },
      {
        "nutrient_code": "added_sugars",
        "display_name": "Added Sugars",
        "value_per_100g": 13.0,
        "value_per_serving": 3.25,
        "unit": "g",
        "rda_percentage": 26.0,
        "classification": "High",
        "concern_level": "CONCERN",
        "status": "PRESENT"
      },
      {
        "nutrient_code": "sodium",
        "display_name": "Sodium",
        "value_per_100g": 450.0,
        "value_per_serving": 112.5,
        "unit": "mg",
        "rda_percentage": 22.5,
        "classification": "Moderate",
        "concern_level": "CONCERN",
        "status": "PRESENT"
      },
      {
        "nutrient_code": "dietary_fibre",
        "display_name": "Dietary Fibre",
        "value_per_100g": 6.2,
        "value_per_serving": 1.55,
        "unit": "g",
        "rda_percentage": 20.6,
        "classification": "High",
        "concern_level": "POSITIVE",
        "status": "PRESENT"
      }
    ]
  },
  "regulatory_claims_validation": {
    "applicable_regulation": "FSSAI (Advertising and Claims) Regulations, 2018 - Schedule II",
    "claims": [
      {
        "claim_code": "HIGH_FIBRE",
        "claim_name": "High Fibre",
        "status": "ELIGIBLE",
        "actual_value": 6.2,
        "required_threshold": 6.0,
        "unit": "g per 100g",
        "regulatory_reference": "FSSAI (Advertising and Claims) Regulations 2018, Schedule II, Item 8",
        "explanation": "Contains 6.2g of fibre per 100g, exceeding the statutory minimum of 6.0g."
      },
      {
        "claim_code": "SOURCE_PROTEIN",
        "claim_name": "Source of Protein",
        "status": "ELIGIBLE",
        "actual_value": 8.0,
        "required_threshold": 5.4,
        "unit": "g per 100g (10% of 54g adult RDA)",
        "regulatory_reference": "FSSAI (Advertising and Claims) Regulations 2018, Schedule II, Item 3",
        "explanation": "Contains 8.0g of protein per 100g, fulfilling the 10% daily adult RDA requirement (5.4g)."
      },
      {
        "claim_code": "LOW_SUGAR",
        "claim_name": "Low Sugar",
        "status": "INELIGIBLE",
        "actual_value": 14.5,
        "required_threshold": 5.0,
        "unit": "g per 100g",
        "regulatory_reference": "FSSAI (Advertising and Claims) Regulations 2018, Schedule II, Item 6",
        "explanation": "Contains 14.5g of sugars per 100g, which exceeds the low sugar limit of 5.0g."
      }
    ]
  },
  "ingredient_analysis": {
    "total_ingredients_count": 8,
    "declared_allergens": ["Gluten (Wheat)", "Milk (Butter)"],
    "categories": [
      {
        "category": "REFINED_CARB",
        "count": 1,
        "items": ["Refined Wheat Flour (Maida)"]
      },
      {
        "category": "FIBRE",
        "count": 1,
        "items": ["Wheat Bran (14%)"]
      },
      {
        "category": "SWEETENER",
        "count": 2,
        "items": ["Sugar", "Invert Sugar Syrup"]
      },
      {
        "category": "EMULSIFIER",
        "count": 2,
        "items": ["Soya Lecithin (INS 322i)", "Mono- and diglycerides of fatty acids (INS 471)"]
      }
    ]
  },
  "ai_explanation": {
    "provider": "xai_grok",
    "is_fallback": false,
    "text": "Nutri-Choice Digestive Biscuits provide a good amount of dietary fibre (6.2g per 100g), qualifying legally as 'High Fibre' under Indian standards. However, it contains 13g of added sugar per 100g, accounting for over a quarter of recommended daily intake if consumed in excess. Declared allergens include Wheat (Gluten) and Milk."
  }
}
```

---

### 2.3 On-Demand AI Synthesis
`POST /api/v1/products/{barcode}/ai-explain`

Allows requesting an AI explanation with custom vernacular guidance (e.g. simplified for elderly or Hindi-transliterated guidance).

**Request Body:**
```json
{
  "target_audience": "general_consumer",
  "preferred_language": "en"
}
```

**Response (200 OK):**
```json
{
  "barcode": "8901030383701",
  "explanation": "Nutri-Choice Digestive Biscuits...",
  "provider": "xai_grok",
  "is_fallback": false,
  "generated_at": "2026-11-03T12:00:05Z"
}
```

---

### 2.4 Reference Catalog Queries
- `GET /api/v1/rules/claims`: Returns all active FSSAI Schedule II claim threshold specifications.
- `GET /api/v1/rules/nutrients`: Returns all ICMR-NIN 2020 RDA values and classification criteria.
- `GET /api/v1/ingredients/additives`: Returns the recognized INS numbers and additive functional roles.

