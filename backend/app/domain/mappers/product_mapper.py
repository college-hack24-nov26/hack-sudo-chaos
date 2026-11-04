"""
ORM to Domain Mapper for Products.

Converts SQLAlchemy 2.0 Product, ProductNutrient, and ProductIngredient ORM models
into framework-independent Pydantic v2 domain DTOs (ProductEvaluationInput, etc.)
required by YumSure's deterministic evaluation engines.

Phase 3 Corrections:
1. Measurement Basis:
   - Explicitly assigns PER_100G, PER_100ML, or PER_SERVING based on product metadata (food_form).
   - Never infers measurement basis from numeric nutrient quantities.
2. Nutrient Units:
   - Removed unsafe default fallback to grams ('g').
   - Preserves valid units. If missing/invalid, explicitly flags unit as 'UNKNOWN'
     and sets data_status to NutrientDataStatus.UNKNOWN.
3. Declared Claims Normalization Boundary:
   - Dedicated normalization boundary (DeclaredClaimsNormalizer) that strictly validates
     and emits typed DeclaredClaimInput objects.
   - Preserves raw_source_payload untouched for provenance telemetry.
   - Never invents claims when source has no authentic claim declarations.
4. Ingredient Ordering & Scientific Classifications:
   - Preserves sequence_order ascending (descending weight order on packaging).
   - Propagates master Ingredient scientific classifications, defaulting safely to UNKNOWN.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Any
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
    DeclaredClaimInput,
    ProductEvaluationInput,
)

logger = logging.getLogger(__name__)


class DeclaredClaimsNormalizer:
    """
    Dedicated normalization boundary for voluntary on-pack marketing claims.
    Strictly validates and produces typed DeclaredClaimInput objects.
    Never invents claims when the source contains no claim declarations.
    """

    @staticmethod
    def normalize(
        raw_source_payload: Optional[Any],
        explicit_claims: Optional[List[DeclaredClaimInput]] = None,
    ) -> List[DeclaredClaimInput]:
        """
        Normalizes claims from explicit parameters or raw source payload.
        Returns empty list if no authentic claims are present.
        """
        if explicit_claims:
            return list(explicit_claims)

        if not raw_source_payload or not isinstance(raw_source_payload, dict):
            return []

        # Look strictly for 'declared_claims' list inside raw_source_payload
        raw_claims = raw_source_payload.get("declared_claims")
        if not raw_claims or not isinstance(raw_claims, list):
            return []

        normalized: List[DeclaredClaimInput] = []
        for item in raw_claims:
            if not isinstance(item, dict):
                continue

            claim_code = item.get("claim_code")
            raw_statement = item.get("raw_label_statement")

            # Must have non-empty claim_code and non-empty statement
            if (
                claim_code
                and isinstance(claim_code, str)
                and claim_code.strip()
                and raw_statement
                and isinstance(raw_statement, str)
                and raw_statement.strip()
            ):
                normalized.append(
                    DeclaredClaimInput(
                        claim_code=claim_code.strip().upper(),
                        raw_label_statement=raw_statement.strip(),
                    )
                )

        return normalized


class ProductMapper:
    """
    Coordinates transformation of SQLAlchemy ORM Product entities into
    clean, framework-independent ProductEvaluationInput domain DTOs.
    """

    @staticmethod
    def map_food_form(raw_form: Optional[str]) -> FoodForm:
        """
        Maps food form string ('solid', 'liquid') to FoodForm enum.
        Defaults to SOLID if missing, logging a warning.
        """
        if not raw_form:
            return FoodForm.SOLID

        clean = str(raw_form).strip().lower()
        if clean == "liquid":
            return FoodForm.LIQUID
        elif clean == "solid":
            return FoodForm.SOLID
        else:
            logger.warning("Unrecognized food_form '%s'; defaulting to FoodForm.SOLID", raw_form)
            return FoodForm.SOLID

    @staticmethod
    def determine_measurement_basis(
        food_form: Optional[FoodForm],
        has_per_100g_declaration: bool,
        has_per_serving_declaration: bool,
    ) -> Optional[MeasurementBasis]:
        """
        Determines the statutory measurement basis strictly from product metadata (food_form)
        and declaration scope. Never infers from numeric values.

        - Serving-only declaration: PER_SERVING
        - Liquid food with reference quantity: PER_100ML
        - Solid food with reference quantity: PER_100G
        - Unresolved / unknown: None
        """
        if not has_per_100g_declaration and has_per_serving_declaration:
            return MeasurementBasis.PER_SERVING

        if food_form == FoodForm.LIQUID:
            return MeasurementBasis.PER_100ML
        elif food_form == FoodForm.SOLID:
            return MeasurementBasis.PER_100G

        return None

    @staticmethod
    def map_nutrient_status(
        raw_status: Optional[str],
        per_100g_value: Optional[Decimal],
        per_serving_value: Optional[Decimal],
        is_unit_valid: bool = True,
    ) -> NutrientDataStatus:
        """
        Maps raw nutrient status string to NutrientDataStatus enum.
        Guarantees strict four-state nutrient declaration semantics.
        Never infers zero for missing values.
        If the unit is missing/invalid, forces status to UNKNOWN.
        """
        if not is_unit_valid:
            return NutrientDataStatus.UNKNOWN

        if raw_status:
            clean = str(raw_status).strip().upper()
            try:
                return NutrientDataStatus(clean)
            except ValueError:
                logger.debug("Unrecognized nutrient status '%s'; fallback to UNKNOWN", raw_status)
                return NutrientDataStatus.UNKNOWN

        # Infer strictly based on values if status was omitted:
        if per_100g_value is None and per_serving_value is None:
            return NutrientDataStatus.NOT_DECLARED

        if (per_100g_value is not None and per_100g_value == Decimal("0")) or (
            per_serving_value is not None and per_serving_value == Decimal("0")
        ):
            return NutrientDataStatus.EXPLICITLY_ZERO

        return NutrientDataStatus.PRESENT

    @classmethod
    def map_nutrient(
        cls,
        pn: ProductNutrient,
        food_form: FoodForm = FoodForm.SOLID,
        serving_size_value: Optional[Decimal] = None,
    ) -> NutrientObservationInput:
        """
        Transforms a single ProductNutrient ORM entity into a NutrientObservationInput DTO.

        Strict Rules:
        - None values for quantities are preserved (never converted to 0).
        - Unit fallback to grams ('g') is strictly removed. If missing from both pn and master,
          explicitly sets unit='UNKNOWN' and data_status=UNKNOWN.
        - Measurement basis is mapped to PER_100G, PER_100ML, or PER_SERVING from product metadata.
        """
        # Resolve Unit: pn.unit -> master Nutrient.standard_unit -> UNKNOWN (never default to 'g')
        unit = pn.unit.strip() if pn.unit and pn.unit.strip() else None
        if not unit and pn.nutrient and pn.nutrient.standard_unit and pn.nutrient.standard_unit.strip():
            unit = pn.nutrient.standard_unit.strip()

        is_unit_valid = True
        if not unit or unit.upper() == "UNKNOWN":
            unit = "UNKNOWN"
            is_unit_valid = False

        # Determine Measurement Basis
        has_per_100 = pn.per_100g_value is not None or (
            pn.data_status in ("PRESENT", "EXPLICITLY_ZERO") and pn.per_serving_value is None
        )
        has_serving = pn.per_serving_value is not None
        basis = cls.determine_measurement_basis(food_form, has_per_100, has_serving)

        # Map 4-state declaration status
        data_status = cls.map_nutrient_status(
            pn.data_status,
            pn.per_100g_value,
            pn.per_serving_value,
            is_unit_valid=is_unit_valid,
        )

<<<<<<< Updated upstream
        dec_100 = pn.per_100g_value
        dec_serving = pn.per_serving_value
        if (
            dec_serving is None
            and dec_100 is not None
            and serving_size_value is not None
            and serving_size_value > Decimal("0")
            and basis in (MeasurementBasis.PER_100G, MeasurementBasis.PER_100ML)
        ):
            dec_serving = Decimal(str(round(float(dec_100) * float(serving_size_value) / 100.0, 2)))
        elif (
            dec_100 is None
            and dec_serving is not None
            and serving_size_value is not None
            and serving_size_value > Decimal("0")
            and basis == MeasurementBasis.PER_SERVING
        ):
            dec_100 = Decimal(str(round(float(dec_serving) * 100.0 / float(serving_size_value), 2)))

        return NutrientObservationInput(
            nutrient_code=pn.nutrient_code,
            per_100g_value=dec_100,
            per_serving_value=dec_serving,
=======
        per_100g = pn.per_100g_value
        per_serving = pn.per_serving_value

        # Critical Guard: PER_SERVING values do not become per-100g values
        if basis == MeasurementBasis.PER_SERVING:
            per_100g = None
        elif basis is None:
            # Unresolved basis cannot be safely attributed to 100g or serving
            per_100g = None
            per_serving = None

        return NutrientObservationInput(
            nutrient_code=pn.nutrient_code,
            per_100g_value=per_100g,
            per_serving_value=per_serving,
>>>>>>> Stashed changes
            unit=unit,
            data_status=data_status,
            measurement_basis=basis,
        )

    @staticmethod
    def map_ingredient(pi: ProductIngredient) -> IngredientObservationInput:
        """
        Transforms a ProductIngredient bridge entity into an IngredientObservationInput DTO.
        Inherits scientific classifications from master Ingredient catalog if attached.
        """
        master_ing = getattr(pi, "ingredient", None)

        declared_text = pi.declared_label_text
        if not declared_text and master_ing and master_ing.canonical_name:
            declared_text = master_ing.canonical_name
        if not declared_text:
            declared_text = pi.ingredient_code

        ins_num = master_ing.ins_number if master_ing else None

        is_allergen = bool(pi.is_allergen_declared)
        if master_ing and master_ing.is_fssai_major_allergen:
            is_allergen = True

        proc_class = IngredientProcessingClass.UNKNOWN
        if master_ing and master_ing.processing_classification:
            try:
                proc_class = IngredientProcessingClass(master_ing.processing_classification)
            except ValueError:
                proc_class = IngredientProcessingClass.UNKNOWN

        sugar_class = IngredientSugarClass.UNKNOWN
        if master_ing and master_ing.sugar_classification:
            try:
                sugar_class = IngredientSugarClass(master_ing.sugar_classification)
            except ValueError:
                sugar_class = IngredientSugarClass.UNKNOWN

        evidence = master_ing.classification_evidence if master_ing else None

        return IngredientObservationInput(
            ingredient_code=pi.ingredient_code,
            declared_label_text=declared_text,
            sequence_order=pi.sequence_order,
            declared_percentage=pi.declared_percentage,
            ins_number=ins_num,
            is_fssai_major_allergen=is_allergen,
            processing_classification=proc_class,
            sugar_classification=sugar_class,
            classification_evidence=evidence,
        )

    @classmethod
    def map_product(
        cls,
        product: Product,
        extra_claims: Optional[List[DeclaredClaimInput]] = None,
    ) -> ProductEvaluationInput:
        """
        Maps a full ORM Product into a framework-independent ProductEvaluationInput.
        """
        food_form = cls.map_food_form(product.food_form)

        # 1. Map Nutrients (passing food_form for explicit measurement basis assignment)
        nutrients_dict: Dict[str, NutrientObservationInput] = {}
        if product.nutrients:
            for pn in product.nutrients:
                nutrients_dict[pn.nutrient_code] = cls.map_nutrient(pn, food_form=food_form, serving_size_value=product.serving_size_value)

        # 2. Map Ingredients (preserving sequence_order ascending = label descending weight)
        ingredients_list: List[IngredientObservationInput] = []
        if product.ingredients:
            sorted_ings = sorted(product.ingredients, key=lambda i: i.sequence_order)
            for pi in sorted_ings:
                ingredients_list.append(cls.map_ingredient(pi))

        # 3. Extract and Normalize Declared Claims via dedicated boundary
        declared_claims = DeclaredClaimsNormalizer.normalize(
            raw_source_payload=product.raw_source_payload,
            explicit_claims=extra_claims,
        )

        return ProductEvaluationInput(
            product_id=str(product.id) if product.id else product.barcode,
            product_name=product.product_name,
            brand_name=product.brand_name,
            food_form=food_form,
            food_category=product.food_category,
            package_size=product.package_size,
            serving_size_value=product.serving_size_value,
            serving_size_unit=product.serving_size_unit or "g",
            nutrients=nutrients_dict,
            ingredients=ingredients_list,
            declared_claims=declared_claims,
            data_source_id=product.source_id,
        )


def map_orm_product_to_domain(
    product: Product,
    extra_claims: Optional[List[DeclaredClaimInput]] = None,
) -> ProductEvaluationInput:
    """Convenience functional wrapper around ProductMapper.map_product."""
    return ProductMapper.map_product(product, extra_claims=extra_claims)
