# YumSure — Phase 1B.4: Engine Sample Cases & Test Fixtures

**Document Version**: 1.0.0  
**Status**: TEST FIXTURE SPECIFICATION  
**Author**: Senior Backend Architect & Nutrition Regulatory Intelligence Lead  
**Collaborator**: Tejas (Backend Foundation Lead)  
**Governing Documents**:
- `ENGINE_CONTRACTS.md` (v1.0.0)
- `RULE_SEED_DATA_SCHEMA.md` (v1.0.0)

---

## 1. Overview

This document provides concrete, end-to-end JSON sample fixtures for each of YumSure's four evaluation engines.

Every engine is demonstrated across three mandatory operational modes:
1. **Evidence-Complete Case** (`PASS` or `FAIL`)
2. **Missing-Data Case** (`INSUFFICIENT_DATA`)
3. **Indeterminate or Non-Applicable Case** (`INDETERMINATE` or `NOT_APPLICABLE`)

---

## 2. Engine 1: Nutrition Engine (`nutrition_engine.py`)

### Scenario 1.1: Evidence-Complete Solid Whole Food (Roasted Bengal Gram)
*Context: A traditional roasted chana product with complete FSSAI 2020 mandatory nutrition declarations.*

#### Input JSON (`ProductEvaluationInput`):
```json
{
  "product_id": "prod_roasted_chana_001",
  "product_name": "Traditional Roasted Bengal Gram (Chana)",
  "food_form": "solid",
  "package_size": "200g",
  "serving_size_value": 30.0,
  "serving_size_unit": "g",
  "nutrients": {
    "energy": {
      "nutrient_code": "energy",
      "per_100g_value": 380.0,
      "per_serving_value": 114.0,
      "unit": "kcal",
      "data_status": "PRESENT"
    },
    "protein": {
      "nutrient_code": "protein",
      "per_100g_value": 19.5,
      "per_serving_value": 5.85,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "carbohydrates": {
      "nutrient_code": "carbohydrates",
      "per_100g_value": 58.0,
      "per_serving_value": 17.4,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "total_sugars": {
      "nutrient_code": "total_sugars",
      "per_100g_value": 2.5,
      "per_serving_value": 0.75,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "added_sugars": {
      "nutrient_code": "added_sugars",
      "per_100g_value": 0.0,
      "per_serving_value": 0.0,
      "unit": "g",
      "data_status": "EXPLICITLY_ZERO"
    },
    "total_fat": {
      "nutrient_code": "total_fat",
      "per_100g_value": 5.2,
      "per_serving_value": 1.56,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "saturated_fat": {
      "nutrient_code": "saturated_fat",
      "per_100g_value": 0.8,
      "per_serving_value": 0.24,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "trans_fat": {
      "nutrient_code": "trans_fat",
      "per_100g_value": 0.0,
      "per_serving_value": 0.0,
      "unit": "g",
      "data_status": "EXPLICITLY_ZERO"
    },
    "sodium": {
      "nutrient_code": "sodium",
      "per_100g_value": 12.0,
      "per_serving_value": 3.6,
      "unit": "mg",
      "data_status": "PRESENT"
    }
  },
  "ingredients": [
    {
      "ingredient_code": "bengal_gram",
      "declared_label_text": "Whole Bengal Gram (Chana)",
      "sequence_order": 1,
      "processing_classification": "WHOLE_FOOD",
      "sugar_classification": "NOT_SUGAR"
    }
  ]
}
```

#### Expected Output JSON (`EngineBatchResult`):
```json
{
  "engine_name": "NUTRITION",
  "product_id": "prod_roasted_chana_001",
  "food_form": "solid",
  "results": [
    {
      "engine_name": "NUTRITION",
      "rule_id": "rdi_contrib_protein",
      "rule_code": "FSSAI_DAILY_RDI_PROTEIN",
      "outcome": "PASS",
      "title": "Protein Daily Contribution",
      "human_readable_explanation": "One serving (30g) provides 5.85g protein, contributing 10.83% of the FSSAI standard adult daily reference intake (54g).",
      "evidence_used": {
        "serving_value": 5.85,
        "fssai_standard_daily_rdi": 54.0,
        "percent_daily_contribution": 10.83
      },
      "missing_evidence": [],
      "statutory_citation": "FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)",
      "official_source_url": "https://fssai.gov.in/food-law/regulations/amendments/labelling-display",
      "source_version": "Gazette 17-11-2020",
      "warnings_or_limitations": "Based on 2,000 kcal standard adult diet reference."
    }
  ],
  "summary_counts": {
    "PASS": 1,
    "FAIL": 0,
    "INSUFFICIENT_DATA": 0,
    "INDETERMINATE": 0,
    "NOT_APPLICABLE": 0
  }
}
```

---

### Scenario 1.2: Missing Mandatory Added Sugar Declaration (Imported Biscuit)
*Context: Packaged imported biscuit declares total sugars but omits added sugars, violating FSSAI 2020 mandatory labelling.*

#### Input JSON:
```json
{
  "product_id": "prod_imported_biscuit_002",
  "product_name": "Imported European Tea Biscuits",
  "food_form": "solid",
  "nutrients": {
    "total_sugars": {
      "nutrient_code": "total_sugars",
      "per_100g_value": 22.0,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "added_sugars": {
      "nutrient_code": "added_sugars",
      "per_100g_value": null,
      "unit": "g",
      "data_status": "NOT_DECLARED"
    }
  }
}
```

#### Expected Output JSON:
```json
{
  "engine_name": "NUTRITION",
  "product_id": "prod_imported_biscuit_002",
  "food_form": "solid",
  "results": [
    {
      "engine_name": "NUTRITION",
      "rule_id": "rdi_contrib_added_sugar",
      "rule_code": "FSSAI_DAILY_RDI_ADDED_SUGAR",
      "outcome": "INSUFFICIENT_DATA",
      "title": "Added Sugar Declaration Status",
      "human_readable_explanation": "Added sugar declaration is missing from the product nutrition table. Cannot calculate percent daily contribution.",
      "evidence_used": {},
      "missing_evidence": ["added_sugars"],
      "statutory_citation": "FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)",
      "official_source_url": "https://fssai.gov.in/food-law/regulations/amendments/labelling-display",
      "source_version": "Gazette 17-11-2020",
      "warnings_or_limitations": "Added sugar declaration is mandatory for all packaged foods under Indian law."
    }
  ],
  "summary_counts": {
    "PASS": 0,
    "FAIL": 0,
    "INSUFFICIENT_DATA": 1,
    "INDETERMINATE": 0,
    "NOT_APPLICABLE": 0
  }
}
```

---

### Scenario 1.3: Non-Applicable Measurement Basis (Liquid Product vs Solid Standard)
*Context: A fruit beverage evaluated against solid-only specific nutrient guidelines.*

#### Expected Output:
`outcome = "NOT_APPLICABLE"`, `warnings_or_limitations = "Liquid beverage cannot be evaluated against solid food measurement basis."`

---

## 3. Engine 2: FSSAI Claims Engine (`claims_engine.py`)

### Scenario 2.1: Trans Fat Free & High Protein Claim (Solid Protein Bar)
*Context: High-protein nutrition bar claiming "Trans Fat Free" and "High Protein".*

#### Input JSON:
```json
{
  "product_id": "prod_protein_bar_003",
  "product_name": "Plant Power Protein Bar",
  "food_form": "solid",
  "nutrients": {
    "energy": {
      "nutrient_code": "energy",
      "per_100g_value": 360.0,
      "unit": "kcal",
      "data_status": "PRESENT"
    },
    "protein": {
      "nutrient_code": "protein",
      "per_100g_value": 22.0,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "trans_fat": {
      "nutrient_code": "trans_fat",
      "per_100g_value": 0.05,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "saturated_fat": {
      "nutrient_code": "saturated_fat",
      "per_100g_value": 1.2,
      "unit": "g",
      "data_status": "PRESENT"
    }
  },
  "declared_claims": [
    {
      "claim_code": "TRANS_FAT_FREE",
      "raw_label_statement": "Zero Trans Fat"
    },
    {
      "claim_code": "HIGH_PROTEIN",
      "raw_label_statement": "Rich in Protein"
    }
  ]
}
```

#### Expected Output JSON:
```json
{
  "engine_name": "CLAIMS",
  "product_id": "prod_protein_bar_003",
  "food_form": "solid",
  "results": [
    {
      "engine_name": "CLAIMS",
      "rule_id": "fssai_claim_trans_fat_free_solid",
      "rule_code": "TRANS_FAT_FREE",
      "outcome": "PASS",
      "title": "Trans Fat Free Claim Eligibility",
      "human_readable_explanation": "Product meets all statutory conditions for 'Trans Fat Free': trans fat is 0.05g/100g (strictly <0.2g), saturated fat is 1.2g/100g (<=1.5g), and saturated fat provides 3.0% of total energy (<=10.0%). The synonym 'Zero Trans Fat' is authorized under Schedule II.",
      "evidence_used": {
        "trans_fat_observed": 0.05,
        "saturated_fat_observed": 1.2,
        "sat_fat_pct_energy_calculated": 3.0,
        "synonym_matched": "Zero Trans Fat"
      },
      "missing_evidence": [],
      "statutory_citation": "FSSAI (Advertising and Claims) Regulations 2018, Schedule I Entry 4(b) & Schedule II",
      "official_source_url": "https://fssai.gov.in/food-law/regulations/amendments/advertising-claims",
      "source_version": "Version III (04-10-2022)"
    },
    {
      "engine_name": "CLAIMS",
      "rule_id": "fssai_claim_high_protein_solid",
      "rule_code": "HIGH_PROTEIN",
      "outcome": "PASS",
      "title": "High Protein Claim Eligibility",
      "human_readable_explanation": "Product contains 22.0g protein per 100g, exceeding the statutory requirement of >=10.8g/100g (20% of 54g RDI). 'Rich in Protein' is an authorized Schedule II synonym.",
      "evidence_used": {
        "protein_observed": 22.0,
        "statutory_threshold": 10.8,
        "synonym_matched": "Rich in Protein"
      },
      "missing_evidence": [],
      "statutory_citation": "FSSAI (Advertising and Claims) Regulations 2018, Schedule I Entry 5(b) & Schedule II",
      "official_source_url": "https://fssai.gov.in/food-law/regulations/amendments/advertising-claims",
      "source_version": "Version III (04-10-2022)"
    }
  ],
  "summary_counts": {
    "PASS": 2,
    "FAIL": 0,
    "INSUFFICIENT_DATA": 0,
    "INDETERMINATE": 0,
    "NOT_APPLICABLE": 0
  }
}
```

---

### Scenario 2.2: Claim With Missing Prerequisite Nutrient (Dietary Fibre Claim)
*Context: Product claims "High Fibre" on front of pack, but the nutrition table omits Dietary Fibre declaration.*

#### Expected Output:
`outcome = "INSUFFICIENT_DATA"`, `missing_evidence = ["dietary_fibre"]`, `human_readable_explanation = "Cannot verify 'High Fibre' claim because Dietary Fibre is omitted from the declared nutrition table."`

---

### Scenario 2.3: "No Added Sugar" Claim Breach Due to Disallowed Sweetener
*Context: Product claims "No Added Sugar", declares 0g added sugar in nutrition table, but contains Apple Juice Concentrate and Maltitol in ingredients.*

#### Expected Output:
`outcome = "FAIL"`, `evidence_used = {"disallowed_ingredients_found": ["apple_juice_concentrate", "ins_965_maltitol"]}`, `human_readable_explanation = "Claim 'No Added Sugar' fails under FSSAI Regulation 6(1): contains fruit juice concentrate and sugar alcohol sweetener (maltitol)."`

---

## 4. Engine 3: ICMR-HFSS Engine (`icmr_hfss_engine.py`)

### Scenario 3.1: Table 15.1 Breach & Table 15.2 UPF Cell C3 (Extruded Snack)
*Context: Commercial extruded spiced chips with cosmetic additives, high fat, and high sodium.*

#### Input JSON:
```json
{
  "product_id": "prod_masala_chips_004",
  "product_name": "Spicy Masala Potato Crisps",
  "food_form": "solid",
  "nutrients": {
    "energy": {
      "nutrient_code": "energy",
      "per_100g_value": 545.0,
      "unit": "kcal",
      "data_status": "PRESENT"
    },
    "added_sugars": {
      "nutrient_code": "added_sugars",
      "per_100g_value": 4.5,
      "unit": "g",
      "data_status": "PRESENT"
    },
    "sodium": {
      "nutrient_code": "sodium",
      "per_100g_value": 850.0,
      "unit": "mg",
      "data_status": "PRESENT"
    }
  },
  "ingredients": [
    {
      "ingredient_code": "dehydrated_potato_flakes",
      "declared_label_text": "Dehydrated Potato Flakes",
      "sequence_order": 1,
      "processing_classification": "INDUSTRIAL_FRACTION"
    },
    {
      "ingredient_code": "palm_olein",
      "declared_label_text": "Refined Palm Olein",
      "sequence_order": 2,
      "processing_classification": "CULINARY_PROCESSED"
    },
    {
      "ingredient_code": "ins_627_disodium_guanylate",
      "declared_label_text": "Flavour Enhancer (INS 627)",
      "sequence_order": 3,
      "processing_classification": "COSMETIC_ADDITIVE"
    }
  ]
}
```

#### Expected Output JSON:
```json
{
  "engine_name": "ICMR_HFSS",
  "product_id": "prod_masala_chips_004",
  "food_form": "solid",
  "results": [
    {
      "engine_name": "ICMR_HFSS",
      "rule_id": "icmr_15_1_salt_solid",
      "rule_code": "HFSS_THRESHOLD_SALT_SOLID",
      "outcome": "FAIL",
      "title": "ICMR Salt Threshold of Concern",
      "human_readable_explanation": "Salt content is 2,125mg/100g (850mg sodium * 2.5), significantly exceeding the ICMR-NIN public health threshold of concern (>625mg/100g).",
      "evidence_used": {
        "sodium_mg": 850.0,
        "salt_calculated_mg": 2125.0,
        "threshold_mg": 625.0
      },
      "statutory_citation": "ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1",
      "official_source_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "source_version": "May 2024"
    },
    {
      "engine_name": "ICMR_HFSS",
      "rule_id": "icmr_matrix_c3",
      "rule_code": "ICMR_MATRIX_CELL_C3",
      "outcome": "PASS",
      "title": "ICMR Table 15.2 Matrix: Cell C3 (High-Calorie UPF)",
      "human_readable_explanation": "Classified into Matrix Cell C3: Ultra-processed food (Group C) with high calorific density (545 kcal/100g > 500 kcal). Characterized by industrial matrix deconstruction and cosmetic flavour enhancers.",
      "evidence_used": {
        "processing_group": "GROUP_C",
        "nutritional_category": "CAT_3",
        "is_upf": true,
        "is_hfss": true,
        "energy_kcal": 545.0
      },
      "statutory_citation": "ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 98",
      "official_source_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "source_version": "May 2024"
    }
  ],
  "summary_counts": {
    "PASS": 1,
    "FAIL": 1,
    "INSUFFICIENT_DATA": 0,
    "INDETERMINATE": 0,
    "NOT_APPLICABLE": 0
  }
}
```

---

### Scenario 3.2: Non-Applicable Table 15.2 on Beverage (Artificially Sweetened Diet Soda)
*Context: Carbonated diet beverage with intense sweeteners.*

#### Expected Output:
- Table 15.1: `outcome = "PASS"`, `human_readable_explanation = "Added sugar is 0g/100ml (<=2.0g), Energy is 1 kcal/100ml (<=70 kcal)."`
- Table 15.2 Matrix: `outcome = "NOT_APPLICABLE"`, `human_readable_explanation = "Table 15.2 Category 1-3 matrix applies strictly to solid foods. ICMR-NIN DGI 2024 does not define Category 1-3 energy bands for beverages."`

---

### Scenario 3.3: Indeterminate Processing Extent (Tomato Puree with Citric Acid)
*Context: Plain crushed tomato puree with salt and INS 330 (citric acid). No cosmetic additives or reconstitution.*

#### Expected Output:
- Table 15.2 Matrix: `outcome = "INDETERMINATE"`, `human_readable_explanation = "Contains functional acidity regulator (INS 330) in a whole vegetable base. Lacks cosmetic additives or industrial fractions. Ambiguous between Group B (Culinary processed) and Group C. Requires recipe audit."`

---

### Scenario 3.4: Low-Calorie UPF Solid Snack (Matrix Cell C1)
*Context: Reconstituted konjac and soy protein snack with emulsifiers and artificial colours, formulated to 120 kcal/100g.*

#### Expected Output:
- Table 15.2 Matrix: `outcome = "PASS"`, `rule_code = "ICMR_MATRIX_CELL_C1"`, `evidence_used = {"is_upf": true, "is_hfss": false, "energy_kcal": 120.0}`, `human_readable_explanation = "Classified as Cell C1: Ultra-processed food (Group C) but low in energy (120 kcal/100g <= 250 kcal, non-HFSS). Demonstrates that UPF and HFSS are independent dimensions."`

---

## 5. Engine 4: Ingredient Engine (`ingredient_engine.py`)

### Scenario 4.1: Aspartame in Flavoured Drink with Mandatory Warning Check
*Context: Aspartame used in a low-calorie drink.*

#### Expected Output:
`outcome = "PASS"`, `rule_type = "MANDATORY_LABEL_WARNING"`, `evidence_used = {"ins_number": "951", "additive": "Aspartame"}`, `warnings_or_limitations = "MANDATORY STATUTORY WARNING REQUIRED: CONTAINS ASPARTAME. NOT RECOMMENDED FOR PHENYLKETONURICS."`

---

### Scenario 4.2: Uncataloged Herbal Ingredient
*Context: Packaged ayurvedic infusion listing "Proprietary Forest Herb Extract".*

#### Expected Output:
`outcome = "INSUFFICIENT_DATA"`, `missing_evidence = ["ins_number", "botanical_species", "processing_method"]`, `human_readable_explanation = "Uncharacterized ingredient cannot be safely mapped to INS additive catalogue or chemical classification."`

---

### Scenario 4.3: Preservative Exceeding Maximum Permissible Limit
*Context: Flavoured water contains 160 ppm Sodium Benzoate (INS 211), exceeding statutory 120 ppm limit.*

#### Expected Output:
`outcome = "FAIL"`, `evidence_used = {"observed_ppm": 160.0, "max_permitted_ppm": 120.0}`, `human_readable_explanation = "Sodium Benzoate concentration (160 ppm) exceeds statutory maximum permissible limit of 120 ppm under FSSAI Additive Regulations 2011 Appendix A Table 3."`

