# YumSure — Nutrition and Regulatory Rules Specification

This document details every rule implemented in YumSure's **Nutritional Interpretation Engine** and **Regulatory Claims Engine**. Every single rule is linked to an official statutory or institutional standard. YumSure does not invent regulatory thresholds.

---

## 1. Reference Standards Overview

| Standard / Authority | Full Statutory Document Citation | Baseline Reference Diet |
| :--- | :--- | :--- |
| **FSSAI Claims** | Food Safety and Standards (Advertising and Claims) Regulations, 2018 (Schedule II & amendments) | Standardized adult daily reference values |
| **FSSAI Labelling** | Food Safety and Standards (Labelling and Display) Regulations, 2020 (Gazette F.No. 1-94/FSSAI/SP(L&C/A)/2009) | Mandatory 8-nutrient declaration panel |
| **ICMR-NIN 2020** | Recommended Dietary Allowances & Nutrient Requirements for Indians (ICMR-NIN Expert Committee 2020) | Reference man/woman daily average (2,000 kcal standardized for consumer labelling) |

---

## 2. ICMR-NIN 2020 Baseline Daily Recommended Allowances (2,000 kcal diet)

- **Energy**: 2,000 kcal
- **Protein**: 54.0 g (Reference average for adults, sedentary)
- **Carbohydrates**: 130.0 g (Minimum requirement; typical diet 275-300g)
- **Total Fat**: 67.0 g (≤ 30% of energy)
- **Saturated Fat**: 22.0 g (< 10% of energy)
- **Trans Fat**: < 2.0 g (< 1% of energy; FSSAI industrial trans-fat cap ≤ 2% total fat)
- **Added Sugars**: 50.0 g (≤ 10% of total daily energy)
- **Sodium**: 2,000.0 mg (Equivalent to 5.0 g sodium chloride / salt)
- **Dietary Fibre**: 30.0 g (Recommended daily intake)

---

## 3. Nutritional Interpretation Rules (Low / Moderate / High)

These rules classify individual nutrient densities per 100g (solids) or 100ml (liquids). They do not generate an overall health score.

### 3.1 Added Sugars
- **Rule ID**: `NIR_SUGAR_SOLID_2020`
- **Rule Name**: Solid Added Sugar Density
- **Nutrient**: Added Sugars
- **Applicable Category**: Solid packaged foods
- **Thresholds**:
  - Low: $\le 5.0\text{ g / 100g}$
  - Moderate: $> 5.0\text{ g}$ and $\le 12.5\text{ g / 100g}$
  - High: $> 12.5\text{ g / 100g}$ (exceeds 25% of single-day added sugar allowance per 100g)
- **Unit**: g per 100g
- **Classification**: Low (Positive/Neutral), Moderate (Neutral), High (Concern)
- **Explanation**: Added sugars provide empty calories without essential micronutrients. High levels increase risk of metabolic disorders.
- **Official Source**: ICMR-NIN 2020 Dietary Guidelines / WHO Sugar Guidelines 2015.
- **Regulatory Reference**: FSSAI Labelling and Display Regulations 2020, Schedule II.
- **Effective Date**: November 2020.
- **Limitations**: Applies only where added sugars are explicitly declared on the label.

- **Rule ID**: `NIR_SUGAR_LIQUID_2020`
- **Rule Name**: Liquid Added Sugar Density
- **Nutrient**: Added Sugars
- **Applicable Category**: Liquid packaged foods / beverages
- **Thresholds**:
  - Low: $\le 2.5\text{ g / 100ml}$
  - Moderate: $> 2.5\text{ g}$ and $\le 6.0\text{ g / 100ml}$
  - High: $> 6.0\text{ g / 100ml}$
- **Unit**: g per 100ml
- **Classification**: Low (Positive/Neutral), Moderate (Neutral), High (Concern)
- **Official Source**: ICMR-NIN 2020 / FSSAI Labelling Regulations 2020.

### 3.2 Sodium
- **Rule ID**: `NIR_SODIUM_SOLID_2020`
- **Rule Name**: Solid Sodium Density
- **Nutrient**: Sodium
- **Applicable Category**: Solid packaged foods
- **Thresholds**:
  - Low: $\le 120.0\text{ mg / 100g}$
  - Moderate: $> 120.0\text{ mg}$ and $\le 600.0\text{ mg / 100g}$
  - High: $> 600.0\text{ mg / 100g}$ (exceeds 30% of daily sodium allowance in 100g)
- **Unit**: mg per 100g
- **Classification**: Low (Positive), Moderate (Neutral), High (Concern)
- **Official Source**: FSSAI Advertising & Claims 2018 (Schedule II) & ICMR-NIN 2020.
- **Limitations**: Natural sodium present in raw ingredients cannot be separated from added sodium unless specified.

- **Rule ID**: `NIR_SODIUM_LIQUID_2020`
- **Rule Name**: Liquid Sodium Density
- **Thresholds**: Low $\le 120\text{ mg/100ml}$, Moderate $> 120\text{ and } \le 300\text{ mg/100ml}$, High $> 300\text{ mg/100ml}$.

### 3.3 Total Fat & Saturated Fat
- **Rule ID**: `NIR_SATFAT_SOLID_2020`
- **Rule Name**: Solid Saturated Fat Density
- **Thresholds**: Low $\le 1.5\text{ g / 100g}$, Moderate $> 1.5\text{ g and } \le 4.0\text{ g / 100g}$, High $> 4.0\text{ g / 100g}$.
- **Classification**: Low (Neutral), Moderate (Neutral), High (Concern).
- **Official Source**: FSSAI Advertising & Claims 2018 & ICMR-NIN 2020.

### 3.4 Dietary Fibre
- **Rule ID**: `NIR_FIBRE_SOLID_2020`
- **Rule Name**: Solid Dietary Fibre Density
- **Thresholds**: Low $< 3.0\text{ g / 100g}$, Moderate $\ge 3.0\text{ g and } < 6.0\text{ g / 100g}$, High $\ge 6.0\text{ g / 100g}$.
- **Classification**: Low (Neutral), Moderate (Positive), High (Positive).
- **Official Source**: FSSAI Advertising & Claims Regulations 2018, Schedule II.

### 3.5 Protein
- **Rule ID**: `NIR_PROTEIN_SOLID_2020`
- **Rule Name**: Solid Protein Density
- **Thresholds**: Low $< 5.4\text{ g / 100g}$ ($< 10\%\text{ RDA}$), Moderate $\ge 5.4\text{ g and } < 10.8\text{ g / 100g}$, High $\ge 10.8\text{ g / 100g}$ ($\ge 20\%\text{ RDA}$).
- **Classification**: Low (Neutral), Moderate (Positive), High (Positive).
- **Official Source**: FSSAI Advertising & Claims Regulations 2018, Schedule II.

---

## 4. Statutory Regulatory Claims Validation (FSSAI 2018 Schedule II)

These rules strictly follow the statutory conditions prescribed by FSSAI for making nutritional claims on packaged foods.

| Claim Code | Claim Title | Food Form | Statutory Threshold Condition | Regulatory Citation | Verification Logic |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CLAIM_SOURCE_PROTEIN_S` | Source of Protein | Solid | $\ge 10\%$ of adult RDA per 100g ($\ge 5.4\text{ g / 100g}$) | FSSAI Claims 2018, Sched. II, Item 3 | PASS if `protein_per_100g >= 5.4` |
| `CLAIM_HIGH_PROTEIN_S` | High Protein | Solid | $\ge 20\%$ of adult RDA per 100g ($\ge 10.8\text{ g / 100g}$) | FSSAI Claims 2018, Sched. II, Item 3 | PASS if `protein_per_100g >= 10.8` |
| `CLAIM_SOURCE_PROTEIN_L` | Source of Protein | Liquid | $\ge 5\%$ of adult RDA per 100ml ($\ge 2.7\text{ g / 100ml}$) | FSSAI Claims 2018, Sched. II, Item 3 | PASS if `protein_per_100ml >= 2.7` |
| `CLAIM_HIGH_PROTEIN_L` | High Protein | Liquid | $\ge 10\%$ of adult RDA per 100ml ($\ge 5.4\text{ g / 100ml}$) | FSSAI Claims 2018, Sched. II, Item 3 | PASS if `protein_per_100ml >= 5.4` |
| `CLAIM_LOW_SUGAR_S` | Low Sugar | Solid | $\le 5.0\text{ g total sugars per 100g}$ | FSSAI Claims 2018, Sched. II, Item 6 | PASS if `sugars_per_100g <= 5.0` |
| `CLAIM_LOW_SUGAR_L` | Low Sugar | Liquid | $\le 2.5\text{ g total sugars per 100ml}$ | FSSAI Claims 2018, Sched. II, Item 6 | PASS if `sugars_per_100ml <= 2.5` |
| `CLAIM_SUGAR_FREE` | Sugar Free | Both | $\le 0.5\text{ g total sugars per 100g or 100ml}$ | FSSAI Claims 2018, Sched. II, Item 6 | PASS if `sugars_per_100 <= 0.5` |
| `CLAIM_NO_ADDED_SUGAR` | No Added Sugar | Both | Added sugars $= 0\text{ g}$ AND no sugar-containing ingredients added | FSSAI Claims 2018, Sched. II, Item 6 | PASS if `added_sugars <= 0.1` AND zero sugar-sweetening ingredients |
| `CLAIM_LOW_FAT_S` | Low Fat | Solid | $\le 3.0\text{ g fat per 100g}$ | FSSAI Claims 2018, Sched. II, Item 1 | PASS if `fat_per_100g <= 3.0` |
| `CLAIM_LOW_FAT_L` | Low Fat | Liquid | $\le 1.5\text{ g fat per 100ml}$ | FSSAI Claims 2018, Sched. II, Item 1 | PASS if `fat_per_100ml <= 1.5` |
| `CLAIM_FAT_FREE` | Fat Free | Both | $\le 0.5\text{ g fat per 100g or 100ml}$ | FSSAI Claims 2018, Sched. II, Item 1 | PASS if `fat_per_100 <= 0.5` |
| `CLAIM_LOW_SAT_FAT_S` | Low Saturated Fat | Solid | $\le 1.5\text{ g sat fat / 100g}$ AND $\le 10\%$ energy from sat fat | FSSAI Claims 2018, Sched. II, Item 2 | PASS if `sat_fat_per_100g <= 1.5` AND `sat_fat_kcal <= 0.10 * energy` |
| `CLAIM_LOW_SODIUM` | Low Sodium | Both | $\le 0.12\text{ g (120 mg) sodium per 100g or 100ml}$ | FSSAI Claims 2018, Sched. II, Item 4 | PASS if `sodium_mg_per_100 <= 120.0` |
| `CLAIM_SODIUM_FREE` | Sodium / Salt Free | Both | $\le 0.005\text{ g (5 mg) sodium per 100g or 100ml}$ | FSSAI Claims 2018, Sched. II, Item 4 | PASS if `sodium_mg_per_100 <= 5.0` |
| `CLAIM_SOURCE_FIBRE_S` | Source of Fibre | Solid | $\ge 3.0\text{ g fibre per 100g}$ or $\ge 1.5\text{ g per 100 kcal}$ | FSSAI Claims 2018, Sched. II, Item 8 | PASS if `fibre_per_100g >= 3.0` |
| `CLAIM_HIGH_FIBRE_S` | High Fibre | Solid | $\ge 6.0\text{ g fibre per 100g}$ or $\ge 3.0\text{ g per 100 kcal}$ | FSSAI Claims 2018, Sched. II, Item 8 | PASS if `fibre_per_100g >= 6.0` |

---

## 5. Missing Data Handling Protocols

1. When a mandatory nutrient (e.g. Trans Fat, Added Sugars) is missing from the packaging record:
   - Status flag set to `NOT_DECLARED`.
   - The engine flags the product with `REGULATORY_NON_COMPLIANCE_POSSIBLE: Mandatory nutrient declaration missing under FSSAI Labelling Regulations 2020`.
   - The claim engine refuses to validate claims dependent on missing data (e.g., cannot certify "Low Saturated Fat" if energy or saturated fat is null).
2. YumSure never interpolates or substitutes default averages for missing nutritional data.

