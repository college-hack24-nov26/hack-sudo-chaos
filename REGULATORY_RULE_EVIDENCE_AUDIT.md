# YumSure Statutory Regulatory & Technical Evidence Audit

**Domain**: Regulatory Compliance, Scientific Provenance, & Rule-Engine Verification  
**Auditor**: Abhishek (Domain Evaluation Core & Rules Engine Lead)  
**Regulatory Standards**: FSSAI (Claims & Advertising) 2018, FSSAI (Labelling & Display) 2020, ICMR-NIN 2020/2024 Dietary Guidelines  
**Date**: November 4, 2026  
**Status**: **100% TRACEABLE & STATUTORILY VERIFIED**

---

## 1. Statutory Claims Audit (FSSAI Regulations, 2018)

### A. Schedule I: Generic Nutrient-Content Claims
Schedule I governs nutrition content claims based on adult Recommended Dietary Allowances (RDA). Schedule I claims **must not be confused with Schedule II conditional claims**.

| Rule ID | Regulation & Schedule | Exact Statutory Threshold | Unit | Measurement Basis | Product Applicability | Verification Evidence Source | Status |
|---|---|---|---|---|---|---|---|
| `fssai_sch1_source_protein` | FSSAI Claims 2018, Sched. I | $\ge 10\%$ of adult RDA per 100g ($\ge 5.4\text{g}$) | g | `PER_100G` | Solid foods | FSSAI Gaz. No. Stds/SP(Ad&Cl)/FSSAI/2017 | **PASS** |
| `fssai_sch1_high_protein` | FSSAI Claims 2018, Sched. I | $\ge 20\%$ of adult RDA per 100g ($\ge 10.8\text{g}$) | g | `PER_100G` | Solid foods | FSSAI Gaz. No. Stds/SP(Ad&Cl)/FSSAI/2017 | **PASS** |
| `fssai_sch1_source_fibre` | FSSAI Claims 2018, Sched. I | $\ge 3.0\text{g}$ per 100g (or $\ge 1.5\text{g}$ per 100 kcal) | g | `PER_100G` | Solid foods | FSSAI Sched. I, Table Entry 3 | **PASS** |
| `fssai_sch1_high_fibre` | FSSAI Claims 2018, Sched. I | $\ge 6.0\text{g}$ per 100g (or $\ge 3.0\text{g}$ per 100 kcal) | g | `PER_100G` | Solid foods | FSSAI Sched. I, Table Entry 3 | **PASS** |
| `fssai_sch1_low_sodium` | FSSAI Claims 2018, Sched. I | $\le 120\text{mg}$ per 100g (or $\le 0.12\text{g}$) | mg | `PER_100G` | Solid foods | FSSAI Sched. I, Table Entry 5 | **PASS** |
| `fssai_sch1_sodium_free` | FSSAI Claims 2018, Sched. I | $\le 5\text{mg}$ per 100g | mg | `PER_100G` | Solid & Liquid | FSSAI Sched. I, Table Entry 5 | **PASS** |

---

### B. Schedule II: Authorized Conditional Claims & Synonyms
Schedule II claims require compound AST validation, ensuring marketing claims are not made on foods high in other detrimental nutrients.

| Rule ID | Regulation & Schedule | Compound Condition / Threshold | Unit | Measurement Basis | Authorized Synonyms | Verification Evidence Source | Status |
|---|---|---|---|---|---|---|---|
| `TRANS_FAT_FREE` | FSSAI Claims 2018, Sched. II | $\text{Trans Fat} \le 0.2\text{g}$ **AND** $\text{Saturated Fat} \le 1.5\text{g}$ (solid) or $\le 0.75\text{g}$ (liquid), **AND** $\le 10\%$ of energy from sat fat | g | `PER_100G` / `PER_100ML` | "Zero Trans Fat", "Free of Trans Fat", "Trans-Fat 0g" | FSSAI 2018 Sched. II Entry 1 | **PASS** |
| `LOW_SATURATED_FAT` | FSSAI Claims 2018, Sched. II | $\le 1.5\text{g}$ per 100g solid (or $\le 0.75\text{g}$ per 100ml liquid) **AND** $\le 10\%$ energy from sat fat | g | `PER_100G` / `PER_100ML` | "Low Sat Fat", "Little Saturated Fat" | FSSAI 2018 Sched. II Entry 2 | **PASS** |
| `NO_ADDED_SUGAR` | FSSAI Claims 2018, Reg. 6(1) | No added mono- or disaccharides, honey, or syrups **AND** naturally present sugars declared | — | Label QUID | "No Added Sugars", "Without Added Sugar" | FSSAI 2018 Reg. 6(1) | **PASS** |

---

## 2. ICMR-NIN Dietary Guidelines Audit (2020 & 2024 Editions)

### A. Table 15.1: High Fat, Sugar, and Salt (HFSS) Thresholds
ICMR Table 15.1 defines statutory dietary thresholds of concern for packaged foods:

| Nutrient Metric | Solid Threshold | Liquid Threshold | Statutory Unit | Basis | Enforcement Logic | Source Reference |
|---|---|---|---|---|---|---|
| **Added Sugar** | $> 10.0\text{ g}$ | $> 5.0\text{ g}$ | g | `PER_100G` / `PER_100ML` | Fails Table 15.1 if exceeded; triggers red High indicator | ICMR-NIN 2024 Dietary Guidelines, Tab. 15.1 |
| **Saturated Fat** | $> 5.0\text{ g}$ | $> 2.5\text{ g}$ | g | `PER_100G` / `PER_100ML` | Fails Table 15.1 if exceeded; triggers red High indicator | ICMR-NIN 2024 Dietary Guidelines, Tab. 15.1 |
| **Sodium / Salt** | $> 600.0\text{ mg}$ | $> 300.0\text{ mg}$ | mg | `PER_100G` / `PER_100ML` | Fails Table 15.1 if exceeded; triggers red High indicator | ICMR-NIN 2024 Dietary Guidelines, Tab. 15.1 |

---

### B. Table 15.2: Nine-Cell Food Processing and Nutrient Classification Matrix
Table 15.2 maps products across two completely independent orthogonal axes:
1. **Processing Classification Axis**:
   - `Group 1`: Unprocessed or minimally processed whole foods (NOVA 1).
   - `Group 2`: Processed culinary ingredients (NOVA 2).
   - `Group 3`: Ultra-processed foods containing industrial fractions, cosmetic colorants, or functional texturizers (NOVA 4).
2. **HFSS Threshold Axis**:
   - `Non-HFSS`: Complies with all Table 15.1 nutrient limits.
   - `HFSS`: Breaches one or more Table 15.1 nutrient limits.

#### Nine-Cell Matrix Independence Audit:
- **`Cell A1`**: Non-UPF, Non-HFSS (e.g. Fresh cut apples, plain roasted gram).
- **`Cell A3`**: Non-UPF, HFSS (e.g. Pure salted butter, plain roasted nuts with added salt).
- **`Cell C1`**: Ultra-processed, Non-HFSS (e.g. Diet cola with cosmetic additives but zero sugar/fat).
- **`Cell C3`**: Ultra-processed, HFSS (e.g. Instant noodles, fried namkeen, commercial cream biscuits).

> [!IMPORTANT]
> **Regulatory Boundary**: Under ICMR Table 15.2 notes, **liquid beverages return `NOT_APPLICABLE` for the Table 15.2 matrix**. The matrix is designated exclusively for solid packaged food items (`test_icmr_liquid_matrix_not_applicable`).

---

## 3. Ingredient and Additive Safety Rules Audit

Implemented under FSSAI (Food Products Standards and Food Additives) Regulations, 2011 & Labelling Regulations, 2020:

| Rule Code | Ingredient / Additive | INS Number | Regulatory Condition & Maximum Limit | Mandatory Advisory Warning Text | Source Regulation |
|---|---|---|---|---|---|
| `ING_ASPARTAME_PKU` | Aspartame (Artificial Sweetener) | INS 951 | Permitted in carbonated waters, chewing gum, confectionery | **"Contains Aspartame. Not recommended for phenylketonurics."** | FSSAI Labelling 2020 Clause 5(3)(b) |
| `ING_CAFFEINE_BEVERAGE` | Caffeine | INS 710 | Maximum permitted limit: $\le 300\text{ ppm}$ in carbonated beverages | **"Contains Caffeine. Not recommended for children, pregnant or lactating women."** | FSSAI Additives 2011 Appendix A |
| `ING_INS_635_FLAVOUR` | Disodium 5'-ribonucleotides | INS 635 | Flavour enhancer for savory snacks, noodles, soups | Functional additive classification (Group 3 Ultra-Processed indicator) | FSSAI Additives 2011 Table 1 |
| `ING_INS_330_CITRIC` | Citric Acid | INS 330 | Acidity regulator permitted under Good Manufacturing Practice (GMP) | Non-cosmetic additive (Group 2 Processed Culinary Ingredient) | FSSAI Additives 2011 GMP Table |

---

## 4. Evaluation Outcome Semantics Traceability

YumSure strictly enforces five deterministic evaluation outcomes:

1. **`PASS`**: Product provides verified declaration fulfilling all statutory conditions.
2. **`FAIL`**: Product provides verified declaration that breaches statutory thresholds.
3. **`INSUFFICIENT_DATA`**: Required nutrient is absent (`NOT_DECLARED`) or unknown (`UNKNOWN`), preventing deterministic evaluation. **Never guesses or defaults to PASS or FAIL**.
4. **`INDETERMINATE`**: AST evaluation exceeded maximum nesting depth ($\text{depth} > 5$) or engine experienced an internal fault.
5. **`NOT_APPLICABLE`**: Rule is outside the statutory scope of the product category (e.g. Table 15.2 matrix on liquid beverages).

