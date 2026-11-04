# YumSure Nutrition Remediation Changelog

**Release Milestone**: Nutrition Data Integrity & Deterministic Evaluation Remediation  
**Lead Contributor**: Abhishek (Domain Evaluation Core & Nutrition Integrity Lead)  
**Co-Owner / Reviewer**: Tejas (Backend API, Mapper, Product Service, & Database Lead)  
**Date**: November 4, 2026  
**Status**: Completed, Audited, & Validated (135 Tests Passing, 0 Failures)

---

## 1. Overview of Changes

This release addresses data integrity bugs, dimensional unit conversion errors, floating-point rounding artifacts, and data-quality grading defects across the YumSure backend and mobile domain models.

### Primary Objectives Achieved:
1. **Product Identity & Barcode Isolation**: Disentangled internal demo fixture barcode (`8901030383701`) from authentic commercial pack barcode (`8901063142015`).
2. **Canonical Nutrient Declarations**: Calibrated all 10 canonical nutrients with verified packaging values for all 6 curated reference products.
3. **Dimensional Unit Compatibility**: Implemented strict dimensional typing preventing conversion between incompatible units (e.g., solid mass in grams vs liquid volume in ml).
4. **Exact Decimal Arithmetic**: Eliminated IEEE 754 floating-point rounding anomalies using `Decimal.quantize(Decimal("0.01"))`.
5. **Conservative Data Quality Classification**: Prevented unverified crowdsourced or ad-hoc data from defaulting to `VERIFIED`; introduced explicit `DEMO_DATA` state.
6. **Mathematical Consistency Validation**: Added per-serving hierarchy checks (`added_sugars <= total_sugars`, `sat_fat <= total_fat`, `trans_fat <= total_fat`) and Atwater energy plausibility checks.
7. **Regression Test Expansion**: Expanded `test_nutrition_data_integrity.py` from 12 to 22 tests, achieving 135 total passing backend tests.

---

## 2. Exhaustive File-by-File Modification Log

### A. Domain Contracts (`backend/app/domain/engines/contracts.py`)
- **Ownership**: Abhishek
- **Change**: Updated `serving_size_unit` in `ProductEvaluationInput` from `str = Field("g", ...)` to `Optional[str] = Field("g", description="Serving unit (e.g. 'g', 'ml')")`.
- **Rationale**: Allows products with unlabelled or missing serving units in the wild to be cleanly instantiated with `serving_size_unit=None`, triggering safe rejection in conversion pipelines rather than failing Pydantic type validation.

### B. Curated Food Catalog (`backend/app/domain/curated_catalog.py`)
- **Ownership**: Abhishek
- **Changes**:
  1. Resolved accidental stash conflict markers (`<<<<<<< Updated upstream`, `=======`, `>>>>>>> Stashed changes`).
  2. Preserved verified `val_serving` parameters across all 10 canonical nutrients for Nutri-Choice Digestive (`8901030383701`), Kissan Ketchup (`8901030825279`), Real Fruit Power (`8901207010497`), and Bournvita (`8901233024013`).
  3. Added authentic commercial EAN-13 pack entry `8901063142015` with `data_source_id="verified_packaging"`.
  4. Updated `CURATED_IMAGE_URLS` to link both `8901030383701` and `8901063142015` to Open Food Facts photographic packaging scans.

### C. Frontend Adapter (`backend/app/schemas/frontend_adapter.py`)
- **Ownership**: Abhishek (Shared with Tejas)
- **Changes**:
  1. **Hierarchy Checks**: Extended `validate_nutrient_consistency` to validate that `added_sugars <= total_sugars`, `saturated_fat <= total_fat`, and `trans_fat <= total_fat` across both `per_100g_value` and `per_serving_value`.
  2. **Conservative Data Quality**: Implemented strict evaluation order:
     - `INCONSISTENT` (if hierarchy/energy checks fail)
     - `INCOMPLETE` (if statutory mandatory nutrients are undeclared or unknown)
     - `OCR_EXTRACTED` (if from camera OCR)
     - `DEMO_DATA` (if from `curated_demo_catalog`)
     - `VERIFIED` (if from `verified_packaging` or `verified_local_db`)
     - `UNVERIFIED_EXTERNAL` (strictly default for all unknown external sources)
  3. **Dimensional Serving Conversions**:
     - Verified serving size requires compatible units (`MASS_UNITS` for `PER_100G`; `VOLUME_UNITS` for `PER_100ML`).
     - Incompatible units or count units (`pieces`, `biscuits`) return `None`.
     - Exact `Decimal` arithmetic using `.quantize(Decimal("0.01"))`.
     - Eliminated duplicate conversion block.

### D. Product Service (`backend/app/services/product_service.py`)
- **Ownership**: Tejas (Abhishek guardrail integration)
- **Changes**:
  1. In fallback resolution, updated `is_verified` flag: `is_verified = (curated.data_source_id == "verified_packaging")`.
  2. Updated `source_provenance` generation to explicitly identify demo fixtures:
     `"Curated Demonstration Packaging (Calibrated from Barcode 8901063142015)"` for `curated_demo_catalog`.

### E. Product Mapper (`backend/app/domain/mappers/product_mapper.py`)
- **Ownership**: Tejas (Abhishek review)
- **Changes**:
  1. Resolved stash conflict markers.
  2. Updated conversion arithmetic from `float` and `round(..., 2)` to `((dec * serv) / Decimal("100")).quantize(Decimal("0.01"))`.
  3. Ensured unresolved basis (`None`) sets both `dec_100` and `dec_serving` to `None`.

### F. Flutter Models (`frontend/lib/features/product_details/data/models/product_response_model.dart`)
- **Ownership**: Frontend / Shared
- **Changes**:
  1. Resolved accidental stash conflict markers at end of file.
  2. Preserved `ProductDataFieldStatus` class for data completeness evaluation.

### G. Regression Test Suite (`backend/tests/test_nutrition_data_integrity.py`)
- **Ownership**: Abhishek
- **Changes**:
  1. Added `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))` for standalone test execution.
  2. Updated Scenario 12 to verify `DEMO_DATA` quality for demo fixture `8901030383701`.
  3. Added Scenarios 13 through 22.

---

## 3. Regression Test Coverage (All 22 Scenarios)

| Test ID | Test Method Name | Description / Verification Target | Result |
|---|---|---|---|
| 01 | `test_01_all_ten_canonical_nutrients_present_with_correct_units` | Verifies all 10 canonical nutrients declared with statutory units in NutriChoice Digestive | **PASS** |
| 02 | `test_02_measurement_basis_preserved_explicitly` | Confirms explicit `MeasurementBasis.PER_100G` without silent inference | **PASS** |
| 03 | `test_03_accurate_100g_to_serving_conversion_nutri_choice` | Validates 25g serving calculations match packaging values exactly | **PASS** |
| 04 | `test_04_bidirectional_serving_to_100g_conversion_in_mapper` | Tests normalization of `PER_SERVING` external products back to per-100g reference | **PASS** |
| 05 | `test_05_missing_nutrient_distinct_from_explicit_zero` | Ensures `EXPLICITLY_ZERO` and `NOT_DECLARED` maintain distinct statuses | **PASS** |
| 06 | `test_06_unknown_measurement_basis_prevents_silent_conversion` | Prevents conversion when measurement basis is unresolved (`None`) or serving is missing | **PASS** |
| 07 | `test_07_inconsistency_added_sugars_exceeding_total_sugars` | Flags `added_sugars > total_sugars` as mathematical inconsistency | **PASS** |
| 08 | `test_08_inconsistency_saturated_fat_exceeding_total_fat` | Flags `saturated_fat > total_fat` as mathematical inconsistency | **PASS** |
| 09 | `test_09_inconsistency_trans_fat_exceeding_total_fat` | Flags `trans_fat > total_fat` as mathematical inconsistency | **PASS** |
| 10 | `test_10_inconsistency_atwater_energy_plausibility` | Detects gross energy deviations from macronutrient Atwater calculation | **PASS** |
| 11 | `test_11_nutri_choice_energy_plausibility_verified` | Validates declared energy (482 kcal) matches Atwater calculation (481.6 kcal) | **PASS** |
| 12 | `test_12_frontend_payload_adapter_serialization_and_quality` | Verifies demo barcode `8901030383701` correctly assigned `DEMO_DATA` quality | **PASS** |
| 13 | `test_13_verified_commercial_barcode_classified_as_verified` | Verifies commercial barcode `8901063142015` correctly assigned `VERIFIED` quality | **PASS** |
| 14 | `test_14_per_100ml_with_valid_volume_serving_conversion` | Confirms liquid product (PER_100ML) with 200 ml serving computes serving values | **PASS** |
| 15 | `test_15_per_100ml_with_incompatible_mass_serving_rejected` | Rejects conversion when liquid product (PER_100ML) receives mass serving (25 g) | **PASS** |
| 16 | `test_16_per_100g_with_valid_mass_serving_conversion` | Confirms solid product (PER_100G) with 25 g serving computes serving values | **PASS** |
| 17 | `test_17_per_100g_with_incompatible_volume_serving_rejected` | Rejects conversion when solid product (PER_100G) receives volume serving (25 ml) | **PASS** |
| 18 | `test_18_unknown_serving_unit_rejected` | Rejects conversion when serving size is declared in piece count (e.g. `2 pieces`) | **PASS** |
| 19 | `test_19_missing_serving_unit_rejected` | Prevents conversion when serving size unit is `None` | **PASS** |
| 20 | `test_20_unknown_external_source_never_defaults_to_verified` | Confirms unknown third-party sources default to `UNVERIFIED_EXTERNAL`, never `VERIFIED` | **PASS** |
| 21 | `test_21_negative_quantity_in_serving_detected` | Flags negative per-serving nutrient quantities as an inconsistency | **PASS** |
| 22 | `test_22_trans_fat_exceeding_total_fat_per_serving_detected` | Flags `trans_fat > total_fat` per serving as an inconsistency | **PASS** |

---

## 4. Full Test Suite Execution Summary

```
Runner: Python 3.14.6 (unittest discover)
Discovered Tests: 14 test suites, 136 tests discovered
Executed Tests: 135 executed, 1 skipped (test_direct_connection_and_table_presence in test_migration_ownership.py due to Supabase DB isolation)
Failures: 0
Errors: 0
Total Execution Time: ~0.475 seconds
Overall Status: SUCCESS (OK)
```

