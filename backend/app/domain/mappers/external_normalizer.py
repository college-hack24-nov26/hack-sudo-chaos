"""
Open Food Facts External Product Normalizer.

Transforms raw Open Food Facts (OFF) JSON responses into:
1. Framework-independent ProductEvaluationInput domain DTOs for deterministic evaluation.
2. Uncommitted Product, ProductNutrient, and ProductIngredient ORM entities for safe persistence.

Critical Regulatory Rules Enforced:
1. Missing nutrients are NEVER converted to zero (None remains None).
2. Explicit zero declarations (e.g. 0g trans fat) are strictly preserved as Decimal(0).
3. Missing nutrient units are NEVER assumed to be grams ('g'); mapped to 'UNKNOWN'.
4. Measurement Basis:
   - Evaluated strictly from explicit source declaration metadata (nutrition_data_per or key suffixes).
   - NEVER inferred solely from food_form or presence of serving sizes.
   - If measurement basis cannot be verified, explicitly set to None (unresolved).
5. Never invents voluntary claims: OFF tags and categories are NOT front-of-pack claims.
6. Preserves ingredient sequence order from packaging (1-based index).
"""

from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Any, Tuple
import uuid
import re
import logging

from app.models.product import Product
from app.models.product_nutrient import ProductNutrient
from app.models.product_ingredient import ProductIngredient
from app.domain.engines.contracts import (
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
    IngredientProcessingClass,
    IngredientSugarClass,
    NutrientObservationInput,
    IngredientObservationInput,
    ProductEvaluationInput,
)

logger = logging.getLogger(__name__)

# Canonical nutrient mapping table: (canonical_slug, [off_nutriment_keys], [off_unit_keys])
OFF_NUTRIENT_MAP: List[Tuple[str, List[str], List[str]]] = [
    ("energy", ["energy-kcal_100g", "energy_100g", "energy-kcal_value", "energy_value"], ["energy-kcal_unit", "energy_unit"]),
    ("protein", ["proteins_100g", "proteins_value", "protein_100g", "protein_value"], ["proteins_unit", "protein_unit"]),
    ("total_fat", ["fat_100g", "fat_value"], ["fat_unit"]),
    ("saturated_fat", ["saturated-fat_100g", "saturated_fat_100g", "saturated-fat_value", "saturated_fat_value"], ["saturated-fat_unit", "saturated_fat_unit"]),
    ("trans_fat", ["trans-fat_100g", "trans_fat_100g", "trans-fat_value", "trans_fat_value"], ["trans-fat_unit", "trans_fat_unit"]),
    ("carbohydrates", ["carbohydrates_100g", "carbohydrates_value"], ["carbohydrates_unit"]),
    ("total_sugars", ["sugars_100g", "sugars_value"], ["sugars_unit"]),
    ("added_sugars", ["added-sugars_100g", "added_sugars_100g", "added-sugars_value", "added_sugars_value"], ["added-sugars_unit", "added_sugars_unit"]),
    ("sodium", ["sodium_100g", "sodium_value"], ["sodium_unit"]),
    ("dietary_fibre", ["fiber_100g", "dietary-fiber_100g", "fiber_value"], ["fiber_unit", "dietary-fiber_unit"]),
]


class ExternalProductNormalizer:
    """
    Normalizes third-party packaged food payloads into YumSure domain contracts.
    """

    @staticmethod
    def extract_food_form(raw_product: Dict[str, Any]) -> FoodForm:
        """
        Determines food form (solid vs liquid) from explicit packaging units or categories.
        Defaults to SOLID if ambiguous.
        """
        # 1. Check product quantity units
        unit = str(raw_product.get("product_quantity_unit", "")).strip().lower()
        if unit in ("ml", "cl", "l", "liter", "litre"):
            return FoodForm.LIQUID

        # 2. Check quantity text
        qty_str = str(raw_product.get("quantity", "")).strip().lower()
        if re.search(r"\b(ml|cl|l|liter|litre)\b", qty_str):
            return FoodForm.LIQUID

        # 3. Check categories tags
        categories = raw_product.get("categories_tags", [])
        if isinstance(categories, list):
            for cat in categories:
                cat_lower = str(cat).lower()
                if any(k in cat_lower for k in ("beverage", "drink", "juice", "soda", "water", "tea", "coffee")):
                    return FoodForm.LIQUID

        return FoodForm.SOLID

    @staticmethod
    def determine_measurement_basis(
        raw_product: Dict[str, Any],
        nutriments: Dict[str, Any]
    ) -> Optional[MeasurementBasis]:
        """
        Determines statutory measurement basis strictly from source metadata.
        Never infers from food_form or missing values.
        Returns None if unresolved.
        """
        # 1. Explicit nutrition_data_per declaration in OFF product metadata
        raw_basis = str(raw_product.get("nutrition_data_per", "")).strip().lower()
        if raw_basis == "100g":
            return MeasurementBasis.PER_100G
        elif raw_basis == "100ml":
            return MeasurementBasis.PER_100ML
        elif raw_basis == "serving":
            return MeasurementBasis.PER_SERVING

        # 2. Inspect key suffixes in nutriments dictionary
        has_100g_keys = any(k.endswith("_100g") for k in nutriments.keys())
        has_100ml_keys = any(k.endswith("_100ml") for k in nutriments.keys())
        has_serving_keys = any(k.endswith("_serving") for k in nutriments.keys())

        if has_100g_keys and not has_100ml_keys:
            return MeasurementBasis.PER_100G
        elif has_100ml_keys and not has_100g_keys:
            return MeasurementBasis.PER_100ML
        elif has_serving_keys and not has_100g_keys and not has_100ml_keys:
            return MeasurementBasis.PER_SERVING

        # 3. Could not establish basis reliably from source metadata
        logger.debug("Measurement basis could not be determined from source metadata for product.")
        return None

    @classmethod
    def normalize_nutrients(
        cls,
        raw_product: Dict[str, Any],
        nutriments: Dict[str, Any],
        measurement_basis: Optional[MeasurementBasis]
    ) -> Dict[str, NutrientObservationInput]:
        """
        Normalizes OFF nutriments into standardized NutrientObservationInput instances.
        - Missing values are NEVER converted to zero.
        - Explicit zeros remain Decimal(0).
        - Missing units become 'UNKNOWN' and force data_status to UNKNOWN.
        """
        observations: Dict[str, NutrientObservationInput] = {}

        for canonical_slug, val_keys, unit_keys in OFF_NUTRIENT_MAP:
            # 1. Locate value
            raw_val = None
            for vk in val_keys:
                if vk in nutriments and nutriments[vk] is not None:
                    raw_val = nutriments[vk]
                    break

            # Serving value if present
            serving_val_keys = [f"{canonical_slug}_serving"] + [
                vk.replace("_100g", "_serving").replace("_value", "_serving")
                for vk in val_keys
            ]
            raw_serving = None
            for sk in serving_val_keys:
                if sk in nutriments and nutriments[sk] is not None:
                    raw_serving = nutriments[sk]
                    break

            # 2. Locate unit
            raw_unit = None
            for uk in unit_keys:
                if uk in nutriments and nutriments[uk]:
                    raw_unit = str(nutriments[uk]).strip()
                    break

            # If energy has no explicit unit but is kcal
            if canonical_slug == "energy" and not raw_unit:
                if any("kcal" in vk for vk in val_keys if vk in nutriments):
                    raw_unit = "kcal"

            # Strict unit resolution: never default to 'g'
            is_unit_valid = bool(raw_unit and raw_unit.upper() != "UNKNOWN")
            final_unit = raw_unit if is_unit_valid else "UNKNOWN"

            # Parse Decimal values based on resolved measurement basis:
            # - If PER_100G or PER_100ML: raw_val represents 100g/ml reference quantity -> dec_100
            # - If PER_SERVING: raw_val (or raw_serving) represents per-serving quantity -> dec_serving ONLY. dec_100 MUST be None.
            # - If None (unresolved): measurement basis is unknown; dec_100 and dec_serving MUST be None to prevent silent injection into rules.
            dec_100: Optional[Decimal] = None
            dec_serving: Optional[Decimal] = None

            # Extract serving quantity if declared
            serv_qty_num: Optional[float] = None
            raw_sq = raw_product.get("serving_quantity")
            if raw_sq is not None:
                try:
                    sq_f = float(raw_sq)
                    if sq_f > 0:
                        serv_qty_num = sq_f
                except (ValueError, TypeError):
                    serv_qty_num = None

            if measurement_basis in (MeasurementBasis.PER_100G, MeasurementBasis.PER_100ML):
                if raw_val is not None:
                    try:
                        dec_100 = Decimal(str(raw_val))
                    except (InvalidOperation, ValueError, TypeError):
                        dec_100 = None
                if raw_serving is not None:
                    try:
                        dec_serving = Decimal(str(raw_serving))
                    except (InvalidOperation, ValueError, TypeError):
                        dec_serving = None
                elif dec_100 is not None and serv_qty_num is not None:
                    # Verified serving weight exists: compute per-serving value
                    dec_serving = Decimal(str(round(float(dec_100) * serv_qty_num / 100.0, 2)))

            elif measurement_basis == MeasurementBasis.PER_SERVING:
                serv_val = raw_serving if raw_serving is not None else raw_val
                if serv_val is not None:
                    try:
                        dec_serving = Decimal(str(serv_val))
                    except (InvalidOperation, ValueError, TypeError):
                        dec_serving = None
                if dec_serving is not None and serv_qty_num is not None:
                    # Verified serving weight exists: compute per-100g value
                    dec_100 = Decimal(str(round(float(dec_serving) * 100.0 / serv_qty_num, 2)))
                else:
                    dec_100 = None

            else:
                # Unresolved measurement basis (None) -> Cannot safely assign to 100g or serving
                dec_100 = None
                dec_serving = None

            # 3. Determine four-state declaration status
            if raw_val is None and raw_serving is None:
                data_status = NutrientDataStatus.NOT_DECLARED
            elif measurement_basis is None:
                # Measurement basis could not be resolved from packaging/metadata -> UNKNOWN
                data_status = NutrientDataStatus.UNKNOWN
            elif not is_unit_valid:
                # If unit is missing/corrupted, observation is invalid -> UNKNOWN
                data_status = NutrientDataStatus.UNKNOWN
            elif (dec_100 is not None and dec_100 == Decimal("0")) or (
                dec_serving is not None and dec_serving == Decimal("0") and dec_100 is None
            ):
                data_status = NutrientDataStatus.EXPLICITLY_ZERO
            elif dec_100 is not None or dec_serving is not None:
                data_status = NutrientDataStatus.PRESENT
            else:
                data_status = NutrientDataStatus.UNKNOWN

            # Special case for energy: ensure 0 is explicit if declared
            observations[canonical_slug] = NutrientObservationInput(
                nutrient_code=canonical_slug,
                per_100g_value=dec_100,
                per_serving_value=dec_serving,
                unit=final_unit,
                data_status=data_status,
                measurement_basis=measurement_basis,
            )

        return observations

    @staticmethod
    def normalize_ingredients(raw_product: Dict[str, Any]) -> List[IngredientObservationInput]:
        """
        Normalizes ingredients from Open Food Facts, preserving packaging sequence order.
        Never invents ingredient declarations.
        """
        raw_ings = raw_product.get("ingredients")
        normalized: List[IngredientObservationInput] = []

        if isinstance(raw_ings, list) and len(raw_ings) > 0:
            seq = 1
            for ing in raw_ings:
                if not isinstance(ing, dict):
                    continue
                # Extract text and code
                text = ing.get("text") or ing.get("id") or f"ingredient_{seq}"
                code = str(ing.get("id") or text).strip().lower().replace("en:", "").replace(" ", "_")

                # Extract QUID percentage if present
                percent: Optional[Decimal] = None
                raw_pct = ing.get("percent") or ing.get("percent_estimate")
                if raw_pct is not None:
                    try:
                        percent = Decimal(str(raw_pct))
                    except (InvalidOperation, ValueError, TypeError):
                        percent = None

                # Extract INS number if text contains 'INS' or 'E'
                ins_num = None
                ins_match = re.search(r"\b(?:ins|e)\s*(\d+[a-z]?)\b", text, re.IGNORECASE)
                if ins_match:
                    ins_num = ins_match.group(1)

                normalized.append(
                    IngredientObservationInput(
                        ingredient_code=code,
                        declared_label_text=str(text).strip(),
                        sequence_order=seq,
                        declared_percentage=percent,
                        ins_number=ins_num,
                        is_fssai_major_allergen=False,
                        processing_classification=IngredientProcessingClass.UNKNOWN,
                        sugar_classification=IngredientSugarClass.UNKNOWN,
                    )
                )
                seq += 1
            return normalized

        # Fallback to ingredients_text if structured array is missing
        ings_text = raw_product.get("ingredients_text")
        if ings_text and isinstance(ings_text, str) and ings_text.strip():
            tokens = [t.strip() for t in re.split(r"[,;]", ings_text) if t.strip()]
            for seq, token in enumerate(tokens, start=1):
                code = re.sub(r"[^\w\s-]", "", token).strip().lower().replace(" ", "_")
                normalized.append(
                    IngredientObservationInput(
                        ingredient_code=code or f"ingredient_{seq}",
                        declared_label_text=token,
                        sequence_order=seq,
                        processing_classification=IngredientProcessingClass.UNKNOWN,
                        sugar_classification=IngredientSugarClass.UNKNOWN,
                    )
                )

        return normalized

    @classmethod
    def to_domain_dto(
        cls,
        barcode: str,
        raw_product: Dict[str, Any],
        raw_payload: Optional[Dict[str, Any]] = None,
    ) -> ProductEvaluationInput:
        """
        Transforms Open Food Facts raw product dictionary into a clean ProductEvaluationInput.
        """
        food_form = cls.extract_food_form(raw_product)
        nutriments = raw_product.get("nutriments", {})
        if not isinstance(nutriments, dict):
            nutriments = {}

        measurement_basis = cls.determine_measurement_basis(raw_product, nutriments)
        nutrients = cls.normalize_nutrients(raw_product, nutriments, measurement_basis)
        ingredients = cls.normalize_ingredients(raw_product)

        # Product name fallback
        prod_name = (
            raw_product.get("product_name")
            or raw_product.get("product_name_en")
            or f"Product {barcode}"
        ).strip()

        # Brand name
        brands = raw_product.get("brands")
        brand_str = str(brands).split(",")[0].strip() if brands else None

        # Serving size
        serving_val: Optional[Decimal] = None
        serving_unit = "g" if food_form == FoodForm.SOLID else "ml"
        raw_serv_qty = raw_product.get("serving_quantity")
        if raw_serv_qty is not None:
            try:
                serving_val = Decimal(str(raw_serv_qty))
            except (InvalidOperation, ValueError, TypeError):
                serving_val = None

        raw_serv_str = raw_product.get("serving_size")
        if raw_serv_str and isinstance(raw_serv_str, str):
            unit_match = re.search(r"([a-zA-Z]+)", raw_serv_str)
            if unit_match:
                serving_unit = unit_match.group(1).lower()

        return ProductEvaluationInput(
            product_id=barcode,
            product_name=prod_name,
            brand_name=brand_str,
            food_form=food_form,
            food_category=raw_product.get("categories"),
            package_size=raw_product.get("quantity"),
            serving_size_value=serving_val,
            serving_size_unit=serving_unit,
            nutrients=nutrients,
            ingredients=ingredients,
            declared_claims=[],  # Never treat OFF tags as verified front-of-pack marketing claims
            data_source_id="open_food_facts",
        )

    @classmethod
    def to_orm_entity(
        cls,
        barcode: str,
        raw_product: Dict[str, Any],
        raw_payload: Optional[Dict[str, Any]] = None,
    ) -> Product:
        """
        Constructs an uncommitted SQLAlchemy Product ORM entity with associated
        ProductNutrient and ProductIngredient models, suitable for safe persistence.
        """
        domain_dto = cls.to_domain_dto(barcode, raw_product, raw_payload)
        prod_uuid = uuid.uuid4()

        # Build ProductNutrient ORM children
        orm_nutrients: List[ProductNutrient] = []
        for slug, obs in domain_dto.nutrients.items():
            orm_nutrients.append(
                ProductNutrient(
                    product_id=prod_uuid,
                    nutrient_code=slug,
                    per_100g_value=obs.per_100g_value,
                    per_serving_value=obs.per_serving_value,
                    unit=obs.unit,
                    data_status=obs.data_status.value,
                )
            )

        # Build ProductIngredient ORM children
        orm_ingredients: List[ProductIngredient] = []
        for obs_ing in domain_dto.ingredients:
            orm_ingredients.append(
                ProductIngredient(
                    product_id=prod_uuid,
                    ingredient_code=obs_ing.ingredient_code,
                    sequence_order=obs_ing.sequence_order,
                    declared_percentage=obs_ing.declared_percentage,
                    declared_label_text=obs_ing.declared_label_text,
                    is_allergen_declared=obs_ing.is_fssai_major_allergen,
                )
            )

        return Product(
            id=prod_uuid,
            barcode=barcode.strip(),
            product_name=domain_dto.product_name,
            brand_name=domain_dto.brand_name,
            food_form=domain_dto.food_form.value,
            food_category=domain_dto.food_category,
            package_size=domain_dto.package_size,
            serving_size_value=domain_dto.serving_size_value,
            serving_size_unit=domain_dto.serving_size_unit,
            is_verified=False,  # External records are unverified by default
            source_id="open_food_facts",
            raw_source_payload=raw_payload or raw_product,
            nutrients=orm_nutrients,
            ingredients=orm_ingredients,
        )

