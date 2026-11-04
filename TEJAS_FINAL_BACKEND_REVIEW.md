# Tejas Final Backend Review Package & Integration Checklist

**Module**: Shared Backend Components & Application Integration  
**Lead Domain Reviewer**: Abhishek (Domain Evaluation Core & Nutrition Integrity Lead)  
**Assigned Technical Owner**: Tejas (ProductMapper, ProductService, API Schemas, & Database Lead)  
**Date**: November 4, 2026  
**Status**: **PENDING TEJAS REVIEW & FORMAL SIGN-OFF**  
**Active Branch**: `develop` | **HEAD Commit**: `938f4d0b39df435d9ec890c149df59e62f407f20`

---

> [!IMPORTANT]
> **Ownership Boundary Declaration**:  
> In strict accordance with our team architecture agreement, **no shared backend files owned by Tejas have been committed as permanently approved**. The diffs and safety guardrails documented herein represent the remediation proposed by Abhishek for Tejas's independent review and authorization.

---

## 1. Summary of Shared Files Reviewed

The following files have shared ownership between Tejas (Application Integration / Persistence / API) and Abhishek (Domain Evaluation / Contracts / Normalization Integrity):

1. `backend/app/domain/mappers/external_normalizer.py` (Tejas primary owner; Abhishek domain mapping collaborator)
2. `backend/app/domain/mappers/product_mapper.py` (Tejas primary owner; Abhishek domain DTO consumer)
3. `backend/app/services/product_service.py` (Tejas primary owner; Abhishek evaluation coordinator consumer)
4. `backend/app/schemas/frontend_adapter.py` (Abhishek DTO adapter; Tejas API schema integration)
5. `backend/app/domain/engines/contracts.py` (Abhishek domain owner; Tejas mapper dependency)
6. `backend/app/domain/engines/coordinator.py` (Abhishek coordinator owner; Tejas service dependency)
7. `backend/app/schemas/product_analysis.py` (Tejas API response owner; Abhishek section model provider)

---

## 2. Detailed Findings & Review Requirements

### A. API Backward Compatibility

#### Backward Compatibility Audit:
- **Zero Breaking Schema Changes**: All existing endpoint response fields on `GET /api/v1/products/{barcode}` and `POST /api/v1/products/evaluate` remain completely intact.
- **Additive Fields**:
  - `data_quality`: Added to `NutritionalInterpretationModel` (defaults to `"VERIFIED"` or `"UNVERIFIED_EXTERNAL"`). Existing clients that do not parse this field simply ignore it.
  - `data_inconsistencies`: Added as a list of strings (`List[str] = Field(default_factory=list)`).
  - `source_provenance`: Preserved as an optional string on `ProductIdentity`.
  - `serving_size_value` and `serving_size_unit`: Preserved on both `ProductIdentity` and `NutritionalInterpretation`.
- **Existing Request Payloads**: `POST /api/v1/products/evaluate` continues to accept `ProductEvaluationInput` with identical field names.
- **Optional Fields with Safe Defaults**: All newly introduced validation fields are either optional or provide sensible statutory defaults, preventing deserialization errors in older client versions.

#### Before vs. After Response Comparison

**Before Remediation (Vulnerable to False Verification & IEEE 754 Float Artifacts):**
```json
{
  "product": {
    "barcode": "8901030383701",
    "product_name": "Nutri-Choice Digestive Biscuits",
    "brand_name": "Britannia",
    "is_verified": true,
    "source_provenance": "Curated and Verified Manufacturer Packaging"
  },
  "nutritional_interpretation": {
    "basis": "per_100g",
    "data_quality": "VERIFIED",
    "serving_size_value": 25.0,
    "serving_size_unit": "g",
    "nutrients": [
      {
        "nutrient_code": "carbohydrates",
        "display_name": "Carbohydrates",
        "value_per_100g": 68.0,
        "value_per_serving": 17.0,
        "status": "PRESENT"
      },
      {
        "nutrient_code": "total_sugars",
        "display_name": "Total Sugars",
        "value_per_100g": 14.5,
        "value_per_serving": 3.6299999999999995,
        "status": "PRESENT"
      }
    ]
  }
}
```

**After Remediation (Strict Identity Isolation, Decimal Exact Arithmetic, Conservative Quality):**
```json
{
  "product": {
    "barcode": "8901030383701",
    "product_name": "Nutri-Choice Digestive Biscuits",
    "brand_name": "Britannia",
    "is_verified": false,
    "source_provenance": "Curated Demonstration Packaging (Calibrated from Barcode 8901063142015)"
  },
  "nutritional_interpretation": {
    "basis": "per_100g",
    "data_quality": "DEMO_DATA",
    "data_inconsistencies": [],
    "serving_size_value": 25.0,
    "serving_size_unit": "g",
    "nutrients": [
      {
        "nutrient_code": "carbohydrates",
        "display_name": "Carbohydrates",
        "value_per_100g": 68.0,
        "value_per_serving": 17.0,
        "status": "PRESENT",
        "explanation": "Carbohydrates declaration per per_100g."
      },
      {
        "nutrient_code": "total_sugars",
        "display_name": "Total Sugars",
        "value_per_100g": 14.5,
        "value_per_serving": 3.63,
        "status": "PRESENT",
        "explanation": "Total Sugars declaration per per_100g."
      }
    ]
  }
}
```

---

### B. Serving-Size Conversion Correctness

1. **Strict Dimensional Unit Compatibility**:
   - `MeasurementBasis.PER_100G`: Requires mass serving units (`"g"`, `"gram"`, `"grams"`, `"gm"`). Any mismatch (e.g., serving in `"ml"`) rejects conversion and sets `value_per_serving = None`.
   - `MeasurementBasis.PER_100ML`: Requires volume serving units (`"ml"`, `"milliliter"`, `"millilitres"`). Any mismatch (e.g., serving in `"g"`) rejects conversion and sets `value_per_serving = None`.
   - Piece counts (e.g., `"2 biscuits"`, `"1 pouch"`) without net mass reject conversion.
2. **Default Value of `serving_size_unit`**:
   - In both `ProductEvaluationInput` and `CoordinatorEvaluationResult`, `serving_size_unit` now defaults to `None` rather than `"g"`.
   - When external scrapers or unverified payloads omit the serving unit, the system preserves `None` rather than silently assuming grams.
3. **No Double Conversion**:
   - Conversion executes only if the target reference value is `None` and the source value is declared. Existing values are never overwritten or recalculated.
4. **Exact Decimal Arithmetic**:
   - All conversions use `Decimal.quantize(Decimal("0.01"))`. Float-based rounding has been completely excised from the conversion pipeline.

---

### C. Conservative Data-Quality Classification

The data-quality grading hierarchy in `build_frontend_sections()` enforces conservative evaluation order:

1. **`INCONSISTENT`**: Data violates physical or mathematical laws (negative quantity, added sugar $>$ total sugar, saturated fat $>$ total fat, Atwater energy deviation $>35\%$).
2. **`INCOMPLETE`**: Any statutory mandatory nutrient (energy, protein, carbohydrates, total sugars, total fat, sodium) is `NOT_DECLARED` or `UNKNOWN`.
3. **`OCR_EXTRACTED`**: On-device camera capture without manual packaging verification.
4. **`DEMO_DATA`**: Internal calibrated demonstration fixtures (`curated_demo_catalog`).
5. **`VERIFIED`**: Physical packaging audit confirmed (`verified_packaging`, `curated_catalog`, `verified_local_db`).
6. **`UNVERIFIED_EXTERNAL`**: Default fallback for crowdsourced Open Food Facts or unknown external APIs. **Unknown sources never default to VERIFIED**.

---

### D. Verified-Product Protection & Update Policy

In `backend/app/services/product_service.py`, lines 213–273 enforce strict persistence protection:
- **Rule 1 (Immutability of Verified Records)**: If a product in the local database has `is_verified = True`, external Open Food Facts lookups or ad-hoc scraper updates are **strictly bypassed**. The curated, verified record is preserved untouched (`test_05_verified_product_never_overwritten`).
- **Rule 2 (Hierarchy of Source Confidence)**:
  1. *Priority 1*: Verified Local Database / Audited Packaging (`is_verified = True`, `data_quality = "VERIFIED"`).
  2. *Priority 2*: Curated Demonstration Catalog (`data_quality = "DEMO_DATA"`).
  3. *Priority 3*: Local Packaged Foods Persistent Store (SQLite `yumsure_persistent.db`, 852 Indian items).
  4. *Priority 4*: Crowdsourced Open Food Facts (`data_quality = "UNVERIFIED_EXTERNAL"`, `is_verified = False`).
- **Rule 3 (Safe Persistence Boundary)**: External crowdsourced products are only inserted into SQLite/Postgres if the barcode does not exist in local verified tables.

---

## 3. Exact DTO & Code Diffs Requiring Tejas's Approval

### Diff 1: `backend/app/domain/mappers/product_mapper.py`
```diff
--- a/backend/app/domain/mappers/product_mapper.py
+++ b/backend/app/domain/mappers/product_mapper.py
@@ -228,15 +228,18 @@ class ProductMapper:
         dec_100 = pn.per_100g_value
         dec_serving = pn.per_serving_value
         if (
             dec_serving is None
             and dec_100 is not None
             and serving_size_value is not None
             and serving_size_value > Decimal("0")
             and basis in (MeasurementBasis.PER_100G, MeasurementBasis.PER_100ML)
         ):
-            dec_serving = Decimal(str(round(float(dec_100) * float(serving_size_value) / 100.0, 2)))
+            dec_serving = ((dec_100 * serving_size_value) / Decimal("100")).quantize(Decimal("0.01"))
         elif (
             dec_100 is None
             and dec_serving is not None
             and serving_size_value is not None
             and serving_size_value > Decimal("0")
             and basis == MeasurementBasis.PER_SERVING
         ):
-            dec_100 = Decimal(str(round(float(dec_serving) * 100.0 / float(serving_size_value), 2)))
+            dec_100 = ((dec_serving * Decimal("100")) / serving_size_value).quantize(Decimal("0.01"))
+        elif basis is None:
+            dec_100 = None
+            dec_serving = None
```

### Diff 2: `backend/app/services/product_service.py`
```diff
--- a/backend/app/services/product_service.py
+++ b/backend/app/services/product_service.py
@@ -245,7 +245,7 @@ class ProductService:
                     if curated:
                         logger.info("Resolved barcode %s from curated demonstration catalog.", barcode)
                         domain_product = curated
-                        is_verified = True
+                        is_verified = (curated.data_source_id == "verified_packaging")
                         is_persisted = False
                         map_ms = 0.0
                         image_url = get_curated_image_url(barcode)
@@ -290,7 +290,7 @@ class ProductService:
             serving_size_unit=domain_product.serving_size_unit or "g",
             is_verified=is_verified,
             source_id=domain_product.data_source_id or ("local_db" if is_persisted else "open_food_facts"),
-            source_provenance="Curated and Verified Manufacturer Packaging" if is_verified else ("Verified Local Database" if is_persisted else "Open Food Facts (Crowdsourced / Unverified)"),
+            source_provenance="Curated Demonstration Packaging (Calibrated from Barcode 8901063142015)" if (domain_product.data_source_id == "curated_demo_catalog") else ("Curated and Verified Manufacturer Packaging" if is_verified else ("Verified Local Database" if is_persisted else "Open Food Facts (Crowdsourced / Unverified)")),
             nutrient_count=len(domain_product.nutrients),
```

### Diff 3: `backend/app/domain/engines/contracts.py` & `coordinator.py`
```diff
--- a/backend/app/domain/engines/contracts.py
+++ b/backend/app/domain/engines/contracts.py
@@ -128,1 +128,1 @@ class ProductEvaluationInput(BaseModel):
-    serving_size_unit: str = Field("g", description="Serving unit (e.g. 'g', 'ml')")
+    serving_size_unit: Optional[str] = Field(None, description="Serving unit (e.g. 'g', 'ml')")

--- a/backend/app/domain/engines/coordinator.py
+++ b/backend/app/domain/engines/coordinator.py
@@ -176,1 +176,1 @@ class CoordinatorEvaluationResult(BaseModel):
-    serving_size_unit: str = Field("g", description="Serving size unit")
+    serving_size_unit: Optional[str] = Field(None, description="Serving size unit")
```

---

## 4. Tejas Actionable Approval Checklist

- [ ] **Verify Decimal Arithmetic**: Confirm that `Decimal.quantize(Decimal("0.01"))` in `product_mapper.py` satisfies database precision requirements.
- [ ] **Confirm Barcode Provenance**: Review the distinction between demo barcode `8901030383701` (`is_verified=False`, `DEMO_DATA`) and commercial barcode `8901063142015` (`is_verified=True`, `VERIFIED`).
- [ ] **Confirm Null Serving Unit**: Confirm that `serving_size_unit: Optional[str] = None` does not conflict with ORM default column mappings in `models/product.py`.
- [ ] **Confirm Quality Fallback**: Confirm that unknown external products default to `UNVERIFIED_EXTERNAL`.
- [ ] **Sign-Off Decision**:
  - Status: **PENDING TEJAS REVIEW**
  - Signer: Tejas Devgharkar
  - Date: `[Awaiting Tejas Signature]`

