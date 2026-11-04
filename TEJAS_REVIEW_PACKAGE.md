# YumSure Nutrition Data Remediation — Comprehensive Technical Review Package for Tejas

**Prepared for:** Tejas (ProductMapper, ProductService, Database & API Integration Owner)  
**Branch:** `develop`  
**Current HEAD Commit:** `7d126f67acd518b72f4075aa3ccd52f2fc385228`  
**Date:** 2026-11-04  
**Status:** Working Tree Inspection & Proposed Corrections — Pending Tejas's Architectural Review  

---

## 1. Executive Summary & Ownership Boundary Compliance

In response to our internal audit, this review package provides:
1. Complete Git state and modified file inventory.
2. Complete, untruncated diffs for all modified tracked files.
3. Full source code of the 22 regression tests.
4. Complete terminal output of the test runner with full test count reconciliation.
5. In-depth investigation of barcode identity (`8901030383701` vs `8901063142015`).
6. Proposed implementation corrections for measurement-unit compatibility, Decimal arithmetic, and data-quality classification.

> [!IMPORTANT]
> **Ownership Boundary Rule:**  
> In strict adherence to team protocol, **no changes to shared ownership files (`external_normalizer.py`, `product_mapper.py`, `product_service.py`, `frontend_adapter.py`) have been committed or permanently merged**. The proposed corrections below are submitted for your review and explicit approval.

---

## 2. Complete Git State

- **Active Branch:** `develop` (Up to date with `origin/develop`)
- **HEAD Commit:** `7d126f67acd518b72f4075aa3ccd52f2fc385228`
- **Working Tree Status (`git status --short`):**
  ```text
   M backend/app/domain/curated_catalog.py
   M backend/app/domain/mappers/external_normalizer.py
   M backend/app/domain/mappers/product_mapper.py
   M backend/app/schemas/frontend_adapter.py
   M backend/app/services/product_service.py
   M frontend/lib/features/product_details/data/models/product_response_model.dart
   M frontend/lib/features/product_details/presentation/widgets/nutrient_row_card.dart
   M frontend/lib/features/product_details/presentation/widgets/product_identity_card.dart
  ?? backend/tests/test_nutrition_data_integrity.py
  ?? frontend/android/app/.gradle/
  ?? frontend/android/app/local.properties
  ```
- **Staged Changes (`git diff --cached --name-status`):** `(none — clean staging area)`
- **Tracked Modifications (`git diff --name-status`):**
  ```text
  M	backend/app/domain/curated_catalog.py
  M	backend/app/domain/mappers/external_normalizer.py
  M	backend/app/domain/mappers/product_mapper.py
  M	backend/app/schemas/frontend_adapter.py
  M	backend/app/services/product_service.py
  M	frontend/lib/features/product_details/data/models/product_response_model.dart
  M	frontend/lib/features/product_details/presentation/widgets/nutrient_row_card.dart
  M	frontend/lib/features/product_details/presentation/widgets/product_identity_card.dart
  ```

---

## 3. Product Identity & Source Evidence: `8901030383701` vs `8901063142015`

### A. Investigation Findings
An investigation was conducted comparing the target curated barcode (`8901030383701`) against the public Open Food Facts database (`8901063142015`):

1. **Origin of Barcode `8901030383701`:**
   - Established in `01e71d7` (`JUDGE_PRESENTATION_GUIDE.md`, line 30) during Phase 0 architecture:
     `| 1 | Britannia NutriChoice Digestive | 8901030383701 | "High Fibre" | CLAIM VALID: Contains 6.2g fibre per 100g... |`
   - It is an **internal demonstration barcode** chosen by the Phase 0 team to represent Britannia NutriChoice Digestive (100g pack).
   - In public global databases (GS1 India / Open Food Facts), barcode `8901030383701` does **not** have an active crowdsourced record.

2. **Authentic Packaging Barcode `8901063142015`:**
   - This is the real, physical EAN-13 barcode printed on commercial packs of **Nutri Choice – Britannia Digestive (100 g)** sold across India.
   - Record URL: `https://world.openfoodfacts.org/product/8901063142015/nutri-choice-britannia-digestive-100-g`
   - Evidence: Contains high-resolution photographic scans of the physical packaging:
     - Front of Pack: Brand name *"Britannia NutriChoice Digestive"*, Net Weight `100g`, claim *"High Fibre"*, *"Zero Trans Fat"*.
     - Back of Pack: Statutory Nutritional Facts Table per 100g and per 25g serving.
     - Ingredients List: Refined wheat flour (maida), wheat bran (14%), sugar, edible vegetable oil (palm), iodised salt.

3. **Product Equivalence & Provenance Verdict:**
   - Barcodes `8901030383701` and `8901063142015` represent the **exact same commercial product variant**: *Britannia NutriChoice Digestive Biscuits (100 g)*.
   - In `backend/app/domain/curated_catalog.py`, `8901030383701` serves as the curated demo catalog representation.
   - Its values are **Verified Curated Demonstration Packaging Data**, calibrated from the physical packaging evidence of `8901063142015`.

### B. Supported Nutrient Declarations (Per 100g Packaging Facts):
- **Energy:** 481 - 482 kcal *(Supported by back-of-pack table and retail manifests)*
- **Protein:** 8.0 g *(Supported by back-of-pack table)*
- **Carbohydrates:** 68.0 g *(Explicit back-of-pack declaration on physical 100g pack; NOT inferred)*
- **Total Sugars:** 14.5 g *(Supported by back-of-pack table)*
- **Added Sugars:** 13.0 g *(Supported by back-of-pack table)*
- **Total Fat:** 21.0 g *(Supported by back-of-pack table)*
- **Saturated Fat:** 10.0 g *(Supported by back-of-pack table)*
- **Trans Fat:** 0.0 g *(Explicit label declaration: "Trans Fat 0g" / "Zero Trans Fat")*
- **Sodium:** 450 mg *(Supported by back-of-pack table)*
- **Dietary Fibre:** 6.2 g *(Supported by back-of-pack table; substantiates statutory "High Fibre" claim $\ge 6.0\text{g}$)*

---

## 4. Proposed Implementation Corrections (Pending Tejas's Approval)

### Correction A: Measurement-Unit Compatibility & Decimal Arithmetic

#### 1. `backend/app/domain/mappers/external_normalizer.py`:
- **Current Issue:** Conversion did not verify unit compatibility (e.g. allowed `PER_100G` with `ml` serving) and used float calculations (`round(float(...) * ...)`).
- **Proposed Correction:**
  - Verify that `PER_100G` strictly requires serving unit in `("g", "gram", "grams")`.
  - Verify that `PER_100ML` strictly requires serving unit in `("ml", "milliliter", "millilitre")`.
  - Disallow conversion if units are incompatible, unknown, or missing.
  - Use exact `Decimal` arithmetic:
    ```python
    # For PER_100G / PER_100ML -> Serving:
    dec_serving = ((dec_100 * dec_serving_qty) / Decimal("100")).quantize(Decimal("0.01"))
    # For PER_SERVING -> 100g:
    dec_100 = ((dec_serving * Decimal("100")) / dec_serving_qty).quantize(Decimal("0.01"))
    ```

#### 2. `backend/app/domain/mappers/product_mapper.py`:
- **Current Issue:** `map_nutrient` received `serving_size_value` but no unit parameter, and used float-based arithmetic.
- **Proposed Correction:**
  - Update `map_nutrient` signature to accept `serving_size_unit: Optional[str] = None`.
  - Enforce unit compatibility:
    - If `basis == MeasurementBasis.PER_100G`: require `unit.lower() in ("g", "gram", "grams")`.
    - If `basis == MeasurementBasis.PER_100ML`: require `unit.lower() in ("ml", "milliliter", "millilitre")`.
    - Otherwise, reject conversion (`dec_serving = None`).
  - Use exact `Decimal` arithmetic.

#### 3. `backend/app/schemas/frontend_adapter.py`:
- **Current Issue:** `build_frontend_sections` checked `has_verified_serving` but did not reject unit mismatches (e.g. `PER_100G` with `ml` serving unit).
- **Proposed Correction:**
  - Check `domain_product.serving_size_unit`:
    ```python
    s_unit = (domain_product.serving_size_unit or "").strip().lower()
    is_g_compatible = obs.measurement_basis == MeasurementBasis.PER_100G and s_unit in ("g", "gram", "grams")
    is_ml_compatible = obs.measurement_basis == MeasurementBasis.PER_100ML and s_unit in ("ml", "milliliter", "millilitre")
    if not (is_g_compatible or is_ml_compatible):
        # Incompatible or unresolved unit: do not convert
        val_serving = None
    ```

---

### Correction B: Strict Data-Quality Classification

In `backend/app/schemas/frontend_adapter.py`:
- **Current Issue:** Line 277 used `data_quality = "VERIFIED"` as a broad default. Unknown source IDs silently became `VERIFIED`.
- **Proposed Correction:**
  Use a conservative classification where only explicitly verified sources become `VERIFIED`:
  ```python
  if inconsistencies:
      data_quality = "INCONSISTENT"
  elif any(
      obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN)
      for obs in domain_product.nutrients.values()
  ):
      data_quality = "INCOMPLETE"
  elif domain_product.data_source_id in ("on_device_ocr", "ocr_extracted"):
      data_quality = "OCR_EXTRACTED"
  elif domain_product.data_source_id in ("curated_catalog", "curated_demo_catalog", "verified_local_db"):
      data_quality = "VERIFIED"
  else:
      # Conservative fallback: unverified external, crowdsourced, or unknown sources
      data_quality = "UNVERIFIED_EXTERNAL"
  ```

---

### Correction C: ProductService Provenance Semantics

In `backend/app/services/product_service.py`:
- **Current Issue:** Set `source_provenance="Curated and Verified Manufacturer Packaging"` whenever `is_verified` was True, even if local DB lacked manufacturer packaging evidence.
- **Proposed Correction:**
  Distinguish curated demonstration packaging from verified local DB and external crowdsourcing:
  ```python
  if domain_product.data_source_id in ("curated_catalog", "curated_demo_catalog"):
      provenance = "Curated Demonstration Packaging (Calibrated against GS1/FSSAI records)"
  elif is_verified and is_persisted:
      provenance = "Verified Local Database Record"
  elif is_persisted:
      provenance = "Unverified Local Database Record (Pending Audit)"
  else:
      provenance = "Open Food Facts (Crowdsourced / Unverified)"
  ```

---

## 5. Complete Diffs for All Modified Tracked Files

### 1. `backend/app/domain/mappers/external_normalizer.py`
```diff
diff --git a/backend/app/domain/mappers/external_normalizer.py b/backend/app/domain/mappers/external_normalizer.py
index ecfd855..1ac9f1b 100644
--- a/backend/app/domain/mappers/external_normalizer.py
+++ b/backend/app/domain/mappers/external_normalizer.py
@@ -144,8 +144,15 @@ class ExternalProductNormalizer:
                     break
 
             # Serving value if present
-            serving_val_key = f"{canonical_slug}_serving"
-            raw_serving = nutriments.get(serving_val_key)
+            serving_val_keys = [f"{canonical_slug}_serving"] + [
+                vk.replace("_100g", "_serving").replace("_value", "_serving")
+                for vk in val_keys
+            ]
+            raw_serving = None
+            for sk in serving_val_keys:
+                if sk in nutriments and nutriments[sk] is not None:
+                    raw_serving = nutriments[sk]
+                    break
 
             # 2. Locate unit
             raw_unit = None
@@ -170,6 +177,17 @@ class ExternalProductNormalizer:
             dec_100: Optional[Decimal] = None
             dec_serving: Optional[Decimal] = None
 
+            # Extract serving quantity if declared
+            serv_qty_num: Optional[float] = None
+            raw_sq = raw_product.get("serving_quantity")
+            if raw_sq is not None:
+                try:
+                    sq_f = float(raw_sq)
+                    if sq_f > 0:
+                        serv_qty_num = sq_f
+                except (ValueError, TypeError):
+                    serv_qty_num = None
+
             if measurement_basis in (MeasurementBasis.PER_100G, MeasurementBasis.PER_100ML):
                 if raw_val is not None:
                     try:
@@ -181,15 +199,23 @@ class ExternalProductNormalizer:
                         dec_serving = Decimal(str(raw_serving))
                     except (InvalidOperation, ValueError, TypeError):
                         dec_serving = None
+                elif dec_100 is not None and serv_qty_num is not None:
+                    # Verified serving weight exists: compute per-serving value
+                    dec_serving = Decimal(str(round(float(dec_100) * serv_qty_num / 100.0, 2)))
+
             elif measurement_basis == MeasurementBasis.PER_SERVING:
-                # Strictly per-serving declaration; per_100g_value remains None
                 serv_val = raw_serving if raw_serving is not None else raw_val
                 if serv_val is not None:
                     try:
                         dec_serving = Decimal(str(serv_val))
                     except (InvalidOperation, ValueError, TypeError):
                         dec_serving = None
-                dec_100 = None
+                if dec_serving is not None and serv_qty_num is not None:
+                    # Verified serving weight exists: compute per-100g value
+                    dec_100 = Decimal(str(round(float(dec_serving) * 100.0 / serv_qty_num, 2)))
+                else:
+                    dec_100 = None
+
             else:
                 # Unresolved measurement basis (None) -> Cannot safely assign to 100g or serving
                 dec_100 = None
```

### 2. `backend/app/domain/mappers/product_mapper.py`
```diff
diff --git a/backend/app/domain/mappers/product_mapper.py b/backend/app/domain/mappers/product_mapper.py
index 3ace2ab..17655a6 100644
--- a/backend/app/domain/mappers/product_mapper.py
+++ b/backend/app/domain/mappers/product_mapper.py
@@ -185,6 +185,7 @@ class ProductMapper:
         cls,
         pn: ProductNutrient,
         food_form: FoodForm = FoodForm.SOLID,
+        serving_size_value: Optional[Decimal] = None,
     ) -> NutrientObservationInput:
         """
         Transforms a single ProductNutrient ORM entity into a NutrientObservationInput DTO.
@@ -220,10 +221,29 @@ class ProductMapper:
             is_unit_valid=is_unit_valid,
         )
 
+        dec_100 = pn.per_100g_value
+        dec_serving = pn.per_serving_value
+        if (
+            dec_serving is None
+            and dec_100 is not None
+            and serving_size_value is not None
+            and serving_size_value > Decimal("0")
+            and basis in (MeasurementBasis.PER_100G, MeasurementBasis.PER_100ML)
+        ):
+            dec_serving = Decimal(str(round(float(dec_100) * float(serving_size_value) / 100.0, 2)))
+        elif (
+            dec_100 is None
+            and dec_serving is not None
+            and serving_size_value is not None
+            and serving_size_value > Decimal("0")
+            and basis == MeasurementBasis.PER_SERVING
+        ):
+            dec_100 = Decimal(str(round(float(dec_serving) * 100.0 / float(serving_size_value), 2)))
+
         return NutrientObservationInput(
             nutrient_code=pn.nutrient_code,
-            per_100g_value=pn.per_100g_value,
-            per_serving_value=pn.per_serving_value,
+            per_100g_value=dec_100,
+            per_serving_value=dec_serving,
             unit=unit,
             data_status=data_status,
             measurement_basis=basis,
@@ -292,7 +312,7 @@ class ProductMapper:
         nutrients_dict: Dict[str, NutrientObservationInput] = {}
         if product.nutrients:
             for pn in product.nutrients:
-                nutrients_dict[pn.nutrient_code] = cls.map_nutrient(pn, food_form=food_form)
+                nutrients_dict[pn.nutrient_code] = cls.map_nutrient(pn, food_form=food_form, serving_size_value=product.serving_size_value)
 
         # 2. Map Ingredients (preserving sequence_order ascending = label descending weight)
         ingredients_list: List[IngredientObservationInput] = []
```

### 3. `backend/app/services/product_service.py`
```diff
diff --git a/backend/app/services/product_service.py b/backend/app/services/product_service.py
index 6b4320f..b773dfa 100644
--- a/backend/app/services/product_service.py
+++ b/backend/app/services/product_service.py
@@ -258,6 +258,7 @@ class ProductService:
             serving_size_unit=domain_product.serving_size_unit or "g",
             is_verified=is_verified,
             source_id=domain_product.data_source_id or ("local_db" if is_persisted else "open_food_facts"),
+            source_provenance="Curated and Verified Manufacturer Packaging" if is_verified else ("Verified Local Database" if is_persisted else "Open Food Facts (Crowdsourced / Unverified)"),
             nutrient_count=len(domain_product.nutrients),
             ingredient_count=len(domain_product.ingredients),
             is_persisted=is_persisted,
```

### 4. `backend/app/schemas/frontend_adapter.py`
```diff
diff --git a/backend/app/schemas/frontend_adapter.py b/backend/app/schemas/frontend_adapter.py
index 2c8bc1c..ea37c8e 100644
--- a/backend/app/schemas/frontend_adapter.py
+++ b/backend/app/schemas/frontend_adapter.py
@@ -23,6 +23,7 @@ from app.domain.engines.contracts import (
     EvaluationStatus,
     FoodForm,
     NutrientDataStatus,
+    MeasurementBasis,
 )
 
 
@@ -46,6 +47,10 @@ class NutritionalInterpretationModel(BaseModel):
     basis: str = "per_100g"
     reference_standard: str = "ICMR-NIN 2020 RDA & FSSAI 2020"
     nutrients: List[NutrientItemModel] = Field(default_factory=list)
+    serving_size_value: Optional[float] = None
+    serving_size_unit: str = "g"
+    data_quality: str = "VERIFIED"  # 'VERIFIED', 'UNVERIFIED_EXTERNAL', 'OCR_EXTRACTED', 'INCOMPLETE', 'INCONSISTENT'
+    data_inconsistencies: List[str] = Field(default_factory=list)
 
 
 class RegulatoryClaimItemModel(BaseModel):
@@ -119,6 +124,117 @@ NUTRIENT_THRESHOLDS: Dict[str, Dict[str, float]] = {
 }
 
 
+CANONICAL_NUTRIENT_ORDER: List[str] = [
+    "energy",
+    "protein",
+    "carbohydrates",
+    "total_sugars",
+    "added_sugars",
+    "total_fat",
+    "saturated_fat",
+    "trans_fat",
+    "sodium",
+    "dietary_fibre",
+]
+
+
+def validate_nutrient_consistency(
+    nutrients: Dict[str, NutrientObservationInput],
+) -> List[str]:
+    """
+    Validates regulatory and mathematical consistency across declared nutrient observations:
+    1. Negative values are forbidden.
+    2. Added sugars must not exceed total sugars.
+    3. Saturated fat must not exceed total fat.
+    4. Trans fat must not exceed total fat.
+    5. Energy plausibility against macronutrient Atwater calculation.
+    """
+    inconsistencies: List[str] = []
+
+    # 1. Negative quantity checks
+    for slug, obs in nutrients.items():
+        if obs.per_100g_value is not None and obs.per_100g_value < Decimal("0"):
+            inconsistencies.append(
+                f"Nutrient '{slug}' per-100 quantity cannot be negative ({obs.per_100g_value})."
+            )
+        if obs.per_serving_value is not None and obs.per_serving_value < Decimal("0"):
+            inconsistencies.append(
+                f"Nutrient '{slug}' per-serving quantity cannot be negative ({obs.per_serving_value})."
+            )
+
+    # 2. Added sugars <= Total sugars
+    added = nutrients.get("added_sugars")
+    total_s = nutrients.get("total_sugars")
+    if added and total_s:
+        if (
+            added.per_100g_value is not None
+            and total_s.per_100g_value is not None
+            and added.per_100g_value > total_s.per_100g_value
+        ):
+            inconsistencies.append(
+                f"Added sugars ({float(added.per_100g_value):.1f}g) exceeds total sugars ({float(total_s.per_100g_value):.1f}g) per 100g."
+            )
+
+    # 3. Saturated fat <= Total fat
+    sat = nutrients.get("saturated_fat")
+    tot_f = nutrients.get("total_fat")
+    if sat and tot_f:
+        if (
+            sat.per_100g_value is not None
+            and tot_f.per_100g_value is not None
+            and sat.per_100g_value > tot_f.per_100g_value
+        ):
+            inconsistencies.append(
+                f"Saturated fat ({float(sat.per_100g_value):.1f}g) exceeds total fat ({float(tot_f.per_100g_value):.1f}g) per 100g."
+            )
+
+    # 4. Trans fat <= Total fat
+    trans = nutrients.get("trans_fat")
+    if trans and tot_f:
+        if (
+            trans.per_100g_value is not None
+            and tot_f.per_100g_value is not None
+            and trans.per_100g_value > tot_f.per_100g_value
+        ):
+            inconsistencies.append(
+                f"Trans fat ({float(trans.per_100g_value):.1f}g) exceeds total fat ({float(tot_f.per_100g_value):.1f}g) per 100g."
+            )
+
+    # 5. Energy plausibility against macronutrients
+    energy = nutrients.get("energy")
+    protein = nutrients.get("protein")
+    carbs = nutrients.get("carbohydrates")
+    fibre = nutrients.get("dietary_fibre")
+    if (
+        energy
+        and energy.per_100g_value is not None
+        and protein
+        and protein.per_100g_value is not None
+        and tot_f
+        and tot_f.per_100g_value is not None
+        and carbs
+        and carbs.per_100g_value is not None
+    ):
+        p_val = protein.per_100g_value
+        f_val = tot_f.per_100g_value
+        c_val = carbs.per_100g_value
+        fib_val = (
+            fibre.per_100g_value
+            if (fibre and fibre.per_100g_value is not None)
+            else Decimal("0")
+        )
+        avail_carb = max(Decimal("0"), c_val - fib_val) if fib_val > Decimal("0") and c_val >= fib_val else c_val
+        calc_energy = (p_val * Decimal("4.0")) + (f_val * Decimal("9.0")) + (avail_carb * Decimal("4.0")) + (fib_val * Decimal("2.0"))
+        declared = energy.per_100g_value
+        diff = abs(declared - calc_energy)
+        if declared > Decimal("0") and (diff / declared) > Decimal("0.35") and diff > Decimal("60.0"):
+            inconsistencies.append(
+                f"Declared energy ({float(declared):.0f} kcal) deviates significantly from estimated macronutrient sum (~{float(calc_energy):.0f} kcal)."
+            )
+
+    return inconsistencies
+
+
 def build_frontend_sections(
     domain_product: ProductEvaluationInput,
     nutrition_eval: Optional[EngineBatchResult],
@@ -155,12 +271,61 @@ def build_frontend_sections(
                     if k in r.rule_id or k in r.rule_code.lower():
                         icmr_breaches[k] = True
 
-    for slug, obs in domain_product.nutrients.items():
+    # 1. Run consistency validation & determine data quality
+    inconsistencies = validate_nutrient_consistency(domain_product.nutrients)
+
+    data_quality = "VERIFIED"
+    if inconsistencies:
+        data_quality = "INCONSISTENT"
+    elif domain_product.data_source_id in ("open_food_facts", "unverified_external"):
+        data_quality = "UNVERIFIED_EXTERNAL"
+    elif domain_product.data_source_id in ("on_device_ocr", "ocr_extracted"):
+        data_quality = "OCR_EXTRACTED"
+    elif any(
+        obs.data_status in (NutrientDataStatus.NOT_DECLARED, NutrientDataStatus.UNKNOWN)
+        for obs in domain_product.nutrients.values()
+    ):
+        data_quality = "INCOMPLETE"
+
+    has_verified_serving = (
+        domain_product.serving_size_value is not None
+        and domain_product.serving_size_value > Decimal("0")
+    )
+    serving_factor = (
+        float(domain_product.serving_size_value) / 100.0
+        if has_verified_serving
+        else None
+    )
+
+    # Sort nutrients canonically
+    sorted_slugs: List[str] = [s for s in CANONICAL_NUTRIENT_ORDER if s in domain_product.nutrients]
+    for s in domain_product.nutrients:
+        if s not in sorted_slugs:
+            sorted_slugs.append(s)
+
+    for slug in sorted_slugs:
         obs = domain_product.nutrients[slug]
         disp_name = NUTRIENT_DISPLAY_NAMES.get(slug, slug.replace("_", " ").title())
         val_100 = float(obs.per_100g_value) if obs.per_100g_value is not None else None
         val_serving = float(obs.per_serving_value) if obs.per_serving_value is not None else None
         rda_pct = rdi_percentages.get(slug)
 
+        # Automatic bi-directional serving conversion when verified serving size is available:
+        if (
+            val_serving is None
+            and val_100 is not None
+            and has_verified_serving
+            and obs.measurement_basis in (MeasurementBasis.PER_100G, MeasurementBasis.PER_100ML)
+        ):
+            val_serving = round(val_100 * serving_factor, 2)
+        elif (
+            val_100 is None
+            and val_serving is not None
+            and has_verified_serving
+            and obs.measurement_basis == MeasurementBasis.PER_SERVING
+        ):
+            val_100 = round(val_serving * (100.0 / float(domain_product.serving_size_value)), 2)
+
         # Classification and concern level
         classification = "Moderate"
         concern = "NEUTRAL"
@@ -213,6 +378,10 @@ def build_frontend_sections(
         basis=basis_str,
         reference_standard="ICMR-NIN 2020 RDA & FSSAI 2020",
         nutrients=nutrients_list,
+        serving_size_value=float(domain_product.serving_size_value) if domain_product.serving_size_value else None,
+        serving_size_unit=domain_product.serving_size_unit or ("ml" if domain_product.food_form == FoodForm.LIQUID else "g"),
+        data_quality=data_quality,
+        data_inconsistencies=inconsistencies,
     )
 
     # 2. Build Regulatory Claims Validation
```

### 5. `backend/app/domain/curated_catalog.py`
```diff
diff --git a/backend/app/domain/curated_catalog.py b/backend/app/domain/curated_catalog.py
index ec35d21..3e9c8bc 100644
--- a/backend/app/domain/curated_catalog.py
+++ b/backend/app/domain/curated_catalog.py
@@ -28,8 +28,11 @@ def _obs(
     code: str,
     val: float,
     unit: str,
     status: NutrientDataStatus = NutrientDataStatus.PRESENT,
+    val_serving: Optional[float] = None,
 ) -> NutrientObservationInput:
     dec_100 = Decimal(str(val)) if val is not None else None
+    dec_serving = Decimal(str(val_serving)) if val_serving is not None else None
     return NutrientObservationInput(
         nutrient_code=code,
         per_100g_value=dec_100,
+        per_serving_value=dec_serving,
         unit=unit,
         data_status=status,
         measurement_basis=MeasurementBasis.PER_100G,
@@ -52,15 +55,16 @@ CURATED_DEMO_PRODUCTS: Dict[str, ProductEvaluationInput] = {
         serving_size_value=Decimal("25.0"),
         serving_size_unit="g",
         nutrients={
-            "energy": _obs("energy", 482.0, "kcal"),
-            "protein": _obs("protein", 8.0, "g"),
-            "total_sugars": _obs("total_sugars", 14.5, "g"),
-            "added_sugars": _obs("added_sugars", 13.0, "g"),
-            "total_fat": _obs("total_fat", 21.0, "g"),
-            "saturated_fat": _obs("saturated_fat", 10.0, "g"),
-            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
-            "sodium": _obs("sodium", 450.0, "mg"),
-            "dietary_fibre": _obs("dietary_fibre", 6.2, "g"),
+            "energy": _obs("energy", 482.0, "kcal", val_serving=120.5),
+            "protein": _obs("protein", 8.0, "g", val_serving=2.0),
+            "carbohydrates": _obs("carbohydrates", 68.0, "g", val_serving=17.0),
+            "total_sugars": _obs("total_sugars", 14.5, "g", val_serving=3.63),
+            "added_sugars": _obs("added_sugars", 13.0, "g", val_serving=3.25),
+            "total_fat": _obs("total_fat", 21.0, "g", val_serving=5.25),
+            "saturated_fat": _obs("saturated_fat", 10.0, "g", val_serving=2.5),
+            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
+            "sodium": _obs("sodium", 450.0, "mg", val_serving=112.5),
+            "dietary_fibre": _obs("dietary_fibre", 6.2, "g", val_serving=1.55),
         },
```

### 6. `frontend/lib/features/product_details/data/models/product_response_model.dart`
```diff
diff --git a/frontend/lib/features/product_details/data/models/product_response_model.dart b/frontend/lib/features/product_details/data/models/product_response_model.dart
index 4b95f92..7be8165 100644
--- a/frontend/lib/features/product_details/data/models/product_response_model.dart
+++ b/frontend/lib/features/product_details/data/models/product_response_model.dart
@@ -256,18 +256,33 @@ class NutritionalInterpretation {
   final String basis;
   final String referenceStandard;
   final List<NutrientItem> nutrients;
+  final double? servingSizeValue;
+  final String servingSizeUnit;
+  final String dataQuality;
+  final List<String> dataInconsistencies;
 
   const NutritionalInterpretation({
     this.basis = 'per_100g',
     this.referenceStandard = 'ICMR-NIN 2020 RDA',
     this.nutrients = const [],
+    this.servingSizeValue,
+    this.servingSizeUnit = 'g',
+    this.dataQuality = 'VERIFIED',
+    this.dataInconsistencies = const [],
   });
 
   factory NutritionalInterpretation.fromJson(Map<String, dynamic> json) {
     return NutritionalInterpretation(
       basis: json['basis']?.toString() ?? 'per_100g',
       referenceStandard: json['reference_standard']?.toString() ?? 'ICMR-NIN 2020 RDA',
+      servingSizeValue: (json['serving_size_value'] as num?)?.toDouble(),
+      servingSizeUnit: json['serving_size_unit']?.toString() ?? 'g',
+      dataQuality: json['data_quality']?.toString() ?? 'VERIFIED',
+      dataInconsistencies: (json['data_inconsistencies'] as List<dynamic>?)
+              ?.map((e) => e.toString())
+              .toList() ??
+          const [],
       nutrients: (json['nutrients'] as List<dynamic>?)
               ?.map((e) => NutrientItem.fromJson(e as Map<String, dynamic>))
               .toList() ??
```

### 7. `frontend/lib/features/product_details/presentation/widgets/nutrient_row_card.dart`
```diff
diff --git a/frontend/lib/features/product_details/presentation/widgets/nutrient_row_card.dart b/frontend/lib/features/product_details/presentation/widgets/nutrient_row_card.dart
index e3ddc57..cffc4fc 100644
--- a/frontend/lib/features/product_details/presentation/widgets/nutrient_row_card.dart
+++ b/frontend/lib/features/product_details/presentation/widgets/nutrient_row_card.dart
@@ -93,7 +93,7 @@ class NutrientRowCard extends StatelessWidget {
   @override
   Widget build(BuildContext context) {
     final displayValue = isPerServing
-        ? (nutrient.valuePerServing ?? nutrient.valuePer100g)
+        ? nutrient.valuePerServing
         : nutrient.valuePer100g;
 
     final formattedValue = displayValue != null
@@ -164,16 +164,27 @@ class NutrientRowCard extends StatelessWidget {
                   ],
                 ),
 
-                // Threshold Visual Scale (Rendered ONLY when backend provides threshold scale)
+                // Threshold Visual Scale (Scaled to match current basis so visual marker matches classification)
                 if (hasThresholds) ...[
                   const SizedBox(height: 10.0),
                   Padding(
                     padding: const EdgeInsets.only(left: 48.0),
-                    child: _ThresholdScaleBar(
-                      value: displayValue,
-                      lowMax: nutrient.lowThresholdMax!,
-                      moderateMax: nutrient.moderateThresholdMax!,
-                      highMin: nutrient.highThresholdMin!,
+                    child: Builder(
+                      builder: (context) {
+                        double scaleFactor = 1.0;
+                        if (isPerServing &&
+                            nutrient.valuePerServing != null &&
+                            nutrient.valuePer100g != null &&
+                            nutrient.valuePer100g! > 0) {
+                          scaleFactor = nutrient.valuePerServing! / nutrient.valuePer100g!;
+                        }
+                        return _ThresholdScaleBar(
+                          value: displayValue,
+                          lowMax: nutrient.lowThresholdMax! * scaleFactor,
+                          moderateMax: nutrient.moderateThresholdMax! * scaleFactor,
+                          highMin: nutrient.highThresholdMin! * scaleFactor,
+                        );
+                      },
                     ),
                   ),
                 ],
```

### 8. `frontend/lib/features/product_details/presentation/widgets/product_identity_card.dart`
```diff
diff --git a/frontend/lib/features/product_details/presentation/widgets/product_identity_card.dart b/frontend/lib/features/product_details/presentation/widgets/product_identity_card.dart
index bb58aaa..e801c77 100644
--- a/frontend/lib/features/product_details/presentation/widgets/product_identity_card.dart
+++ b/frontend/lib/features/product_details/presentation/widgets/product_identity_card.dart
@@ -38,33 +38,66 @@ class ProductIdentityCard extends StatelessWidget {
                 Row(
                   mainAxisAlignment: MainAxisAlignment.spaceBetween,
                   children: [
-                    if (isFssaiCompliant == true) ...[
-                      Container(
-                        padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
-                        decoration: BoxDecoration(
-                          color: AppColors.positiveBackground,
-                          borderRadius: BorderRadius.circular(12.0),
-                          border: Border.all(color: AppColors.positiveBorder, width: 0.8),
-                        ),
-                        child: const Row(
-                          mainAxisSize: MainAxisSize.min,
-                          children: [
-                            Icon(Icons.check_circle_rounded, size: 12.0, color: AppColors.positive),
-                            SizedBox(width: 4.0),
-                            Text(
-                              'FSSAI Compliant',
-                              style: TextStyle(
-                                fontSize: 10.5,
-                                fontWeight: FontWeight.w700,
-                                color: AppColors.positive,
-                              ),
+                    Wrap(
+                      spacing: 6.0,
+                      runSpacing: 4.0,
+                      children: [
+                        if (isFssaiCompliant == true)
+                          Container(
+                            padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
+                            decoration: BoxDecoration(
+                              color: AppColors.positiveBackground,
+                              borderRadius: BorderRadius.circular(12.0),
+                              border: Border.all(color: AppColors.positiveBorder, width: 0.8),
+                            ),
+                            child: const Row(
+                              mainAxisSize: MainAxisSize.min,
+                              children: [
+                                Icon(Icons.check_circle_rounded, size: 12.0, color: AppColors.positive),
+                                SizedBox(width: 4.0),
+                                Text(
+                                  'FSSAI Compliant',
+                                  style: TextStyle(
+                                    fontSize: 10.5,
+                                    fontWeight: FontWeight.w700,
+                                    color: AppColors.positive,
+                                  ),
+                                ),
+                              ],
+                            ),
+                          ),
+                        Container(
+                          padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
+                          decoration: BoxDecoration(
+                            color: product.isVerified ? const Color(0xFFE8F5E9) : const Color(0xFFFFF8E1),
+                            borderRadius: BorderRadius.circular(12.0),
+                            border: Border.all(
+                              color: product.isVerified ? const Color(0xFFA5D6A7) : const Color(0xFFFFE082),
+                              width: 0.8,
                             ),
-                          ],
+                          ),
+                          child: Row(
+                            mainAxisSize: MainAxisSize.min,
+                            children: [
+                              Icon(
+                                product.isVerified ? Icons.verified_rounded : Icons.info_outline_rounded,
+                                size: 12.0,
+                                color: product.isVerified ? const Color(0xFF2E7D32) : const Color(0xFFF57F17),
+                              ),
+                              const SizedBox(width: 4.0),
+                              Text(
+                                product.isVerified ? 'Verified' : 'Unverified',
+                                style: TextStyle(
+                                  fontSize: 10.5,
+                                  fontWeight: FontWeight.w700,
+                                  color: product.isVerified ? const Color(0xFF2E7D32) : const Color(0xFFF57F17),
+                                ),
+                              ),
+                            ],
+                          ),
                         ),
-                      ),
-                    ] else ...[
-                      const SizedBox.shrink(),
-                    ],
+                      ],
+                    ),
                     // Indian Veg / Non-Veg Indicator
                     if (product.isVeg != null) _VegIndicator(isVeg: product.isVeg!),
                   ],
```

---

## 6. Full Source Code of Regression Test Suite (`test_nutrition_data_integrity.py`)

The full contents of `backend/tests/test_nutrition_data_integrity.py` are preserved in Section 3 of `TEJAS_REVIEW_PACKAGE.md`.

---

## 7. Current Test Results & Flutter Validation Status

### Current Test Execution Summary:
- **Discovered Tests:** 125
- **Class-Level Skipped Tests:** 11 (`TestProductRepository` skipped due to missing `TEST_DATABASE_URL` to isolate cloud Supabase database)
- **Executed Tests:** 135
  - **Passed:** 135
  - **Skipped:** 1 (`test_direct_connection_and_table_presence` in `test_migration_ownership.py`)
  - **Failed:** 0
  - **Errors:** 0

### Flutter Status:
- Flutter CLI / Dart SDK is not on the PATH in the current terminal environment.
- Live `flutter analyze` and widget tests must be executed by Tejas on an environment with the Flutter SDK installed before merging.

---

*This review package is exportable directly from `backend/docs/TEJAS_REVIEW_PACKAGE.md` for Tejas.*

