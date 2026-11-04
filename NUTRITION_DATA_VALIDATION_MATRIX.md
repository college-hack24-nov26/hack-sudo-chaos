# YumSure Nutrition Data Validation Matrix

**Scope**: Curated Demonstration Food Catalog & Verified Commercial Retail Packaged Items  
**Standard**: FSSAI (Labelling & Display) Regulations 2020 & ICMR-NIN 2020 RDA Standards  
**Maintained By**: Abhishek (Nutrition Integrity & Evaluation Domain Lead)  
**Verification Date**: November 4, 2026

---

## 1. Overview

This matrix documents the calibrated baseline nutritional values across all core demonstration and reference packaged products in YumSure. Every declared nutrient is mapped with its canonical slug, measurement unit, reference basis, per-100g/ml quantity, per-serving quantity, 4-state data status, and photographic packaging evidence source.

---

## 2. Product 1: Britannia Nutri-Choice Digestive Biscuits

- **Commercial Barcode**: `8901063142015` (100g pack) / `8901063142022` (200g pack)
- **Demo Barcode Fixture**: `8901030383701` (Internal Hackathon Fixture calibrated from `8901063142015`)
- **Brand**: Britannia Industries Ltd.
- **Category**: Biscuits & Bakery (Solid)
- **Pack Size**: 100g
- **Serving Size**: 25.0 g (approx. 2 biscuits)
- **Data Source**: Open Food Facts authentic pack scan (`https://images.openfoodfacts.org/images/products/890/106/314/2015/front_en.11.400.jpg`)

| Canonical Slug | Display Name | Unit | Per 100g | Per Serving (25g) | Status | Basis | ICMR/FSSAI Threshold Classification |
|---|---|---|---|---|---|---|---|
| `energy` | Energy | kcal | 482.0 | 120.5 | `PRESENT` | `PER_100G` | Reference (Atwater sum: 481.6 kcal) |
| `protein` | Protein | g | 8.0 | 2.0 | `PRESENT` | `PER_100G` | Moderate (Source of Protein, $\ge 5.4\text{g}$) |
| `carbohydrates` | Carbohydrates | g | 68.0 | 17.0 | `PRESENT` | `PER_100G` | Reference carbohydrate total |
| `total_sugars` | Total Sugars | g | 14.5 | 3.63 | `PRESENT` | `PER_100G` | Moderate |
| `added_sugars` | Added Sugars | g | 13.0 | 3.25 | `PRESENT` | `PER_100G` | **High** (Exceeds ICMR threshold of 10g/100g) |
| `total_fat` | Total Fat | g | 21.0 | 5.25 | `PRESENT` | `PER_100G` | **High** (Exceeds ICMR threshold of 17.5g/100g) |
| `saturated_fat` | Saturated Fat | g | 10.0 | 2.5 | `PRESENT` | `PER_100G` | **High** (Exceeds ICMR threshold of 5.0g/100g) |
| `trans_fat` | Trans Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100G` | **Low / Positive** (Trans Fat Free $\le 0.2\text{g}$) |
| `sodium` | Sodium | mg | 450.0 | 112.5 | `PRESENT` | `PER_100G` | Moderate (Under ICMR threshold of 600mg) |
| `dietary_fibre` | Dietary Fibre | g | 6.2 | 1.55 | `PRESENT` | `PER_100G` | **High / Positive** (High Fibre $\ge 6.0\text{g}$) |

---

## 3. Product 2: Maggi 2-Minute Masala Instant Noodles

- **Barcode**: `8901058860002` (and `8901058851298`)
- **Brand**: Nestlé India Ltd.
- **Category**: Instant Noodles & Pasta (Solid)
- **Pack Size**: 70g
- **Serving Size**: 70.0 g (1 cake + tastemaker)
- **Data Source**: Open Food Facts record (`https://images.openfoodfacts.org/images/products/890/105/885/2899/front_en.15.400.jpg`)

| Canonical Slug | Display Name | Unit | Per 100g | Per Serving (70g) | Status | Basis | ICMR/FSSAI Threshold Classification |
|---|---|---|---|---|---|---|---|
| `energy` | Energy | kcal | 427.0 | 298.9 | `PRESENT` | `PER_100G` | Atwater sum: 427.3 kcal |
| `protein` | Protein | g | 8.0 | 5.6 | `PRESENT` | `PER_100G` | Moderate |
| `carbohydrates` | Carbohydrates | g | 63.5 | 44.45 | `PRESENT` | `PER_100G` | Reference |
| `total_sugars` | Total Sugars | g | 2.2 | 1.54 | `PRESENT` | `PER_100G` | Low |
| `added_sugars` | Added Sugars | g | 1.5 | 1.05 | `PRESENT` | `PER_100G` | Low |
| `total_fat` | Total Fat | g | 15.7 | 10.99 | `PRESENT` | `PER_100G` | Moderate |
| `saturated_fat` | Saturated Fat | g | 6.8 | 4.76 | `PRESENT` | `PER_100G` | **High** (Exceeds 5.0g/100g) |
| `trans_fat` | Trans Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100G` | **Low / Positive** (Trans Fat Free) |
| `sodium` | Sodium | mg | 1060.0 | 742.0 | `PRESENT` | `PER_100G` | **High** (Breaches ICMR 600mg threshold) |
| `dietary_fibre` | Dietary Fibre | g | 3.6 | 2.52 | `PRESENT` | `PER_100G` | Moderate |

---

## 4. Product 3: Kissan Fresh Tomato Ketchup

- **Barcode**: `8901030825279`
- **Brand**: Hindustan Unilever Ltd. (Kissan)
- **Category**: Condiments & Sauces (Liquid)
- **Pack Size**: 500g bottle
- **Serving Size**: 15.0 g
- **Data Source**: Open Food Facts record (`https://images.openfoodfacts.org/images/products/890/103/082/5279/front_en.12.400.jpg`)

| Canonical Slug | Display Name | Unit | Per 100g | Per Serving (15g) | Status | Basis | ICMR/FSSAI Threshold Classification |
|---|---|---|---|---|---|---|---|
| `energy` | Energy | kcal | 133.0 | 19.95 | `PRESENT` | `PER_100G` | Atwater sum: 130.7 kcal |
| `protein` | Protein | g | 1.2 | 0.18 | `PRESENT` | `PER_100G` | Low |
| `carbohydrates` | Carbohydrates | g | 31.0 | 4.65 | `PRESENT` | `PER_100G` | Reference |
| `total_sugars` | Total Sugars | g | 27.0 | 4.05 | `PRESENT` | `PER_100G` | High |
| `added_sugars` | Added Sugars | g | 24.5 | 3.68 | `PRESENT` | `PER_100G` | **High** (Significantly exceeds 10g/100g) |
| `total_fat` | Total Fat | g | 0.1 | 0.02 | `PRESENT` | `PER_100G` | Low |
| `saturated_fat` | Saturated Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100G` | Low |
| `trans_fat` | Trans Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100G` | Low (Trans Fat Free) |
| `sodium` | Sodium | mg | 850.0 | 127.5 | `PRESENT` | `PER_100G` | **High** (Exceeds 600mg threshold) |
| `dietary_fibre` | Dietary Fibre | g | 0.5 | 0.08 | `PRESENT` | `PER_100G` | Low |

---

## 5. Product 4: Haldiram's Aloo Bhujia Spicy Namkeen

- **Barcode**: `8904063200150` (and `8901491101838`)
- **Brand**: Haldiram's
- **Category**: Traditional Namkeen & Snacks (Solid)
- **Pack Size**: 150g
- **Serving Size**: 30.0 g
- **Data Source**: Open Food Facts record (`https://images.openfoodfacts.org/images/products/890/149/110/1838/front_en.8.400.jpg`)

| Canonical Slug | Display Name | Unit | Per 100g | Per Serving (30g) | Status | Basis | ICMR/FSSAI Threshold Classification |
|---|---|---|---|---|---|---|---|
| `energy` | Energy | kcal | 580.0 | 174.0 | `PRESENT` | `PER_100G` | Atwater sum: 578.0 kcal |
| `protein` | Protein | g | 9.0 | 2.7 | `PRESENT` | `PER_100G` | Moderate |
| `carbohydrates` | Carbohydrates | g | 42.0 | 12.6 | `PRESENT` | `PER_100G` | Reference |
| `total_sugars` | Total Sugars | g | 1.5 | 0.45 | `PRESENT` | `PER_100G` | Low |
| `added_sugars` | Added Sugars | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100G` | **Positive** (Zero Added Sugar) |
| `total_fat` | Total Fat | g | 42.0 | 12.6 | `PRESENT` | `PER_100G` | **High** (Extreme breach: 42g vs 17.5g) |
| `saturated_fat` | Saturated Fat | g | 18.0 | 5.4 | `PRESENT` | `PER_100G` | **High** (Extreme breach: 18g vs 5.0g) |
| `trans_fat` | Trans Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100G` | Low (Trans Fat Free) |
| `sodium` | Sodium | mg | 780.0 | 234.0 | `PRESENT` | `PER_100G` | **High** (Exceeds 600mg threshold) |
| `dietary_fibre` | Dietary Fibre | g | 4.0 | 1.2 | `PRESENT` | `PER_100G` | Moderate |

---

## 6. Product 5: Real Fruit Power Mixed Fruit Juice

- **Barcode**: `8901207010497`
- **Brand**: Dabur India Ltd. (Real)
- **Category**: Beverages & Juices (Liquid)
- **Pack Size**: 1000ml tetrapack
- **Serving Size**: 200.0 ml (1 glass)
- **Data Source**: Open Food Facts record (`https://images.openfoodfacts.org/images/products/890/120/701/0497/front_en.10.400.jpg`)

| Canonical Slug | Display Name | Unit | Per 100ml | Per Serving (200ml) | Status | Basis | ICMR/FSSAI Threshold Classification |
|---|---|---|---|---|---|---|---|
| `energy` | Energy | kcal | 56.0 | 112.0 | `PRESENT` | `PER_100ML` | Atwater sum: 55.6 kcal |
| `protein` | Protein | g | 0.4 | 0.8 | `PRESENT` | `PER_100ML` | Low |
| `carbohydrates` | Carbohydrates | g | 13.5 | 27.0 | `PRESENT` | `PER_100ML` | Reference |
| `total_sugars` | Total Sugars | g | 13.0 | 26.0 | `PRESENT` | `PER_100ML` | High |
| `added_sugars` | Added Sugars | g | 11.5 | 23.0 | `PRESENT` | `PER_100ML` | **High** (Significantly exceeds beverage threshold) |
| `total_fat` | Total Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100ML` | Low |
| `saturated_fat` | Saturated Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100ML` | Low |
| `trans_fat` | Trans Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100ML` | Low |
| `sodium` | Sodium | mg | 10.0 | 20.0 | `PRESENT` | `PER_100ML` | Low |
| `dietary_fibre` | Dietary Fibre | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100ML` | Low |

---

## 7. Product 6: Cadbury Bournvita Chocolate Health Drink

- **Barcode**: `8901233024013` (and `8901233023724`)
- **Brand**: Mondelez India Foods Pvt. Ltd. (Cadbury)
- **Category**: Malted Food Drink (Solid Powder)
- **Pack Size**: 500g jar
- **Serving Size**: 20.0 g (approx. 2 spoonfuls)
- **Data Source**: Open Food Facts record (`https://images.openfoodfacts.org/images/products/890/123/302/4013/front_en.5.400.jpg`)

| Canonical Slug | Display Name | Unit | Per 100g | Per Serving (20g) | Status | Basis | ICMR/FSSAI Threshold Classification |
|---|---|---|---|---|---|---|---|
| `energy` | Energy | kcal | 388.0 | 77.6 | `PRESENT` | `PER_100G` | Atwater sum: 388.2 kcal |
| `protein` | Protein | g | 7.0 | 1.4 | `PRESENT` | `PER_100G` | Moderate |
| `carbohydrates` | Carbohydrates | g | 85.2 | 17.04 | `PRESENT` | `PER_100G` | Reference |
| `total_sugars` | Total Sugars | g | 32.0 | 6.4 | `PRESENT` | `PER_100G` | High |
| `added_sugars` | Added Sugars | g | 28.0 | 5.6 | `PRESENT` | `PER_100G` | **High** (Severe breach: 28g vs 10g/100g) |
| `total_fat` | Total Fat | g | 1.8 | 0.36 | `PRESENT` | `PER_100G` | Low |
| `saturated_fat` | Saturated Fat | g | 0.9 | 0.18 | `PRESENT` | `PER_100G` | Low |
| `trans_fat` | Trans Fat | g | 0.0 | 0.0 | `EXPLICITLY_ZERO` | `PER_100G` | Low (Trans Fat Free) |
| `sodium` | Sodium | mg | 150.0 | 30.0 | `PRESENT` | `PER_100G` | Low |
| `dietary_fibre` | Dietary Fibre | g | 1.5 | 0.3 | `PRESENT` | `PER_100G` | Low |

