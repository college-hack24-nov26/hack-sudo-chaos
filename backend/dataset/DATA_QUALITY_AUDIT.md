# YumSure — Data Quality Audit & Ingestion Integrity Ledger

**Phase**: Phase 2B (Live Product Data Research & Evidence Validation)  
**Lead Auditor**: Varad (Data Quality & Product Research Lead)  
**Status**: Validated Working Draft — Candidates #1, #2, #3, #4 & #5 Audited  
**Date of Audit**: November 3, 2026  

---

## 1. Proposed Data-Quality Framework: The Six Rigorous Validation Levels

> [!NOTE]
> **Architectural Status**: The six validation levels outlined below represent a **proposed data-quality framework** to ensure strict analytical integrity. They are not yet fully implemented as backend database services.

| Level | Validation Level | Exact Definition | Verification Status in YumSure |
|---|---|---|---|
| **Level 1** | **Barcode Mathematical Validity** | The 13-digit EAN-13 code mathematically satisfies the GS1 Modulo 10 check digit algorithm. | Pre-query mathematical check. Eliminates malformed codes (e.g. `8901030383701`, `8901058860002`, `8901233024013`). |
| **Level 2** | **OFF Database Record Existence** | A record indexed under that barcode exists in Open Food Facts and returns HTTP 200. | Ingested as raw data. `is_verified = False`. |
| **Level 3** | **OFF Photographic Evidence** | Packaging photographs are attached to the record (front, ingredients, nutrition table). | Allows visual cross-checking, but photos can be motion-blurred, cropped, or out-of-focus. |
| **Level 4** | **Independent Physical-Pack Verification** | A YumSure team member physically inspects a commercially purchased retail pack in India. | Confirms label fidelity of the retail batch. *(Not yet conducted for Candidates #1, #2, or #3)*. |
| **Level 5** | **Manufacturer Confirmation** | Product data certified directly by the brand manufacturer via B2B data exchange or official spec sheet. | High trust level for intended formulation. *(Not conducted)*. |
| **Level 6** | **Laboratory Verification** | Chemical analysis in an NABL-accredited food testing lab measuring actual sugars, sodium, and moisture. | Scientific gold standard. Sets `is_verified = True`. *(Not conducted)*. |

> [!CAUTION]
> **Key Distinctions to Maintain**:
> 1. None of Candidates #1, #2, or #3 have been independently verified against an in-hand physical pack (Level 4), confirmed by the manufacturer (Level 5), or lab-tested (Level 6). All three currently exist as **Level 2 records with Level 3 photographic evidence**.
> 2. Country tags in Open Food Facts (e.g. `"India"`, `"France, India"`) are crowd-submitted metadata and do **not** constitute proof of active retail store availability in India today.
> 3. PostgreSQL `JSONB` stores structured JSON (keys, values, arrays, booleans), but does **not** guarantee byte-for-byte preservation of the raw HTTP stream (PostgreSQL normalizes whitespace, key ordering, and duplicate keys during binary parsing).
> 4. Source brand spelling (e.g. `"britannnia"`, `"Maggi"`, empty string) is preserved separately from any proposed normalized display brand (`"Britannia"`, `"Maggi"`, `"Cadbury"`).

---

## 2. Product Audit #1: Britannia NutriChoice Digestive

*(Preserved unchanged: Initial barcode `8901030383701` invalid; verified barcode `8901063142022`, sodium converted from 0.368g to 368mg, brand typo `"britannnia"`, Level 2 record with Level 3 photo evidence).*

---

## 3. Product Audit #2: Maggi 2-Minute Masala Noodles

*(Preserved unchanged: Initial barcode `8901058860002` invalid; verified barcode `8901058851298`, sodium 863mg representing 43.15% of ICMR-NIN 2000mg daily reference intake, energy/carb discrepancy documented and marked for physical verification, nested tastemaker percentages preserved).*

---

## 4. Product Audit #3: Cadbury Bournvita (Indian Retail Variant)

### 4.1 Audit Summary Matrix
- **Initial Candidate Barcode**: `8901233024013` ❌ **STRUCTURALLY INVALID** (Check digit fails GS1 Modulo 10; Returns HTTP 404 in OFF).
- **Verified Open Food Facts Barcode**: `8901233023724` ✅ **STRUCTURALLY VALID** (Check digit 4 confirmed; Returns HTTP 200 in OFF).
- **API Evidence File on Disk**: `C:\Users\Varad\.gemini\antigravity\brain\e3db19ec-8b06-4a06-b7fb-b3d75dae2cff\scratch\product_v3_8901233023724.json` (37,642 bytes).
- **Current Validation Status**: **Level 2 (Database Record Exists)** with **Level 3 Photographic Evidence** (`nutrition_en.7.400.jpg`, `ingredients_en.4.400.jpg`).

---

### 4.2 Mathematical Check Digit Verification for Bournvita
- **Candidate 1 (`8901233024013`)**:
  - Digits 1 to 12: `8 9 0 1 2 3 3 0 2 4 0 1`
  - Sum $= (8 \times 1) + (9 \times 3) + (0 \times 1) + (1 \times 3) + (2 \times 1) + (3 \times 3) + (3 \times 1) + (0 \times 3) + (2 \times 1) + (4 \times 3) + (0 \times 1) + (1 \times 3) = \mathbf{69}$
  - Nearest multiple of 10 is 70. $70 - 69 = \mathbf{1}$.
  - Result: Declared 13th digit is **`3`**. **MATHEMATICALLY INVALID**.
- **Candidate 2 (`8901233023724`)**:
  - Digits 1 to 12: `8 9 0 1 2 3 3 0 2 3 7 2`
  - Sum $= (8 \times 1) + (9 \times 3) + (0 \times 1) + (1 \times 3) + (2 \times 1) + (3 \times 3) + (3 \times 1) + (0 \times 3) + (2 \times 1) + (3 \times 3) + (7 \times 1) + (2 \times 3) = \mathbf{76}$
  - Nearest multiple of 10 is 80. $80 - 76 = \mathbf{4}$.
  - Result: Declared 13th digit is **`4`**. **MATHEMATICALLY VALID**.

---

### 4.3 Quality Assessment Matrix for Cadbury Bournvita

| Quality Dimension | Evaluation | Evidence & Defect Analysis | Ingestion Handling (Proposed) |
|---|---|---|---|
| **1. Barcode Correctness** | ⚠️ Correction Applied | Candidate barcode `8901233024013` failed Modulo 10 (returns 404). Real barcode is `8901233023724` (check digit 4 confirmed). | Update demo catalogue to `8901233023724`. |
| **2. Product Identity** | ✅ Valid | Named `"Cadbury Bournvita"`. Clear match to retail malted food drink powder. | Map to `products.product_name`. |
| **3. Brand Quality** | ⚠️ Incomplete in OFF | Brand key is empty in OFF; brand exists in product name `"Cadbury Bournvita"`. | Normalize display brand to `"Cadbury"`. |
| **4. Serving Size** | ✅ Confirmed | Declared as `"20 g"`. Physical label photo confirms: `"Per (20g) Serve"`. | Parse `serving_size_value = 20.0`, `serving_size_unit = 'g'`. |
| **5. Ingredients Completeness** | ✅ High | Raw text is complete: Malt Extract (44%), Sugar, Cocoa Solids, Milk Solids, Liquid Glucose, Emulsifiers (322, 471), Vitamins, Raising Agent (500(i)), Minerals, Salt. | Store raw string in `products.raw_source_payload`. |
| **6. Allergen Extraction** | ⚠️ OFF Omission | OFF tags only flag `milk`. Raw ingredient text declares `Malt Extract (44%)`. Malt extract must not be automatically classified as a confirmed gluten allergen declaration without formal evaluation. | Preserve raw ingredient text verbatim; mark regulatory allergen interpretation as **pending Abhishek's review**. |
| **7. Energy Discrepancy & Verification** | ⚠️ Discrepancy Flagged | OFF reports `energy-kcal_100g = 383` and `energy-kj_100g = 1639.1`. Converting $1639.1\text{ kJ} / 4.184 \approx \mathbf{391.8\text{ kcal}}$, differing from declared $383\text{ kcal}$ by $+8.8\text{ kcal}$ ($+2.3\%$). Do not describe this as consistent. Photo `nutrition_en.7.400.jpg` confirms label prints `383 kcal` (1639 kJ / 77 kcal / 328 kJ). | Preserve both original source values (`383 kcal` and `1639.1 kJ`) and explicitly flag the discrepancy. |
| **8. Added Sugars Audit** | ⚠️ Crowd vs Label Distinction | OFF raw JSON contains community-sourced `added-sugars = 23.54g`. Physical packaging photograph confirms manufacturer label declared only *Total Sugars (71.1g)* with added sugars omitted. | Preserve OFF's 23.54g in raw source record (do not silently delete); mark added sugars as `NOT_DECLARED` by manufacturer label. |
| **9. Sodium Omission** | ℹ️ Preserved | Salt is declared in ingredients, but sodium/salt row is **completely omitted from the nutrition table**. | Store `sodium` as `NOT_DECLARED`. Never assume 0. Avoids falsely reporting Bournvita as sodium-free. |
| **10. Dietary Fibre Omission** | ℹ️ Preserved | Dietary fibre is omitted from the nutrition table. | Store `dietary_fibre` as `NOT_DECLARED`. Never assume 0. |

---

## 5. Rechecked Backend Relational Mapping for Bournvita

The proposed mapping strictly targets the actual SQLAlchemy models defined in `backend/app/models/`:

| Open Food Facts Field | Target Table | Target SQLAlchemy Column | Data Type & Constraints | Ingestion Transformation / Handling |
| :--- | :--- | :--- | :--- | :--- |
| `code` | `products` | `barcode` | `String(32)`, Unique, Indexed | Direct mapping (`"8901233023724"`). |
| `product_name` | `products` | `product_name` | `String(255)`, Not Null | Direct mapping (`"Cadbury Bournvita"`). |
| `brands` | `products` | `brand_name` | `String(255)`, Nullable | Normalize to `"Cadbury"`. |
| `quantity` | `products` | `package_size` | `String(100)`, Nullable | Retain raw string or `None` if undeclared. |
| `serving_size` | `products` | `serving_size_value` | `Numeric(10, 2)`, Nullable | `20.0` (confirmed on packaging photo). |
| `serving_size` | `products` | `serving_size_unit` | `String(20)`, Default `'g'` | `"g"` |
| System Normalization Decision | `products` | `food_form` | `String(20)`, Check `solid`/`liquid` | Map to `"solid"` (**normalization decision** based on dry powder product, not directly supplied source fact from OFF). |
| `categories` | `products` | `food_category` | `String(100)`, Nullable | Map to `"Malted Beverage Powder"`. |
| Static key | `products` | `source_id` | `String(50)`, FK to `data_sources` | Map to `"OFF_API_V3"`. |
| Timestamp | `products` | `source_retrieval_date` | `DateTime(timezone=True)` | Record retrieval datetime (`2026-11-03T16:51:14Z`). |
| Entire JSON response | `products` | `raw_source_payload` | `JSONB`, Nullable | **Stores structured JSON response (37.6 KB).** |
| Verification flag | `products` | `is_verified` | `Boolean`, Default `False` | Retain as `False` (Level 2 crowd data). |
| `nutriments["energy-kcal_100g"]` | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `383.0`, `unit = 'kcal'`, `data_status = 'PRESENT'`. |
| `nutriments["energy-kj_100g"]` | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `1639.1`, `unit = 'kJ'`, `data_status = 'PRESENT'`. ($1639.1 / 4.184 \approx 391.8\text{ kcal}$, $+8.8\text{ kcal}$ discrepancy vs $383\text{ kcal}$ flagged; not described as consistent). |
| `nutriments["energy-kcal_serving"]`| `product_nutrients` | `per_serving_value` | `Numeric(10, 3)` | Store `77.0`, `unit = 'kcal'`, `data_status = 'PRESENT'`. |
| `nutriments["sugars_100g"]` | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `71.10`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| `nutriments["sugars_serving"]` | `product_nutrients` | `per_serving_value` | `Numeric(10, 3)` | Store `14.20`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| `nutriments["added-sugars_100g"]` (23.54g in raw JSON) | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Preserve 23.54g in `raw_source_payload` (distinguish community data from label); set `per_100g_value = NULL`, `data_status = 'NOT_DECLARED'` (not declared on manufacturer label). |
| Missing sodium on pack | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Set `per_100g_value = NULL`, `data_status = 'NOT_DECLARED'`. |
| Missing fiber on pack | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Set `per_100g_value = NULL`, `data_status = 'NOT_DECLARED'`. |
| `trans-fat_100g` | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.00`, `unit = 'g'`, `data_status = 'EXPLICITLY_ZERO'`. |
| Ingredients list | `product_ingredients` | Multiple rows | Composite bridge table | Tokenize each ingredient into `sequence_order`. `Malt Extract (44%)` mapped with `declared_percentage = 44.0` (malt extract not auto-classified as gluten allergen). Allergen interpretation is **pending Abhishek's review**. |

---

## 6. Product Audit #4: Balaji Wafers Shing Bhujia — Nimbu Chatka

### 6.1 Audit Summary Matrix
- **Barcode (Declared & Verified)**: `8906010500863` ✅ **STRUCTURALLY VALID** (Check digit 3 confirmed; returns HTTP 200 in OFF).
- **API Evidence File on Disk**: `C:\Users\Varad\.gemini\antigravity\brain\e3db19ec-8b06-4a06-b7fb-b3d75dae2cff\scratch\product_v3_8906010500863.json` (40,249 bytes).
- **Current Validation Status**: **Physical-Pack Verified with Photographic Proof (Level 3 & 4 candidate record)** (`balaji_front.jpg`, `balaji_ingredients.jpg`, `balaji_nutrition.jpg`, `balaji_img2.jpg`).
- **Critical Quality Finding**: Discovered an **unresolved source discrepancy** between the **physical retail pack (24g, 685mg sodium, 9.5g sat fat)** and the **Open Food Facts community record (22g on photo, 1109mg sodium, 11.4g sat fat)** under the identical EAN-13 barcode. Hypotheses such as differing production batches, oil blend changes, or packaging revisions remain unconfirmed without manufacturer evidence. Both datasets are preserved separately.

---

### 6.2 Mathematical Check Digit Verification for Balaji Shing Bhujia
- **Barcode (`8906010500863`)**:
  - Digits 1 to 12: `8 9 0 6 0 1 0 5 0 0 8 6`
  - Odd-position sum: $(8 \times 1) + (0 \times 1) + (0 \times 1) + (0 \times 1) + (0 \times 1) + (8 \times 1) = 16$
  - Even-position sum: $(9 \times 3) + (6 \times 3) + (1 \times 3) + (5 \times 3) + (0 \times 3) + (6 \times 3) = 27 + 18 + 3 + 15 + 0 + 18 = 81$
  - Total Sum $= 16 + 81 = \mathbf{97}$
  - Nearest higher multiple of 10 is 100. $100 - 97 = \mathbf{3}$.
  - Result: Declared 13th digit is **`3`**. **MATHEMATICALLY VALID**.

---

### 6.3 Quality Assessment Matrix for Balaji Shing Bhujia

| Quality Dimension | Evaluation | Evidence & Defect Analysis | Ingestion Handling (Proposed) |
|---|---|---|---|
| **1. Barcode Correctness** | ✅ Valid | Barcode `8906010500863` strictly satisfies GS1 Modulo 10 (check digit 3 confirmed; returns HTTP 200). | Ingest directly into `products.barcode`. |
| **2. Product Identity** | ✅ Valid | Physical pack: `Balaji Wafers Shing Bhujia — Nimbu Chatka`. OFF: `Shing Bhujiya - Nimbu Chatka`. | Map to `products.product_name`. |
| **3. Brand Quality** | ✅ Valid | Brand is `Balaji Wafers`. Manufacturer is `Balaji Wafers Pvt. Ltd.`, Rajkot, Gujarat. | Normalize display brand to `Balaji Wafers`. |
| **4. Net Weight vs Serving Size** | ⚠️ Serving-Size Proportion | Physical pack net weight is **24g**, while declared serving size is **20g**. Whole pack contains **1.2 times (20% more than)** one declared serving. | Preserve both: `package_size = '24g'`, `serving_size_value = 20.0, serving_size_unit = 'g'`. Reconcile per-serving and whole-pack figures (clearly marked as derived calculations). |
| **5. Ingredients Completeness** | ✅ High | Raw text complete: Peanut (70%), chickpea flour (13%), edible vegetable oil (palmolein, rice bran, corn, cottonseed), corn flour, black gram flour, seasoning with spices, dehydrated lemon (0.3%), HVP (soya), yeast extract, INS 330, 627, 631, 551. | Store raw string in `products.raw_source_payload`. Tokenize ingredients with declared percentages. |
| **6. Allergen Extraction** | ✅ Source Agreement | Physical pack states: `CONTAINS PEANUT & SOY`. OFF tags: `['en:peanuts', 'en:soybeans']`. Source agreement observed. | Store allergens linked to Peanuts and Soybeans. Source agreement alone does not prove regulatory compliance; formal interpretation remains **pending Abhishek's review**. |
| **7. Nutritional Completeness** | ✅ Sharp Photo Proof | Physical pack declares: 624 kcal, 20.4g protein, 30.6g carbs, 3.5g sugars, 3.0g added sugars, 12.0g fibre, 44.0g fat, 9.5g sat fat, 0.1g trans fat, <1mg cholesterol, 685mg sodium. | Store physical-label values with high confidence as ground truth. Clearly distinguish derived calculations from label declarations. |
| **8. Sodium Source Discrepancy** | 🚨 Unresolved Source Discrepancy | Physical pack declares **`685 mg` sodium**. OFF record reports **`1109 mg` sodium** ($+424\text{ mg}$ difference). Reformulation or batch variation are hypotheses, not confirmed facts. | Preserve physical-pack value `685mg` as verified label truth; retain OFF `1109mg` in raw source payload; document as an unresolved source discrepancy. |
| **9. Saturated Fat Discrepancy** | ⚠️ Unresolved Source Discrepancy | Physical pack declares **`9.5 g` sat fat**. OFF record reports **`11.4 g` sat fat** ($+1.9\text{ g}$ difference). Frying oil changes or batch variations are hypotheses, not confirmed facts. | Preserve physical-pack value `9.5g`; retain OFF `11.4g` in raw source payload; document as an unresolved source discrepancy. |
| **10. Fibre Omission in JSON** | ⚠️ OFF Parser Omission | Dietary fibre (`12.0g` on physical pack; `12.6g` on OFF photo) was completely omitted from OFF JSON nutriments. | Ingest verified physical value `12.0g` as `PRESENT`; avoid marking as missing. |

---

### 6.4 Rechecked Backend Relational Mapping for Balaji Shing Bhujia

The proposed mapping strictly targets the actual SQLAlchemy models defined in `backend/app/models/`:

| Open Food Facts / Label Field | Target Table | Target SQLAlchemy Column | Data Type & Constraints | Ingestion Transformation / Handling |
| :--- | :--- | :--- | :--- | :--- |
| `code` | `products` | `barcode` | `String(32)`, Unique, Indexed | Direct mapping (`"8906010500863"`). |
| `product_name` | `products` | `product_name` | `String(255)`, Not Null | Direct mapping (`"Balaji Wafers Shing Bhujia — Nimbu Chatka"`). |
| `brands` | `products` | `brand_name` | `String(255)`, Nullable | Direct mapping (`"Balaji Wafers"`). |
| Physical pack quantity | `products` | `package_size` | `String(100)`, Nullable | Set to `"24g"` (physical label net weight). |
| Physical pack serving | `products` | `serving_size_value` | `Numeric(10, 2)`, Nullable | `20.0` (declared on physical label). |
| Physical pack serving unit | `products` | `serving_size_unit` | `String(20)`, Default `'g'` | `"g"` |
| System Normalization Decision | `products` | `food_form` | `String(20)`, Check `solid`/`liquid` | Map to `"solid"` (**normalization decision** based on spiced coated peanut savoury). |
| `categories` | `products` | `food_category` | `String(100)`, Nullable | Map to `"Namkeen, Indian Savouries"`. |
| Static key | `products` | `source_id` | `String(50)`, FK to `data_sources` | Map to `"OFF_API_V3"`. |
| Timestamp | `products` | `source_retrieval_date` | `DateTime(timezone=True)` | Record retrieval datetime (`2026-11-03T17:17:01Z`). |
| Entire JSON response | `products` | `raw_source_payload` | `JSONB`, Nullable | **Stores structured JSON response (40.2 KB).** |
| Verification flag | `products` | `is_verified` | `Boolean`, Default `False` | Retain as `False` (pending automated verification pipeline). |
| Physical label Energy (kcal) | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `624.0`, `unit = 'kcal'`, `data_status = 'PRESENT'`. |
| Physical label Protein | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `20.40`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Physical label Carbohydrates | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `30.60`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Physical label Total Sugars | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `3.50`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Physical label Added Sugars | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `3.00`, `unit = 'g'`, `data_status = 'PRESENT'` (declared on pack). |
| Physical label Dietary Fibre | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `12.00`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Physical label Total Fat | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `44.00`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Physical label Saturated Fat | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `9.50`, `unit = 'g'`, `data_status = 'PRESENT'` (OFF batch `11.4g` retained in raw JSON). |
| Physical label Trans Fat | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.10`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Physical label Cholesterol | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Preserve source inequality **`< 1 mg per 100g`** in payload and evidence. Relational limitation noted: numeric SQL column cannot store inequality symbols directly; stored as upper-bound threshold `1.0` or flagged with qualifier in metadata. Do not normalize to an arbitrary exact figure like 0.9mg. |
| Physical label Sodium | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `685.0`, `unit = 'mg'`, `data_status = 'PRESENT'` (OFF batch `1109mg` retained in raw JSON). |
| Ingredients list | `product_ingredients` | Multiple rows | Composite bridge table | Tokenize each ingredient into `sequence_order`. `Peanut (70%)` mapped with `declared_percentage = 70.0`, `Chickpea Flour (13%)` with `13.0`, `Lemon (0.3%)` with `0.3`. Additives INS 330, 627, 631, 551 mapped to `ingredient_rules`. Allergens mapped to Peanuts and Soybeans. |

---

## 7. Product Audit #5: Diet Coke (Indian Market)

> [!CAUTION]
> **Physical Verification Status: UNPERFORMED (`is_verified = False`)**  
> We do not possess the physical packaging (can or bottle) for Diet Coke.  
> Data is established strictly from **official manufacturer disclosures (The Coca-Cola Company / Coca-Cola India portal)**, corroborated by **Open Food Facts API v3 database records** and **retailer catalog listings**.  
> Neither a valid barcode checksum, an Open Food Facts record, nor a retailer listing constitutes physical-label verification.

---

### 7.1 Audit Summary Matrix
- **Investigated Barcodes**:
  - `8901764061103` (330ml Can): ✅ **VALID** (Sum: `77`, check: `3`). Returns HTTP 200 in OFF API v3. **Strongest-Supported Demo Candidate**.
  - `8901764061257` (Can / 4-pack): ✅ **VALID** (Sum: `93`, check: `7`). Returns HTTP 200 in OFF API v3.
  - `8901764062704` (500ml Bottle): ✅ **VALID** (Sum: `86`, check: `4`). Returns HTTP 200 in OFF API v3.
  - `8901764061189` (200ml regular Coke): ✅ **VALID** checksum, but OFF record proves this barcode belongs to regular sugary Coca-Cola. **Disqualified**.
  - `8901764016105`: ❌ **INVALID** checksum (Calculated: 3, declared: 5). **Disqualified**.
- **Primary Ground Truth**: Official Coca-Cola India corporate transparency portal (`coca-cola.com/in/en`). Note: The official portal publishes ingredients, nutrition information, and advisory text, but does not independently verify any specific retail barcode, production batch, manufacturing plant, or physical can.
- **API Evidence File on Disk**: `C:\Users\Varad\.gemini\antigravity\brain\e3db19ec-8b06-4a06-b7fb-b3d75dae2cff\scratch\product_v3_8901764061103.json` (40.2 KB).
- **Retrieval Timestamp**: `2026-11-03T17:45:50Z` (`HTTP 200 OK`).
- **Validation Status**: **Level 5 (Manufacturer Published) + Level 2 (OFF Database Record)**. Physical packaging verification is NOT PERFORMED (`is_verified = False` is the proposed application status; no database record was created or changed).

---

### 7.2 Mathematical Check Digit Verification for Candidate Barcodes

1. **Candidate 1 (`8901764061103` — 330ml Can)**:
   - Digits 1 to 12: `8 9 0 1 7 6 4 0 6 1 1 0`
   - Odd sum: $(8 \times 1) + (0 \times 1) + (7 \times 1) + (4 \times 1) + (6 \times 1) + (1 \times 1) = \mathbf{26}$
   - Even sum: $(9 \times 3) + (1 \times 3) + (6 \times 3) + (0 \times 3) + (1 \times 3) + (0 \times 3) = \mathbf{51}$
   - Sum $= 26 + 51 = \mathbf{77} \implies 80 - 77 = \mathbf{3}$. Declared: `3`. **VALID**.

2. **Candidate 2 (`8901764061257` — 300ml / 250ml Can)**:
   - Digits 1 to 12: `8 9 0 1 7 6 4 0 6 1 2 5`
   - Odd sum: $(8 \times 1) + (0 \times 1) + (7 \times 1) + (4 \times 1) + (6 \times 1) + (2 \times 1) = \mathbf{27}$
   - Even sum: $(9 \times 3) + (1 \times 3) + (6 \times 3) + (0 \times 3) + (1 \times 3) + (5 \times 3) = \mathbf{66}$
   - Sum $= 27 + 66 = \mathbf{93} \implies 100 - 93 = \mathbf{7}$. Declared: `7`. **VALID**.

3. **Candidate 3 (`8901764062704` — 500ml Bottle)**:
   - Digits 1 to 12: `8 9 0 1 7 6 4 0 6 2 7 0`
   - Odd sum: $(8 \times 1) + (0 \times 1) + (7 \times 1) + (4 \times 1) + (6 \times 1) + (7 \times 1) = \mathbf{32}$
   - Even sum: $(9 \times 3) + (1 \times 3) + (6 \times 3) + (0 \times 3) + (2 \times 3) + (0 \times 3) = \mathbf{54}$
   - Sum $= 32 + 54 = \mathbf{86} \implies 90 - 86 = \mathbf{4}$. Declared: `4`. **VALID**.

---

### 7.3 Quality Assessment Matrix for Diet Coke (Indian Market)

| Quality Dimension | Evaluation | Evidence & Defect Analysis | Ingestion Handling (Proposed) |
| :--- | :--- | :--- | :--- |
| **1. Barcode Correctness** | ✅ Validated | Barcodes `8901764061103`, `8901764061257`, `8901764062704` satisfy GS1 Modulo 10. | Assign recommended barcode `8901764061103` to demo product. |
| **2. Product Identity** | ✅ Validated | Official portal: Diet Coke. OFF: Diet Coke (`Coke` / `Coca-Cola`). | Map to `products.product_name = "Diet Coke"`. |
| **3. Brand Quality** | ✅ Validated | Brand: `Coca-Cola` / `Diet Coke`. Bottler in India: Hindustan Coca-Cola Beverages Pvt. Ltd. (HCCB) and franchisees. | Normalize display brand to `Coca-Cola`. |
| **4. Package Variant Selection** | ℹ️ Triangulated | 330ml Can is the strongest-supported demo candidate based on the evidence collected. 500ml PET has fewer corroborating listings; 200ml candidate barcode was misattributed to regular Coke. | Select **330ml Can** as primary demo package variant. |
| **5. Ingredients Completeness** | ✅ High | Official portal declares: Carbonated water, INS 338, INS 331(iii), INS 951, INS 950, INS 211, Caffeine (10mg/100g), INS 150d, natural flavours. Product is described by manufacturer as a "vegetarian product" (preserved as stated, without expanded claims). | Ingest into `product_ingredients` with explicit functional roles. |
| **6. Non-Caloric Sweeteners** | ℹ️ Regulatory Advisory | Aspartame (INS 951) and Acesulfame Potassium (INS 950). Contains statutory advisory for phenylketonurics and pregnant/lactating women. | Flag artificial sweetener blend; create advisory tag in `ingredient_rules` pending Abhishek's review. |
| **7. Nutritional Completeness** | ✅ Verified (Mfr) | Official Coca-Cola India portal: 0 kcal energy (nutrition panel) and "less than 1 Calorie" (product description); displayed 0 kcal is statutory rounding, not proof of absolute zero energy. 0g protein, 0g carbohydrates, 0g total sugars, 0g added sugars, 0g fat, 8.3mg sodium per 100ml. | Ingest official manufacturer values as primary ground truth. |
| **8. OFF Database Entry Quirks** | ⚠️ OFF Schema Anomaly | In OFF record `8901764061103`, nutriments were recorded under `nutriments_prepared` fields rather than `as sold`. In `8901764062704`, energy is erroneously recorded as `0.2 kcal` and sodium as `0 mg`. | Do not silently map `_prepared` fields to ordinary as-sold nutrients; ingestion mapping logic requires developer/architecture review before database import. Disregard crowdsourced `0.2 kcal` entry in favor of official manufacturer disclosure. |
| **9. Sodium Concordance** | ✅ High Concordance | Official portal: **`8.3 mg`**. OFF record `8901764061103` (`sodium_prepared_100g`): **`0.0083 g` = `8.3 mg`**. OFF record `8901764061257`: **`0.0083 g` = `8.3 mg`**. | Store `8.3 mg` with high confidence based on multi-source concordance. |
| **10. Physical Pack Verification** | ❌ Absent | Physical packaging (can or bottle) not in hand. Physical verification is NOT PERFORMED. | Keep `products.is_verified = False` as proposed application status. No database records created or changed. Explicitly highlight unverified gap in judge deck. |

---

### 7.4 Rechecked Backend Relational Mapping for Diet Coke

The proposed mapping strictly targets the actual SQLAlchemy models defined in `backend/app/models/`:

| Source Field | Target Table | Target Column | Data Type & Constraints | Ingestion Value / Transformation |
| :--- | :--- | :--- | :--- | :--- |
| Verified Barcode | `products` | `barcode` | `String(32)`, Unique, Indexed | `"8901764061103"` (330ml Can). |
| Product Name | `products` | `product_name` | `String(255)`, Not Null | `"Diet Coke"` |
| Brand Name | `products` | `brand_name` | `String(255)`, Nullable | `"Coca-Cola"` |
| Package Size | `products` | `package_size` | `String(100)`, Nullable | `"330ml"` |
| Serving Size Value | `products` | `serving_size_value` | `Numeric(10, 2)`, Nullable | `200.0` (manufacturer-published serving information from official portal; a 330ml can represents $1.65 \times 200\text{ml}$ servings by volume; physical can's printed serving was not inspected). |
| Serving Size Unit | `products` | `serving_size_unit` | `String(20)`, Default `'g'` | `"ml"` |
| Normalization Decision | `products` | `food_form` | `String(20)`, Check `solid`/`liquid` | Map to `"liquid"` (**normalization decision** based on carbonated dietary beverage). |
| Food Category | `products` | `food_category` | `String(100)`, Nullable | Map to `"Carbonated Soft Drink, Diet Beverage"`. |
| Static Key | `products` | `source_id` | `String(50)`, FK to `data_sources` | Map to `"MFR_PORTAL_AND_OFF_V3"`. |
| Timestamp | `products` | `source_retrieval_date` | `DateTime(timezone=True)` | Record retrieval datetime (`2026-11-03T17:45:50Z`). |
| Entire JSON response | `products` | `raw_source_payload` | `JSONB`, Nullable | Stores structured JSON response from OFF v3 (40.2 KB). |
| Verification Flag | `products` | `is_verified` | `Boolean`, Default `False` | Retain as **`False`** (physical verification is NOT PERFORMED; no database record was created or changed). |
| Official Energy (kcal) | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.000`, `unit = 'kcal'`, `data_status = 'EXPLICITLY_ZERO'`. |
| Official Protein | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.000`, `unit = 'g'`, `data_status = 'EXPLICITLY_ZERO'`. |
| Official Carbohydrates | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.000`, `unit = 'g'`, `data_status = 'EXPLICITLY_ZERO'`. |
| Official Total Sugars | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.000`, `unit = 'g'`, `data_status = 'EXPLICITLY_ZERO'`. |
| Official Added Sugars | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.000`, `unit = 'g'`, `data_status = 'EXPLICITLY_ZERO'`. |
| Official Total Fat | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.000`, `unit = 'g'`, `data_status = 'EXPLICITLY_ZERO'`. |
| Official Sodium | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `8.300`, `unit = 'mg'`, `data_status = 'PRESENT'`. |
| Ingredients list | `product_ingredients` | Multiple rows | Composite bridge table | Tokenize each ingredient into `sequence_order`: Carbonated Water, Acidity Regulators (INS 338, 331iii), Sweeteners (INS 951, 950), Preservative (INS 211), Caffeine (10mg/100g — preserved in original weight-based units without volume multiplication), Colour (INS 150d). Manufacturer describes product as a "vegetarian product" (preserved as stated, without expanded claims). Statutory advisory for Phenylketonurics ("Contains Aspartame", "Not recommended for children", "No sugar added in the product") linked to `ingredient_rules` pending review. |

---

## 8. Candidate #6: Comprehensive Oreo Product Research & Data Quality Audit (Indian Market)

> [!CAUTION]
> **Physical Verification Status: UNPERFORMED (`is_verified = False`)**  
> We do not possess an unsealed physical retail wrapper for the Indian Oreo products. No physical packaging verification has been conducted.  
> Data is triangulated across **official manufacturer disclosures (Mondelēz International / Cadbury India)**, **Open Food Facts API v3 database records**, and **corroborating Indian quick-commerce / grocery platforms (BigBasket, Blinkit, Zepto, Swiggy Instamart)**.  
> Neither an Open Food Facts database hit nor a commercial retailer listing constitutes physical-label verification.

---

### 8.1 Audit Summary Matrix for Oreo Products in India

- **Investigated Barcodes & Candidate Barcode Reconciliation**:
  - Across the 11 discovered commercial packaging formats (Rows 6A through 6K), there are **exactly 10 unique valid EAN-13 barcode strings**:
    1. `7622201756697` (Oreo Vanilla Crème 43.75g): ✅ **VALID** (Sum: `113`, check: `7`). Returns HTTP 200 in OFF API v3 (`37.8 KB`). **Primary Recommended Demo Candidate**.
    2. `7622201756918` (Cadbury Oreo Vanilla 481.25g / 581.25g): ✅ **VALID** (Sum: `92`, check: `8`). Returns HTTP 200 in OFF API v3 (`36.8 KB`). Corroborating sister batch.
    3. `7622201801878` (Oreo Original 500g): ✅ **VALID** (Sum: `92`, check: `8`). Returns HTTP 200 in OFF API v3 (`37.5 KB`).
    4. `7622201756932` (Cadbury Oreo Choco Crème): ✅ **VALID** (Sum: `98`, check: `2`). Returns HTTP 200 in OFF API v3 (`30.1 KB`). Flagged for catastrophic crowdsource sodium error & missing nutrition photo.
    5. `7622201756789` (Oreo Strawberry Biscuit 43.75g): ✅ **VALID** (Sum: `111`, check: `9`). Returns HTTP 200 in OFF API v3 (`38.1 KB`). Flagged for synthetic azo dye (INS 122).
    6. `8901233031125` (Cadbury Oreo Golden 50g): ✅ **VALID** (Sum: `65`, check: `5`). BigBasket retail listing; returns HTTP 404 in OFF API v3.
    7. `7622201507763` (Cadbury Oreo Dipped 50g): ✅ **VALID** (Sum: `97`, check: `3`). BigBasket retail listing; returns HTTP 404 in OFF API v3.
    8. `8901233011202` (Cadbury Original Oreo 20g): ✅ **VALID** (Sum: `58`, check: `2`). Returns HTTP 200 in OFF API v3 (`30.2 KB`). Incomplete macro profile.
    9. `8901233013091` (Cadbury Oreo Small Pack 50g): ✅ **VALID** (Sum: `89`, check: `1`). Returns HTTP 200 in OFF API v3 (`29.3 KB`). Incomplete macro profile.
    10. `8901233024622` (Cadbury Oreo 60g): ✅ **VALID** (Sum: `78`, check: `2`). Returns HTTP 200 in OFF API v3 (`12.6 KB`). Missing ingredients/nutrition.
  - **Disqualified Non-Barcode & Invalid Entries (Excluded from Barcode Count)**:
    - `7622201525928` (Cadbury Oreo Dipped 150g Listing): ❌ **INVALID** (Calculated check digit: `7`, declared: `8`). BigBasket typographical error. **Disqualified**.
    - Retail SKU `40242232` (Cadbury Oreo Red Velvet 60g): Internal retailer SKU, not an EAN-13 barcode. **Disqualified**.
  - **Additional Barcodes Evaluated in Broad OFF Search Audit (Non-Catalogue)**:
    - `2296637125669` (Oreo 43.75g): ✅ **VALID** (Sum: `101`, check: `9`), but begins with prefix `22` (GS1 internal / restricted distribution prefix). Disqualified from primary recommendation.
    - `7622201464486` (Oreo 7-pack): ✅ **VALID** (Sum: `94`, check: `6`). Returns HTTP 200 in OFF API v3 (`19.0 KB`). Incomplete packaging/ingredient text.
  - *(Crucial Counting Distinction: Commercial package format rows [11] do not equal unique valid barcode count [10], because row 6B encompasses two distinct barcodes, while rows 6G and 6H contain an invalid checksum and an internal retailer SKU respectively).*
- **Primary Ground Truth**: Official Mondelēz International / Cadbury India product packaging specifications and corroborated Level 3 photographic records from Open Food Facts community uploads.
- **API Evidence Files on Disk**:
  - `product_v3_7622201756697.json` (37.8 KB, HTTP 200)
  - `product_v3_7622201756789.json` (38.1 KB, HTTP 200)
  - `product_v3_7622201756918.json` (36.8 KB, HTTP 200)
  - `product_v3_7622201756932.json` (30.1 KB, HTTP 200)
  - `product_v3_7622201801878.json` (37.5 KB, HTTP 200)
  - `product_v3_8901233013091.json` (29.3 KB, HTTP 200)
  - `product_v3_8901233011202.json` (30.2 KB, HTTP 200)
  - `product_v3_8901233024622.json` (12.6 KB, HTTP 200)
- **Retrieval Timestamp**: `2026-11-03T18:10:45Z` (`HTTP 200 OK`).
- **Validation Status**: **Level 2 (OFF Database Record) + Level 3 (Packaging Photographs) + Retailer Platform Triangulation**. Physical packaging verification is NOT PERFORMED (`is_verified = False`). Community photographs provide visual corroboration but are not equivalent to in-hand physical packaging verification.

---

### 8.2 Detailed Mathematical Check Digit Verification for Oreo Barcodes

Every discovered barcode was evaluated via the official GS1 Modulo 10 algorithm:

1. **`7622201756697` (Vanilla Crème 43.75g — Recommended Demo Candidate)**:
   - Digits 1 to 12: `7 6 2 2 2 0 1 7 5 6 6 9`
   - Odd sum (digits 1, 3, 5, 7, 9, 11): $(7 \times 1) + (2 \times 1) + (2 \times 1) + (1 \times 1) + (5 \times 1) + (6 \times 1) = \mathbf{23}$
   - Even sum (digits 2, 4, 6, 8, 10, 12): $(6 \times 3) + (2 \times 3) + (0 \times 3) + (7 \times 3) + (6 \times 3) + (9 \times 3) = 18 + 6 + 0 + 21 + 18 + 27 = \mathbf{90}$
   - Total Sum $= 23 + 90 = \mathbf{113}$
   - Nearest higher multiple of 10 is 120. $120 - 113 = \mathbf{7}$. Declared check digit: `7`. **MATHEMATICALLY VALID**.

2. **`7622201756789` (Strawberry Crème 43.75g)**:
   - Digits 1 to 12: `7 6 2 2 2 0 1 7 5 6 7 8`
   - Odd sum: $(7) + (2) + (2) + (1) + (5) + (7) = \mathbf{24}$
   - Even sum: $(6 \times 3) + (2 \times 3) + (0 \times 3) + (7 \times 3) + (6 \times 3) + (8 \times 3) = 18 + 6 + 0 + 21 + 18 + 24 = \mathbf{87}$
   - Total Sum $= 24 + 87 = \mathbf{111} \implies 120 - 111 = \mathbf{9}$. Declared: `9`. **MATHEMATICALLY VALID**.

3. **`7622201756932` (Choco Crème)**:
   - Digits 1 to 12: `7 6 2 2 2 0 1 7 5 6 9 3`
   - Odd sum: $(7) + (2) + (2) + (1) + (5) + (9) = \mathbf{26}$
   - Even sum: $(6 \times 3) + (2 \times 3) + (0 \times 3) + (7 \times 3) + (6 \times 3) + (3 \times 3) = 18 + 6 + 0 + 21 + 18 + 9 = \mathbf{72}$
   - Total Sum $= 26 + 72 = \mathbf{98} \implies 100 - 98 = \mathbf{2}$. Declared: `2`. **MATHEMATICALLY VALID**.

4. **`8901233031125` (Cadbury Oreo Golden 50g — BigBasket Listing)**:
   - Digits 1 to 12: `8 9 0 1 2 3 3 0 3 1 1 2`
   - Odd sum: $(8) + (0) + (2) + (3) + (3) + (1) = \mathbf{17}$
   - Even sum: $(9 \times 3) + (1 \times 3) + (3 \times 3) + (0 \times 3) + (1 \times 3) + (2 \times 3) = 27 + 3 + 9 + 0 + 3 + 6 = \mathbf{48}$
   - Total Sum $= 17 + 48 = \mathbf{65} \implies 70 - 65 = \mathbf{5}$. Declared: `5`. **MATHEMATICALLY VALID**.

5. **`7622201507763` (Cadbury Oreo Dipped 50g)**:
   - Digits 1 to 12: `7 6 2 2 2 0 1 5 0 7 7 6`
   - Odd sum: $(7) + (2) + (2) + (1) + (0) + (7) = \mathbf{19}$
   - Even sum: $(6 \times 3) + (2 \times 3) + (0 \times 3) + (5 \times 3) + (7 \times 3) + (6 \times 3) = 18 + 6 + 0 + 15 + 21 + 18 = \mathbf{78}$
   - Total Sum $= 19 + 78 = \mathbf{97} \implies 100 - 97 = \mathbf{3}$. Declared: `3`. **MATHEMATICALLY VALID**.

6. **`7622201525928` (Cadbury Oreo Dipped 150g — BigBasket Malformed Listing)**:
   - Digits 1 to 12: `7 6 2 2 2 0 1 5 2 5 9 2`
   - Odd sum: $(7) + (2) + (2) + (1) + (2) + (9) = \mathbf{23}$
   - Even sum: $(6 \times 3) + (2 \times 3) + (0 \times 3) + (5 \times 3) + (5 \times 3) + (2 \times 3) = 18 + 6 + 0 + 15 + 15 + 6 = \mathbf{60}$
   - Total Sum $= 23 + 60 = \mathbf{83} \implies 90 - 83 = \mathbf{7}$.
   - Declared check digit on BigBasket: `8`! **❌ INVALID EAN-13 CHECKSUM**. Disqualified from catalogue.

---

### 8.3 Quality Assessment Matrix for Discovered Oreo Variants

| Quality Dimension | Evaluation | Evidence & Defect Analysis | Ingestion Handling (Proposed) |
| :--- | :--- | :--- | :--- |
| **1. Barcode Correctness** | ⚠️ Mixed Validity | Exactly **10 unique valid EAN-13 barcodes** identified across candidate records (`7622201756697`, `7622201756918`, `7622201801878`, `7622201756932`, `7622201756789`, `8901233031125`, `7622201507763`, `8901233011202`, `8901233013091`, `8901233024622`). BigBasket listing `7622201525928` fails check digit calculation; retailer SKU `40242232` excluded from barcode count. | Accept 10 validated barcodes; reject malformed BigBasket barcode `7622201525928` and exclude non-EAN internal SKU `40242232`. |
| **2. Dual GS1 Namespace** | ℹ️ Architectural Reality | Mondelez products in India use both national `8901233` (Cadbury India) and global `7622201` (Mondelez Switzerland). | Schema must support both `890` and non-`890` prefixes for valid Indian retail products. |
| **3. Catastrophic Crowdsource Unit Error & Missing Photo** | ❌ Severe OFF Defect | In `7622201756932` (Choco Crème), contributor recorded `420 g` sodium instead of `420 mg`, resulting in $420\text{ g}$ sodium and $1050\text{ g}$ salt per 100g. **Critical Evidence Finding**: Record `7622201756932` contains **no nutrition panel photograph**. The $420\text{ mg}$ value is an extrapolated inference from sister Vanilla/Strawberry records, NOT directly photo-derived for Choco Crème. | Reject crowdsourced value via automated sanity check ($> 5000\text{ mg/100g}$ threshold); retain $420\text{ mg}$ strictly as an unverified candidate with missing variant photograph limitation. Raw payload preserved. |
| **4. Salt vs Sodium Derivation Defect** | ⚠️ OFF Derivation Bug | In `7622201756697`, contributor entered `0.42 g` as salt, causing OFF to misderive sodium as `0.168 g` ($168\text{ mg}$). Attached photo `nutrition_en.5.400.jpg` (Image ID `2`, uploader `dhinesh0097`) is present, but independent legibility audit is constrained offline. Sister record `7622201756918` (`nutrition_en.10.400.jpg`) explicitly declares $420\text{ mg}$ sodium per 100g and $71.4\text{ mg}$ per 17g serving. Physical packaging has not been inspected. | Flag for developer review; reconcile candidate sodium to $420\text{ mg}$ with documentation of contributor entry confusion. Retain candidate as unverified; raw payload preserved. |
| **5. Energy Calculation Discrepancy** | ℹ️ Minor Discrepancy | Declared kJ ($2059.9\text{ kJ}$) yields $492.3\text{ kcal}$ ($+9.3\text{ kcal}$ over declared $483\text{ kcal}$). Atwater 4-4-9 calculation yields $484.8\text{ kcal}$ ($< 0.4\%$ variance). Discrepancy remains unresolved. | Preserve declared $483\text{ kcal}$ and $2059.9\text{ kJ}$ separately; document conversion variance without silently overriding either value. |
| **6. Added Sugars Completeness** | ✅ High Quality | OFF record `7622201756697` explicitly captures $38.7\text{g}$ added sugars (out of $38.8\text{g}$ total sugars). | Nutritional fields reported in the available product record. Physical label verification and regulatory compliance assessment have not been performed. |
| **7. Additive & Colour Transparency** | ✅ Verified | Strawberry Crème discloses synthetic azo dye INS 122 (Carmoisine). Dipped discloses INS 476 (PGPR) and INS 422. Red Velvet discloses INS 162 (Beetroot Red). | Map to `product_ingredients` and trigger dietary/additive rules. Regulatory compliance assessment has not been performed. |
| **8. Physical Pack Verification** | ❌ Absent | No physical pack in hand. Level 4 verification is NOT PERFORMED. | Retain `is_verified = False` as proposed application schema status. |

---

### 8.4 Proposed Backend Relational Mapping for Primary Oreo Candidate (`7622201756697`)

The proposed mapping strictly targets the actual SQLAlchemy models defined in `backend/app/models/`:

| Source Field | Target Table | Target Column | Data Type & Constraints | Ingestion Value / Transformation |
| :--- | :--- | :--- | :--- | :--- |
| Verified Barcode | `products` | `barcode` | `String(32)`, Unique, Indexed | `"7622201756697"` (Vanilla Crème 43.75g). |
| Product Name | `products` | `product_name` | `String(255)`, Not Null | `"Oreo Vanilla Crème Sandwich Biscuits"` |
| Brand Name | `products` | `brand_name` | `String(255)`, Nullable | `"Cadbury Oreo"` |
| Package Size | `products` | `package_size` | `String(100)`, Nullable | `"43.75g"` |
| Serving Size Value | `products` | `serving_size_value` | `Numeric(10, 2)`, Nullable | `17.0` (reported serving size in product record; physical label has not been inspected). |
| Serving Size Unit | `products` | `serving_size_unit` | `String(20)`, Default `'g'` | `"g"` |
| Normalization Decision | `products` | `food_form` | `String(20)`, Check `solid`/`liquid` | Map to `"solid"` (**normalization decision** based on baked composite biscuit). |
| Food Category | `products` | `food_category` | `String(100)`, Nullable | Map to `"Biscuits and Cookies, Cream Filled"`. |
| Static Key | `products` | `source_id` | `String(50)`, FK to `data_sources` | Map to `"OPEN_FOOD_FACTS_V3"`. |
| Timestamp | `products` | `source_retrieval_date` | `DateTime(timezone=True)` | Record retrieval datetime (`2026-11-03T18:10:45Z`). |
| Entire JSON response | `products` | `raw_source_payload` | `JSONB`, Nullable | Stores structured JSON response from OFF v3 (37.8 KB). Raw source values preserved without alteration. |
| Verification Flag | `products` | `is_verified` | `Boolean`, Default `False` | Retain as **`False`** (physical verification is NOT PERFORMED; no database record was created or changed). |
| Energy (kcal) | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `483.000`, `unit = 'kcal'`, `data_status = 'PRESENT'`. |
| Protein | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `5.200`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Carbohydrates | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `71.900`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Total Sugars | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `38.800`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Added Sugars | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `38.700`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Total Fat | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `19.600`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Saturated Fat | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `9.700`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Trans Fat | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `0.100`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Dietary Fibre | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `3.000`, `unit = 'g'`, `data_status = 'PRESENT'`. |
| Candidate Sodium | `product_nutrients` | `per_100g_value` | `Numeric(10, 3)` | Store `420.000`, `unit = 'mg'`, `data_status = 'PRESENT'` (reconciled candidate value from community image with raw payload preserving 0.168g sodium; subject to unverified candidate limitation as physical verification is unperformed). |
| Ingredients list | `product_ingredients` | Multiple rows | Composite bridge table | Tokenize each ingredient: Refined Wheat Flour (Maida), Sugar, Fractionated Fat, Palmolein, Invert Sugar, Cocoa Solids (2%), Leavening Agents (INS 500i, INS 503ii), Starch, Iodised Salt, Emulsifier (INS 322), Nature Identical Flavouring Substances. Allergens linked: Wheat (Gluten), Sulphites, Soy; Traces: Milk, Barley. Physical label verification unperformed. |

> [!NOTE]
> **Adherence to YumSure Four-State Nutrient Status Model**:
> The proposed relational mapping strictly implements YumSure's four data status values:
> 1. **`PRESENT`**: Used for all non-zero declared/reconciled nutrient fields above (Energy `483 kcal`, Protein `5.2g`, Carbohydrates `71.9g`, Total Sugars `38.8g`, Added Sugars `38.7g`, Total Fat `19.6g`, Saturated Fat `9.7g`, Trans Fat `0.1g`, Dietary Fibre `3.0g`, Candidate Sodium `420 mg`).
> 2. **`EXPLICITLY_ZERO`**: Used whenever packaging explicitly declares `0` or `0.0g` (e.g. Diet Coke macronutrients).
> 3. **`NOT_DECLARED`**: Assigned to nutrients omitted from the source record or packaging facts panel (e.g. Dietary Fibre in Strawberry Crème `7622201756789`, Trans Fat and Dietary Fibre in Choco Crème `7622201756932`); never assumed or stored as zero.
> 4. **`UNKNOWN`**: Assigned if nutrient data is garbled, contradictory, or unresolvable.


---

## 9. Batch Data Quality Audit: Candidates #7–#11

> [!CAUTION]
> **Physical Verification Status: UNPERFORMED (`is_verified = False`)**  
> We do not possess physical packaging for Candidates #7–#11. Data is audited across **Open Food Facts API v3 database records** and packaging photographs uploaded by community contributors.  
> Neither an Open Food Facts database hit nor a crowdsourced photograph constitutes physical-label verification.

---

### 9.1 GS1 Modulo 10 Checksum Verification for Batch Barcodes

| Candidate # | Product Name & Variant | Barcode (EAN-13) | Odd Position Sum ($\times 1$) | Even Position Sum ($\times 3$) | Total Sum | Check Digit Calculation ($10 - (Total \bmod 10)$) | Declared Digit | Checksum Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **7** | Lay's Classic Salted Potato Chips (50g) | `8901491101837` | $8+0+4+1+0+8 = \mathbf{21}$ | $(9+1+9+1+1+3) \times 3 = \mathbf{72}$ | $\mathbf{93}$ | $100 - 93 = \mathbf{7}$ | `7` | ✅ **MATHEMATICALLY VALID** |
| **8** | Kurkure Masala Munch (78g) | `8901491100519` | $8+0+4+1+0+5 = \mathbf{18}$ | $(9+1+9+1+0+1) \times 3 = \mathbf{63}$ | $\mathbf{81}$ | $90 - 81 = \mathbf{9}$ | `9` | ✅ **MATHEMATICALLY VALID** |
| **9** | Parle-G Original Glucose Biscuits (80g) | `8901719100956` | $8+0+7+9+0+9 = \mathbf{33}$ | $(9+1+1+1+0+5) \times 3 = \mathbf{51}$ | $\mathbf{84}$ | $90 - 84 = \mathbf{6}$ | `6` | ✅ **MATHEMATICALLY VALID** |
| **10** | Haldiram's Aloo Bhujia (205g) | `8904063218124` | $8+0+0+3+1+1 = \mathbf{13}$ | $(9+4+6+2+8+2) \times 3 = \mathbf{93}$ | $\mathbf{106}$ | $110 - 106 = \mathbf{4}$ | `4` | ✅ **MATHEMATICALLY VALID** |
| **11** | KitKat 4-Finger Milk Chocolate (55g) | `8901058868036` | $8+0+0+8+6+0 = \mathbf{22}$ | $(9+1+5+8+8+3) \times 3 = \mathbf{102}$ | $\mathbf{124}$ | $130 - 124 = \mathbf{6}$ | `6` | ✅ **MATHEMATICALLY VALID** |

---

### 9.2 Quality Assessment Matrix: Field Completeness vs Evidence Confidence

| Candidate # & Product | Barcode Validity | Nutrition Field Completeness | Evidence Confidence Level | Discrepancy & Defect Analysis | Ingestion Handling Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **#7: Lay's Classic Salted** (`8901491101837`) | ✅ Valid EAN-13 | ✅ **Complete** (10 core fields populated) | **High** (Level 2 OFF Record + Level 3 Photos for front, ingredients, and nutrition) | Minor kJ discrepancy ($2311.4 / 4.184 \approx 552.4\text{ kcal}$ vs $554\text{ kcal}$). Dietary fibre recorded as 0g. | **ACCEPT FOR DEMO**: Ingest declared values; map INS 551, 627, 631 additives; preserve raw payload. |
| **#8: Kurkure Masala Munch** (`8901491100519`) | ✅ Valid EAN-13 | ✅ **Complete** (All 10 core fields populated) | **High** (Level 2 OFF Record + Level 3 Photos for front, ingredients, nutrition, packaging) | Substantial sodium ($796\text{ mg}$/100g, representing ~39.8% of ICMR-NIN 2000mg reference intake; $159.2\text{ mg}$ per 20g serving). | **ACCEPT FOR DEMO**: Ingest declared values; map rice/corn composite matrix; flag high sodium. |
| **#9: Parle-G Glucose** (`8901719100956`) | ✅ Valid EAN-13 | ⚠️ **Incomplete** (Ingredients missing; sodium zero-fill suspected; added sugars omitted) | **Moderate** (Level 2 OFF Record + Photos for front and nutrition; ingredients uncorroborated) | **Defect Finding**: Crowdsourced sodium entered as 0g. A zero-fill problem is **suspected, not proven**. Ingredients are omitted from record; ingredients or sodium are not inferred from external recipes. | **REJECT FOR DEMO / MARK INCOMPLETE**: Store sodium as `UNKNOWN` with raw 0g preserved. Require label re-audit. |
| **#10: Haldiram's Aloo Bhujia** (`8904063218124`) | ✅ Valid EAN-13 | ✅ **Complete** (Protein $8.68\text{g}$, Fibre $4.01\text{g}$, Sodium $615\text{mg}$, Sat Fat $16.5\text{g}$) | **Moderate** (Level 2 OFF Record + Front Photo Only; **Nutrition Table NOT photograph-verified**) | **Energy Discrepancy**: Declared `562 kcal` and `2373.78 kJ`. Converted kJ yields $2373.78 / 4.184 \approx \mathbf{567.3\text{ kcal}}$ ($\approx 5.3\text{ kcal}$ gap). Atwater estimate with fibre yields $(8.68 \times 4) + (46.1 \times 4) + (38.12 \times 9) + (4.01 \times 2) \approx \mathbf{570.2\text{ kcal}}$ ($+8.2\text{ kcal}$ variance). Energy marked as **unresolved**; raw values preserved. | **ACCEPT FOR DEMO WITH CAVEAT**: Ingest declared values; note front-photo limitation and unresolved energy discrepancy. |
| **#11: KitKat 4-Finger** (`8901058868036`) | ✅ Valid EAN-13 | ⚠️ **Incomplete** (Sat fat $23.0\text{g}$ present; sodium, trans fat, added sugars omitted) | **Moderate** (Level 2 OFF Record + Front Photo Only; **Nutrition Table NOT photograph-verified**) | **Defect Finding**: Sodium, trans fat, and added sugars omitted (`NOT_DECLARED`). Very high saturated fat proportion (89.5% of total fat). | **REJECT FOR DEMO / MARK INCOMPLETE**: Map allergens (milk, soy, sesame, gluten); retain as unverified candidate. |

---

### 9.3 Four-State Nutrient Mapping Summary for Batch Candidates

| Target Field | Lay's Classic Salted (`8901491101837`) | Kurkure Masala Munch (`8901491100519`) | Parle-G Glucose (`8901719100956`) | Haldiram's Aloo Bhujia (`8904063218124`) | KitKat 4-Finger (`8901058868036`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Energy (kcal)** | `554.000` (`PRESENT`) | `557.000` (`PRESENT`) | `454.000` (`PRESENT`) | `562.000` (`PRESENT` — unresolved discrepancy vs 567.3 kcal converted & 570.2 kcal Atwater) | `518.000` (`PRESENT`) |
| **Protein (g)** | `7.000` (`PRESENT`) | `6.000` (`PRESENT`) | `7.000` (`PRESENT`) | `8.680` (`PRESENT`) | `8.000` (`PRESENT`) |
| **Carbohydrates (g)** | `51.700` (`PRESENT`) | `57.700` (`PRESENT`) | `77.300` (`PRESENT`) | `46.100` (`PRESENT`) | `63.800` (`PRESENT`) |
| **Total Sugars (g)** | `2.600` (`PRESENT`) | `2.200` (`PRESENT`) | `25.000` (`PRESENT`) | `0.250` (`PRESENT`) | `48.700` (`PRESENT`) |
| **Added Sugars (g)** | `0.510` (`PRESENT`) | `0.800` (`PRESENT`) | `NULL` (`NOT_DECLARED`) | `0.000` (`EXPLICITLY_ZERO`) | `NULL` (`NOT_DECLARED`) |
| **Total Fat (g)** | `35.500` (`PRESENT`) | `33.700` (`PRESENT`) | `13.000` (`PRESENT`) | `38.120` (`PRESENT`) | `25.700` (`PRESENT`) |
| **Saturated Fat (g)** | `14.000` (`PRESENT`) | `7.700` (`PRESENT`) | `6.000` (`PRESENT`) | `16.500` (`PRESENT`) | `23.000` (`PRESENT`) |
| **Trans Fat (g)** | `0.100` (`PRESENT`) | `0.100` (`PRESENT`) | `0.000` (`EXPLICITLY_ZERO`) | `0.000` (`EXPLICITLY_ZERO`) | `NULL` (`NOT_DECLARED`) |
| **Dietary Fibre (g)** | `0.000` (`EXPLICITLY_ZERO`) | `0.000` (`EXPLICITLY_ZERO`) | `NULL` (`NOT_DECLARED`) | `4.010` (`PRESENT`) | `2.600` (`PRESENT`) |
| **Sodium (mg)** | `204.000` (`PRESENT`) | `796.000` (`PRESENT`) | `NULL` (`UNKNOWN` — suspected zero-fill; raw OFF `0.0g` preserved in source payload) | `615.000` (`PRESENT`) | `NULL` (`NOT_DECLARED`) |
| **Verification Flag** | `False` (`is_verified = False`) | `False` (`is_verified = False`) | `False` (`is_verified = False`) | `False` (`is_verified = False`) | `False` (`is_verified = False`) |

---

### 9.4 Batch Compliance & Boundary Statement:
- **Physical Verification**: **NOT PERFORMED**. No physical packaging was handled or inspected for Candidates #7–#11.
- **Database Operations**: Zero database operations, migrations, or table inserts were executed.
- **Application Schema Status**: Retained as proposed application status **`is_verified = False`**.
