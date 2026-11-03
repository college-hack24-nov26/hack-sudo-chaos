# YumSure — Phase 1B.4: Rule Seed Data Schema & Specification

**Document Version**: 1.0.0  
**Status**: SEED DATA SPECIFICATION  
**Author**: Senior Backend Architect & Nutrition Regulatory Intelligence Lead  
**Collaborator**: Tejas (Backend Foundation Lead)  
**Governing Documents**:
- `NUTRIENT_CLASSIFICATION_RESEARCH.md` (v4.0.0)
- `SOURCE_PROVENANCE_REGISTER.md` (v4.0.0)
- `ICMR_TABLE_15_2_VERIFICATION.md` (v4.0.0)
- `ENGINE_CONTRACTS.md` (v1.0.0)

---

## 1. Overview & Seed Data Philosophy

The seed data files in YumSure represent **authoritative, verified regulatory standards and dietary guidelines**. 

To maintain statutory integrity, the seed datasets are partitioned into five structurally independent JSON datasets:
1. `icmr_table_15_1_seed.json`: ICMR-NIN 2024 Table 15.1 Thresholds of Concern.
2. `icmr_table_15_2_seed.json`: ICMR-NIN 2024 Table 15.2 2D Matrix (A1–C3 cells).
3. `fssai_schedule_i_claims_seed.json`: FSSAI 2018 (Consolidated 2022) Schedule I Nutrient Content Claims.
4. `fssai_schedule_ii_synonyms_seed.json`: FSSAI 2018 Schedule II Authorized Synonyms.
5. `ingredient_rules_seed.json`: FSSAI Statutory Additive Safety Limits & Mandatory Warnings.

### Universal Rule Attributes
Every seed rule across all datasets MUST contain the following 12 metadata attributes:
1. `rule_id`: Stable, immutable primary key string (e.g. `fssai_claim_trans_fat_free_solid`).
2. `rule_family`: Broad categorization (e.g. `FSSAI_CLAIM`, `ICMR_HFSS_THRESHOLD`, `ICMR_MATRIX`, `INGREDIENT_SAFETY`).
3. `official_source_name`: Exact statutory authority or institution (e.g. `FSSAI`, `ICMR-NIN`).
4. `document_version`: Version or gazette number (e.g. `Version III dated 04-10-2022`).
5. `exact_citation`: Exact schedule, table, or clause (e.g. `Schedule I, Entry 4(b)`).
6. `official_source_url`: Verifiable government or institutional URL.
7. `measurement_basis`: Explicit basis (`PER_100G`, `PER_100ML`, `PER_100KCAL`, `PER_SERVING`, or `NOT_APPLICABLE`).
8. `applicable_food_form`: `solid`, `liquid`, or `both`.
9. `conditions`: Machine-readable condition logic (AST or scalar thresholds).
10. `effective_from`: Established effective date (`YYYY-MM-DD`).
11. `verification_status`: `VERIFIED_STATUTORY`, `VERIFIED_GUIDELINE`, or `RESEARCH_REQUIRED`.
12. `limitations_and_ambiguities`: Documented scientific or regulatory boundary conditions.

---

## 2. Seed Schema 1: ICMR Table 15.1 Nutrient Thresholds

### 2.1 Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IcmrTable151ThresholdRule",
  "type": "object",
  "required": [
    "rule_id", "rule_code", "target_nutrient_code", "food_form",
    "threshold_value", "operator", "measurement_basis", "statutory_provenance"
  ],
  "properties": {
    "rule_id": { "type": "string" },
    "rule_code": { "type": "string" },
    "target_nutrient_code": { "type": "string" },
    "food_form": { "type": "string", "enum": ["solid", "liquid"] },
    "threshold_value": { "type": "number" },
    "operator": { "type": "string", "enum": ["GT", "GTE"] },
    "measurement_basis": { "type": "string", "enum": ["PER_100G", "PER_100ML"] },
    "statutory_provenance": {
      "type": "object",
      "required": ["source_name", "document_title", "table_number", "publication_date", "official_url", "copyright_notice"],
      "properties": {
        "source_name": { "type": "string" },
        "document_title": { "type": "string" },
        "table_number": { "type": "string" },
        "publication_date": { "type": "string" },
        "official_url": { "type": "string" },
        "copyright_notice": { "type": "string" }
      }
    },
    "consumer_guidance": { "type": "string" },
    "limitations": { "type": "string" }
  }
}
```

### 2.2 Complete Seed Records (Official Table 15.1 Cutoffs)
```json
[
  {
    "rule_id": "icmr_15_1_added_sugar_solid",
    "rule_code": "HFSS_THRESHOLD_ADDED_SUGAR_SOLID",
    "target_nutrient_code": "added_sugars",
    "food_form": "solid",
    "threshold_value": 3.0,
    "operator": "GT",
    "measurement_basis": "PER_100G",
    "statutory_provenance": {
      "source_name": "ICMR - National Institute of Nutrition",
      "document_title": "Dietary Guidelines for Indians (2024)",
      "table_number": "Table 15.1",
      "publication_date": "2024-05-08",
      "official_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "copyright_notice": "Copyright Reserved ICMR-NIN. Institutional public health guidance."
    },
    "consumer_guidance": "Contains high added sugar (>3.0g/100g) exceeding ICMR-NIN public health threshold.",
    "limitations": "Evaluates added sugars only; intrinsic sugars from fruits and unflavored milk excluded."
  },
  {
    "rule_id": "icmr_15_1_added_sugar_liquid",
    "rule_code": "HFSS_THRESHOLD_ADDED_SUGAR_LIQUID",
    "target_nutrient_code": "added_sugars",
    "food_form": "liquid",
    "threshold_value": 2.0,
    "operator": "GT",
    "measurement_basis": "PER_100ML",
    "statutory_provenance": {
      "source_name": "ICMR - National Institute of Nutrition",
      "document_title": "Dietary Guidelines for Indians (2024)",
      "table_number": "Table 15.1",
      "publication_date": "2024-05-08",
      "official_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "copyright_notice": "Copyright Reserved ICMR-NIN. Institutional public health guidance."
    },
    "consumer_guidance": "Beverage contains high added sugar (>2.0g/100ml) exceeding ICMR-NIN public health threshold.",
    "limitations": "Evaluates added sugars only."
  },
  {
    "rule_id": "icmr_15_1_salt_solid",
    "rule_code": "HFSS_THRESHOLD_SALT_SOLID",
    "target_nutrient_code": "sodium",
    "food_form": "solid",
    "threshold_value": 625.0,
    "operator": "GT",
    "measurement_basis": "PER_100G",
    "statutory_provenance": {
      "source_name": "ICMR - National Institute of Nutrition",
      "document_title": "Dietary Guidelines for Indians (2024)",
      "table_number": "Table 15.1",
      "publication_date": "2024-05-08",
      "official_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "copyright_notice": "Copyright Reserved ICMR-NIN. Institutional public health guidance."
    },
    "consumer_guidance": "Contains high salt/sodium (>625mg salt or >250mg sodium per 100g).",
    "limitations": "Table 15.1 specifies salt (NaCl). Engine converts sodium to salt using factor: Salt (mg) = Sodium (mg) * 2.5."
  },
  {
    "rule_id": "icmr_15_1_salt_liquid",
    "rule_code": "HFSS_THRESHOLD_SALT_LIQUID",
    "target_nutrient_code": "sodium",
    "food_form": "liquid",
    "threshold_value": 175.0,
    "operator": "GT",
    "measurement_basis": "PER_100ML",
    "statutory_provenance": {
      "source_name": "ICMR - National Institute of Nutrition",
      "document_title": "Dietary Guidelines for Indians (2024)",
      "table_number": "Table 15.1",
      "publication_date": "2024-05-08",
      "official_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "copyright_notice": "Copyright Reserved ICMR-NIN. Institutional public health guidance."
    },
    "consumer_guidance": "Beverage contains high salt/sodium (>175mg salt or >70mg sodium per 100ml).",
    "limitations": "Salt (mg) = Sodium (mg) * 2.5."
  },
  {
    "rule_id": "icmr_15_1_added_fat_solid",
    "rule_code": "HFSS_THRESHOLD_ADDED_FAT_SOLID",
    "target_nutrient_code": "added_fat",
    "food_form": "solid",
    "threshold_value": 4.2,
    "operator": "GT",
    "measurement_basis": "PER_100G",
    "statutory_provenance": {
      "source_name": "ICMR - National Institute of Nutrition",
      "document_title": "Dietary Guidelines for Indians (2024)",
      "table_number": "Table 15.1",
      "publication_date": "2024-05-08",
      "official_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "copyright_notice": "Copyright Reserved ICMR-NIN. Institutional public health guidance."
    },
    "consumer_guidance": "Contains high added fat (>4.2g/100g) exceeding ICMR-NIN public health threshold.",
    "limitations": "CRITICAL: Added fat is not statutory under FSSAI. If undeclared, engine returns INSUFFICIENT_DATA; never infers from total fat."
  },
  {
    "rule_id": "icmr_15_1_added_fat_liquid",
    "rule_code": "HFSS_THRESHOLD_ADDED_FAT_LIQUID",
    "target_nutrient_code": "added_fat",
    "food_form": "liquid",
    "threshold_value": 1.5,
    "operator": "GT",
    "measurement_basis": "PER_100ML",
    "statutory_provenance": {
      "source_name": "ICMR - National Institute of Nutrition",
      "document_title": "Dietary Guidelines for Indians (2024)",
      "table_number": "Table 15.1",
      "publication_date": "2024-05-08",
      "official_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "copyright_notice": "Copyright Reserved ICMR-NIN. Institutional public health guidance."
    },
    "consumer_guidance": "Beverage contains high added fat (>1.5g/100ml).",
    "limitations": "Cannot be inferred from total fat."
  },
  {
    "rule_id": "icmr_15_1_energy_solid",
    "rule_code": "HFSS_THRESHOLD_ENERGY_SOLID",
    "target_nutrient_code": "energy",
    "food_form": "solid",
    "threshold_value": 250.0,
    "operator": "GT",
    "measurement_basis": "PER_100G",
    "statutory_provenance": {
      "source_name": "ICMR - National Institute of Nutrition",
      "document_title": "Dietary Guidelines for Indians (2024)",
      "table_number": "Table 15.1",
      "publication_date": "2024-05-08",
      "official_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "copyright_notice": "Copyright Reserved ICMR-NIN. Institutional public health guidance."
    },
    "consumer_guidance": "High energy density solid food (>250 kcal/100g).",
    "limitations": "Applies to total declared energy."
  },
  {
    "rule_id": "icmr_15_1_energy_liquid",
    "rule_code": "HFSS_THRESHOLD_ENERGY_LIQUID",
    "target_nutrient_code": "energy",
    "food_form": "liquid",
    "threshold_value": 70.0,
    "operator": "GT",
    "measurement_basis": "PER_100ML",
    "statutory_provenance": {
      "source_name": "ICMR - National Institute of Nutrition",
      "document_title": "Dietary Guidelines for Indians (2024)",
      "table_number": "Table 15.1",
      "publication_date": "2024-05-08",
      "official_url": "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
      "copyright_notice": "Copyright Reserved ICMR-NIN. Institutional public health guidance."
    },
    "consumer_guidance": "High energy density beverage (>70 kcal/100ml).",
    "limitations": "Applies to total declared energy."
  }
]
```

---

## 3. Seed Schema 2: ICMR Table 15.2 Food Classification Matrix

### 3.1 Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IcmrTable152MatrixRule",
  "type": "object",
  "required": [
    "matrix_id", "cell_code", "processing_group", "nutritional_category",
    "applicable_food_form", "is_upf", "is_hfss", "energy_min_kcal", "energy_max_kcal",
    "processing_description", "nutritional_description", "consumer_guidance", "statutory_provenance"
  ],
  "properties": {
    "matrix_id": { "type": "string" },
    "cell_code": { "type": "string", "enum": ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"] },
    "processing_group": { "type": "string", "enum": ["GROUP_A", "GROUP_B", "GROUP_C"] },
    "nutritional_category": { "type": "string", "enum": ["CAT_1", "CAT_2", "CAT_3"] },
    "applicable_food_form": { "type": "string", "enum": ["solid"] },
    "is_upf": { "type": "boolean" },
    "is_hfss": { "type": "boolean" },
    "energy_min_kcal": { "type": ["number", "null"] },
    "energy_max_kcal": { "type": ["number", "null"] },
    "processing_description": { "type": "string" },
    "nutritional_description": { "type": "string" },
    "consumer_guidance": { "type": "string" },
    "statutory_provenance": { "type": "object" }
  }
}
```

### 3.2 Complete Seed Records (Official 9 Cells)
```json
[
  {
    "matrix_id": "icmr_matrix_a1",
    "cell_code": "A1",
    "processing_group": "GROUP_A",
    "nutritional_category": "CAT_1",
    "applicable_food_form": "solid",
    "is_upf": false,
    "is_hfss": false,
    "energy_min_kcal": null,
    "energy_max_kcal": 250.0,
    "processing_description": "Minimally processed fresh or frozen foods (e.g. cut fruits, raw vegetables, boiled whole legumes).",
    "nutritional_description": "Low calorific density (<=250 kcal/100g) with natural nutrient matrix.",
    "consumer_guidance": "Recommended core of a healthy diet. Wholesome and nutrient-rich.",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97"
    }
  },
  {
    "matrix_id": "icmr_matrix_a2",
    "cell_code": "A2",
    "processing_group": "GROUP_A",
    "nutritional_category": "CAT_2",
    "applicable_food_form": "solid",
    "is_upf": false,
    "is_hfss": true,
    "energy_min_kcal": 250.0,
    "energy_max_kcal": 500.0,
    "processing_description": "Minimally processed natural whole foods with moderate natural energy density (e.g. dried whole grains, dried fruits, plain roasted oilseeds).",
    "nutritional_description": "Moderate calorific density (>250 to 500 kcal/100g) without industrial deconstruction.",
    "consumer_guidance": "Wholesome food. Consume as part of balanced meals with portion awareness.",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97"
    }
  },
  {
    "matrix_id": "icmr_matrix_a3",
    "cell_code": "A3",
    "processing_group": "GROUP_A",
    "nutritional_category": "CAT_3",
    "applicable_food_form": "solid",
    "is_upf": false,
    "is_hfss": true,
    "energy_min_kcal": 500.0,
    "energy_max_kcal": null,
    "processing_description": "Minimally processed natural high-energy foods (e.g. whole tree nuts, dry oilseeds).",
    "nutritional_description": "High calorific density (>500 kcal/100g) due to natural intrinsic oils.",
    "consumer_guidance": "Nutrient-dense whole food. Consume in controlled portions (e.g. 15-30g daily).",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97"
    }
  },
  {
    "matrix_id": "icmr_matrix_b1",
    "cell_code": "B1",
    "processing_group": "GROUP_B",
    "nutritional_category": "CAT_1",
    "applicable_food_form": "solid",
    "is_upf": false,
    "is_hfss": false,
    "energy_min_kcal": null,
    "energy_max_kcal": 250.0,
    "processing_description": "Processed culinary ingredients or cooked foods using culinary additives (e.g. salted canned vegetables, tomato puree with salt/citric acid).",
    "nutritional_description": "Low calorific density (<=250 kcal/100g).",
    "consumer_guidance": "Suitable culinary ingredient. Monitor added salt or culinary seasoning.",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97"
    }
  },
  {
    "matrix_id": "icmr_matrix_b2",
    "cell_code": "B2",
    "processing_group": "GROUP_B",
    "nutritional_category": "CAT_2",
    "applicable_food_form": "solid",
    "is_upf": false,
    "is_hfss": true,
    "energy_min_kcal": 250.0,
    "energy_max_kcal": 500.0,
    "processing_description": "Processed traditional foods cooked with culinary fat or sugar (e.g. freshly baked plain bread, homemade snack mixes).",
    "nutritional_description": "Moderate calorific density (>250 to 500 kcal/100g) due to added culinary fats/sugar.",
    "consumer_guidance": "Consume in moderation. Limit frequency of foods with added culinary sugar and fat.",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97"
    }
  },
  {
    "matrix_id": "icmr_matrix_b3",
    "cell_code": "B3",
    "processing_group": "GROUP_B",
    "nutritional_category": "CAT_3",
    "applicable_food_form": "solid",
    "is_upf": false,
    "is_hfss": true,
    "energy_min_kcal": 500.0,
    "energy_max_kcal": null,
    "processing_description": "Culinary fats/oils or deep-fried traditional foods (e.g. pure ghee, cold-pressed vegetable oil, traditional savouries).",
    "nutritional_description": "High calorific density (>500 kcal/100g).",
    "consumer_guidance": "High calorie food/fat. Use sparingly as cooking medium in limited amounts.",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97"
    }
  },
  {
    "matrix_id": "icmr_matrix_c1",
    "cell_code": "C1",
    "processing_group": "GROUP_C",
    "nutritional_category": "CAT_1",
    "applicable_food_form": "solid",
    "is_upf": true,
    "is_hfss": false,
    "energy_min_kcal": null,
    "energy_max_kcal": 250.0,
    "processing_description": "Ultra-processed industrial formulation containing cosmetic additives, emulsifiers, or intense sweeteners, but formulated to be low in energy (e.g. reconstituted low-calorie textured snacks, diet solid gel desserts).",
    "nutritional_description": "Low calorific density (<=250 kcal/100g), non-HFSS by calorie criteria.",
    "consumer_guidance": "Ultra-processed food. Non-HFSS by energy criteria, but consume rarely due to industrial processing and synthetic additives.",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 98"
    }
  },
  {
    "matrix_id": "icmr_matrix_c2",
    "cell_code": "C2",
    "processing_group": "GROUP_C",
    "nutritional_category": "CAT_2",
    "applicable_food_form": "solid",
    "is_upf": true,
    "is_hfss": true,
    "energy_min_kcal": 250.0,
    "energy_max_kcal": 500.0,
    "processing_description": "Ultra-processed food with industrial deconstruction and cosmetic additives (e.g. reconstituted breakfast cereals with flavourings, commercial biscuits, snack bars).",
    "nutritional_description": "Moderate calorific density (>250 to 500 kcal/100g) combined with ultra-processing.",
    "consumer_guidance": "Ultra-processed and HFSS. Limit consumption; linked to metabolic health risks.",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 98"
    }
  },
  {
    "matrix_id": "icmr_matrix_c3",
    "cell_code": "C3",
    "processing_group": "GROUP_C",
    "nutritional_category": "CAT_3",
    "applicable_food_form": "solid",
    "is_upf": true,
    "is_hfss": true,
    "energy_min_kcal": 500.0,
    "energy_max_kcal": null,
    "processing_description": "Ultra-processed food of highest concern: industrial matrix deconstruction, cosmetic additives, and high fat/sugar content (e.g. commercial extruded potato chips, chocolate confectionery, filled cream biscuits).",
    "nutritional_description": "High calorific density (>500 kcal/100g) driven by industrial fats and refined carbohydrates.",
    "consumer_guidance": "High-risk UPF and HFSS food. Avoid or consume very rarely.",
    "statutory_provenance": {
      "source_name": "ICMR-NIN",
      "citation": "Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 98"
    }
  }
]
```

---

## 4. Seed Schema 3: FSSAI Schedule I Claims

### 4.1 Schema Definition
Matches `RegulatoryClaimRule` and `ClaimConditionGroup` AST schema (`claim_ast_schema.py`).
```json
{
  "claim_id": "fssai_claim_trans_fat_free_solid",
  "claim_code": "TRANS_FAT_FREE",
  "claim_title": "Trans Fat Free (Solids)",
  "claim_family": "NUTRIENT_CONTENT_CLAIM",
  "food_form": "solid",
  "applicable_category": "ALL",
  "condition_expression": {
    "logical_operator": "AND",
    "conditions": [
      {
        "type": "NUTRIENT_THRESHOLD",
        "nutrient_code": "trans_fat",
        "operator": "LT",
        "threshold_value": 0.2,
        "measurement_basis": "PER_100G"
      },
      {
        "type": "NUTRIENT_THRESHOLD",
        "nutrient_code": "saturated_fat",
        "operator": "LTE",
        "threshold_value": 1.5,
        "measurement_basis": "PER_100G"
      },
      {
        "type": "ENERGY_PERCENTAGE",
        "nutrient_code": "saturated_fat",
        "operator": "LTE",
        "threshold_value": 10.0,
        "measurement_basis": "PCT_TOTAL_ENERGY"
      }
    ]
  },
  "fssai_regulation_reference": "FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(b)",
  "official_source_version": "Version III (04-10-2022)",
  "effective_from": "2019-07-01",
  "consumer_explanation": "Contains strictly less than 0.2g trans fat per 100g, and low saturated fat (<=1.5g and <=10% energy)."
}
```

---

## 5. Seed Schema 4: FSSAI Schedule II Authorized Synonyms

Schedule II synonyms are kept in a separate lookup registry mapping official claim codes to legally authorized synonym phrases.

```json
{
  "TRANS_FAT_FREE": [
    "Zero Trans Fat",
    "No Trans Fat",
    "Trans Fatty Acid Free",
    "Free of Trans Fat"
  ],
  "SOURCE_OF_PROTEIN": [
    "Provides Protein",
    "With Protein",
    "Contains Protein"
  ],
  "HIGH_PROTEIN": [
    "Rich in Protein",
    "Protein Rich",
    "Excellent Source of Protein"
  ],
  "LOW_SUGARS": [
    "Low Sugar",
    "Little Sugar"
  ],
  "NO_ADDED_SUGARS": [
    "No Added Sugar",
    "Without Added Sugar",
    "Zero Added Sugar"
  ]
}
```

---

## 6. Seed Schema 5: Ingredient Statutory Safety & Warning Rules

```json
[
  {
    "rule_id": "ir_aspartame_pku_warning",
    "ingredient_code": "ins_951_aspartame",
    "rule_type": "MANDATORY_LABEL_WARNING",
    "target_food_category": "ALL",
    "max_permitted_ppm": null,
    "warning_statement": "CONTAINS ASPARTAME. NOT RECOMMENDED FOR PHENYLKETONURICS.",
    "condition_expression": null,
    "regulatory_reference": "FSSAI (Labelling and Display) Regulations 2020, Schedule II, Entry 1",
    "consumer_guidance": "Aspartame metabolizes into phenylalanine. Phenylketonurics must avoid."
  },
  {
    "rule_id": "ir_polyols_laxative_warning",
    "ingredient_code": "ins_965_maltitol",
    "rule_type": "MANDATORY_LABEL_WARNING",
    "target_food_category": "ALL",
    "max_permitted_ppm": null,
    "warning_statement": "Polyols may produce laxative effects.",
    "condition_expression": null,
    "regulatory_reference": "FSSAI (Labelling and Display) Regulations 2020, Schedule II, Entry 4",
    "consumer_guidance": "Excessive consumption of sugar alcohols (polyols) can cause gastrointestinal discomfort."
  },
  {
    "rule_id": "ir_benzoate_max_limit_beverages",
    "ingredient_code": "ins_211_sodium_benzoate",
    "rule_type": "MAX_PERMISSIBLE_LIMIT",
    "target_food_category": "BEVERAGE",
    "max_permitted_ppm": 120.0,
    "warning_statement": null,
    "condition_expression": null,
    "regulatory_reference": "FSSAI (Food Products Standards and Food Additives) Regulations 2011, Appendix A, Table 3",
    "consumer_guidance": "Preservative limited to a maximum of 120 ppm in water-based flavoured drinks."
  }
]
```

---

## 7. Legal Provenance, Licensing & Commercial Distribution Governance

> [!WARNING]
> **COPYRIGHT & RE-DISTRIBUTION RESTRICTIONS**
> 1. **ICMR-NIN DGI 2024**: Copyright Reserved by Director, ICMR - National Institute of Nutrition, Hyderabad. Commercial distribution or incorporation into proprietary commercial SaaS products requires prior written permission.
> 2. **WHO South-East Asia Nutrient Profile Model (2017)**: Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0 IGO (CC BY-NC-SA 3.0 IGO). Must NOT be commercialized without a specific license agreement with WHO.
> 3. **FSSAI Statutory Gazettes**: Official Government of India statutory instruments published under the Food Safety and Standards Act, 2006. Public statutory law.

