"""
Curated Packaged Food Products Catalog.

Provides verified, regulatory-calibrated domain inputs for key Indian packaged foods
featured in official demonstrations and presentation scenarios (JUDGE_PRESENTATION_GUIDE.md).
Ensures zero-downtime availability and graceful fallback when local DB is unmigrated
or when products are absent from Open Food Facts.
"""

from decimal import Decimal
from typing import Dict, Optional

from app.domain.engines.contracts import (
    ProductEvaluationInput,
    NutrientObservationInput,
    IngredientObservationInput,
    DeclaredClaimInput,
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
)


def _obs(
    code: str,
    val: float,
    unit: str,
    status: NutrientDataStatus = NutrientDataStatus.PRESENT,
    val_serving: Optional[float] = None,
) -> NutrientObservationInput:
    dec_100 = Decimal(str(val)) if val is not None else None
    dec_serving = Decimal(str(val_serving)) if val_serving is not None else None
    return NutrientObservationInput(
        nutrient_code=code,
        per_100g_value=dec_100,
        per_serving_value=dec_serving,
        unit=unit,
        data_status=status,
        measurement_basis=MeasurementBasis.PER_100G,
    )


CURATED_DEMO_PRODUCTS: Dict[str, ProductEvaluationInput] = {
    # 1. Britannia NutriChoice Digestive Biscuits (Demo Case #1)
    "8901030383701": ProductEvaluationInput(
        product_id="8901030383701",
        product_name="Nutri-Choice Digestive Biscuits",
        brand_name="Britannia",
        food_form=FoodForm.SOLID,
        food_category="Biscuits & Bakery",
        package_size="100g",
        serving_size_value=Decimal("25.0"),
        serving_size_unit="g",
        nutrients={
<<<<<<< Updated upstream
            "energy": _obs("energy", 482.0, "kcal", val_serving=120.5),
            "protein": _obs("protein", 8.0, "g", val_serving=2.0),
            "carbohydrates": _obs("carbohydrates", 68.0, "g", val_serving=17.0),
            "total_sugars": _obs("total_sugars", 14.5, "g", val_serving=3.63),
            "added_sugars": _obs("added_sugars", 13.0, "g", val_serving=3.25),
            "total_fat": _obs("total_fat", 21.0, "g", val_serving=5.25),
            "saturated_fat": _obs("saturated_fat", 10.0, "g", val_serving=2.5),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "sodium": _obs("sodium", 450.0, "mg", val_serving=112.5),
            "dietary_fibre": _obs("dietary_fibre", 6.2, "g", val_serving=1.55),
=======
            "energy": _obs("energy", 482.0, "kcal"),
            "protein": _obs("protein", 8.0, "g"),
            "carbohydrates": _obs("carbohydrates", 63.5, "g"),
            "carbohydrates": _obs("carbohydrates", 68.0, "g"),
            "total_sugars": _obs("total_sugars", 14.5, "g"),
            "added_sugars": _obs("added_sugars", 13.0, "g"),
            "total_fat": _obs("total_fat", 21.0, "g"),
            "saturated_fat": _obs("saturated_fat", 10.0, "g"),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
            "sodium": _obs("sodium", 450.0, "mg"),
            "dietary_fibre": _obs("dietary_fibre", 6.2, "g"),
>>>>>>> Stashed changes
        },
        ingredients=[
            IngredientObservationInput(
                ingredient_code="wheat_flour", declared_label_text="Refined Wheat Flour (Maida)",
                sequence_order=1, is_fssai_major_allergen=True
            ),
            IngredientObservationInput(
                ingredient_code="wheat_bran", declared_label_text="Wheat Bran (14%)",
                sequence_order=2
            ),
            IngredientObservationInput(
                ingredient_code="sugar", declared_label_text="Sugar",
                sequence_order=3
            ),
            IngredientObservationInput(
                ingredient_code="palmolein_oil", declared_label_text="Refined Palm Oil",
                sequence_order=4
            ),
            IngredientObservationInput(
                ingredient_code="salt", declared_label_text="Iodised Salt",
                sequence_order=5
            ),
        ],
        declared_claims=[
            DeclaredClaimInput(claim_code="HIGH_FIBRE", raw_label_statement="High Fibre"),
            DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat"),
        ],
        data_source_id="curated_demo_catalog",
    ),

    # 2. Maggi 2-Minute Masala Noodles (Demo Case #2)
    "8901058860002": ProductEvaluationInput(
        product_id="8901058860002",
        product_name="2-Minute Masala Instant Noodles",
        brand_name="Maggi",
        food_form=FoodForm.SOLID,
        food_category="Instant Noodles",
        package_size="70g",
        serving_size_value=Decimal("70.0"),
        serving_size_unit="g",
        nutrients={
            "energy": _obs("energy", 427.0, "kcal", val_serving=298.9),
            "protein": _obs("protein", 8.0, "g", val_serving=5.6),
            "carbohydrates": _obs("carbohydrates", 63.5, "g", val_serving=44.45),
            "total_sugars": _obs("total_sugars", 2.2, "g", val_serving=1.54),
            "added_sugars": _obs("added_sugars", 1.5, "g", val_serving=1.05),
            "total_fat": _obs("total_fat", 15.7, "g", val_serving=10.99),
            "saturated_fat": _obs("saturated_fat", 6.8, "g", val_serving=4.76),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "sodium": _obs("sodium", 1060.0, "mg", val_serving=742.0),
            "dietary_fibre": _obs("dietary_fibre", 3.6, "g", val_serving=2.52),
        },
        ingredients=[
            IngredientObservationInput(
                ingredient_code="wheat_flour", declared_label_text="Refined Wheat Flour (Maida)",
                sequence_order=1, is_fssai_major_allergen=True
            ),
            IngredientObservationInput(
                ingredient_code="palm_oil", declared_label_text="Palm Oil",
                sequence_order=2
            ),
            IngredientObservationInput(
                ingredient_code="salt", declared_label_text="Iodised Salt",
                sequence_order=3
            ),
            IngredientObservationInput(
                ingredient_code="flavour_enhancer_635", declared_label_text="Flavour Enhancer (INS 635)",
                sequence_order=4
            ),
        ],
        declared_claims=[
            DeclaredClaimInput(claim_code="SOURCE_IRON", raw_label_statement="Goodness of Iron"),
            DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat"),
        ],
        data_source_id="curated_demo_catalog",
    ),

    # 3. Kissan Fresh Tomato Ketchup (Demo Case & Integration Test Product)
    "8901030825279": ProductEvaluationInput(
        product_id="8901030825279",
        product_name="Fresh Tomato Ketchup",
        brand_name="Kissan",
        food_form=FoodForm.LIQUID,
        food_category="Condiments & Sauces",
        package_size="500g",
        serving_size_value=Decimal("15.0"),
        serving_size_unit="g",
        nutrients={
<<<<<<< Updated upstream
            "energy": _obs("energy", 133.0, "kcal", val_serving=19.95),
            "protein": _obs("protein", 1.2, "g", val_serving=0.18),
            "carbohydrates": _obs("carbohydrates", 31.0, "g", val_serving=4.65),
            "total_sugars": _obs("total_sugars", 27.0, "g", val_serving=4.05),
            "added_sugars": _obs("added_sugars", 24.5, "g", val_serving=3.68),
            "total_fat": _obs("total_fat", 0.1, "g", val_serving=0.02),
            "saturated_fat": _obs("saturated_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "sodium": _obs("sodium", 850.0, "mg", val_serving=127.5),
            "dietary_fibre": _obs("dietary_fibre", 0.5, "g", val_serving=0.08),
=======
            "energy": _obs("energy", 133.0, "kcal"),
            "protein": _obs("protein", 1.2, "g"),
            "carbohydrates": _obs("carbohydrates", 28.0, "g"),
            "total_sugars": _obs("total_sugars", 27.0, "g"),
            "added_sugars": _obs("added_sugars", 24.5, "g"),
            "total_fat": _obs("total_fat", 0.1, "g"),
            "saturated_fat": _obs("saturated_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
            "sodium": _obs("sodium", 850.0, "mg"),
            "dietary_fibre": _obs("dietary_fibre", 0.5, "g"),
>>>>>>> Stashed changes
        },
        ingredients=[
            IngredientObservationInput(
                ingredient_code="tomato_paste", declared_label_text="Tomato Paste (28%)",
                sequence_order=1
            ),
            IngredientObservationInput(
                ingredient_code="water", declared_label_text="Water",
                sequence_order=2
            ),
            IngredientObservationInput(
                ingredient_code="sugar", declared_label_text="Sugar",
                sequence_order=3
            ),
            IngredientObservationInput(
                ingredient_code="salt", declared_label_text="Salt",
                sequence_order=4
            ),
            IngredientObservationInput(
                ingredient_code="acidity_regulator", declared_label_text="Acidity Regulator (INS 260)",
                sequence_order=5
            ),
        ],
        declared_claims=[
            DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat"),
        ],
        data_source_id="curated_demo_catalog",
    ),

    # 4. Haldiram's Aloo Bhujia (Demo Case #5)
    "8904063200150": ProductEvaluationInput(
        product_id="8904063200150",
        product_name="Aloo Bhujia Spicy Namkeen",
        brand_name="Haldiram's",
        food_form=FoodForm.SOLID,
        food_category="Traditional Namkeen",
        package_size="150g",
        serving_size_value=Decimal("30.0"),
        serving_size_unit="g",
        nutrients={
            "energy": _obs("energy", 580.0, "kcal", val_serving=174.0),
            "protein": _obs("protein", 9.0, "g", val_serving=2.7),
            "carbohydrates": _obs("carbohydrates", 42.0, "g", val_serving=12.6),
            "total_sugars": _obs("total_sugars", 1.5, "g", val_serving=0.45),
            "added_sugars": _obs("added_sugars", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "total_fat": _obs("total_fat", 42.0, "g", val_serving=12.6),
            "saturated_fat": _obs("saturated_fat", 18.0, "g", val_serving=5.4),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "sodium": _obs("sodium", 780.0, "mg", val_serving=234.0),
            "dietary_fibre": _obs("dietary_fibre", 4.0, "g", val_serving=1.2),
        },
        ingredients=[
            IngredientObservationInput(
                ingredient_code="potato", declared_label_text="Potatoes (44%)",
                sequence_order=1
            ),
            IngredientObservationInput(
                ingredient_code="gram_flour", declared_label_text="Edible Chickpea Flour",
                sequence_order=2
            ),
            IngredientObservationInput(
                ingredient_code="palmolein_oil", declared_label_text="Edible Vegetable Oil (Palmolein)",
                sequence_order=3
            ),
            IngredientObservationInput(
                ingredient_code="salt", declared_label_text="Iodised Salt",
                sequence_order=4
            ),
            IngredientObservationInput(
                ingredient_code="spices", declared_label_text="Spices and Condiments",
                sequence_order=5
            ),
        ],
        declared_claims=[
            DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat"),
        ],
        data_source_id="curated_demo_catalog",
    ),

    # Also map Haldiram's alternate retail barcode
    "8901491101838": ProductEvaluationInput(
        product_id="8901491101838",
        product_name="Aloo Bhujia Spicy Namkeen",
        brand_name="Haldiram's",
        food_form=FoodForm.SOLID,
        food_category="Traditional Namkeen",
        package_size="150g",
        serving_size_value=Decimal("30.0"),
        serving_size_unit="g",
        nutrients={
            "energy": _obs("energy", 580.0, "kcal", val_serving=174.0),
            "protein": _obs("protein", 9.0, "g", val_serving=2.7),
            "carbohydrates": _obs("carbohydrates", 42.0, "g", val_serving=12.6),
            "total_sugars": _obs("total_sugars", 1.5, "g", val_serving=0.45),
            "added_sugars": _obs("added_sugars", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "total_fat": _obs("total_fat", 42.0, "g", val_serving=12.6),
            "saturated_fat": _obs("saturated_fat", 18.0, "g", val_serving=5.4),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "sodium": _obs("sodium", 780.0, "mg", val_serving=234.0),
            "dietary_fibre": _obs("dietary_fibre", 4.0, "g", val_serving=1.2),
        },
        ingredients=[
            IngredientObservationInput(
                ingredient_code="potato", declared_label_text="Potatoes (44%)",
                sequence_order=1
            ),
            IngredientObservationInput(
                ingredient_code="gram_flour", declared_label_text="Edible Chickpea Flour",
                sequence_order=2
            ),
            IngredientObservationInput(
                ingredient_code="palmolein_oil", declared_label_text="Edible Vegetable Oil (Palmolein)",
                sequence_order=3
            ),
            IngredientObservationInput(
                ingredient_code="salt", declared_label_text="Iodised Salt",
                sequence_order=4
            ),
        ],
        declared_claims=[
            DeclaredClaimInput(claim_code="TRANS_FAT_FREE", raw_label_statement="Zero Trans Fat"),
        ],
        data_source_id="curated_demo_catalog",
    ),

    # 5. Real Fruit Power Mixed Fruit Juice (Demo Case #4)
    "8901207010497": ProductEvaluationInput(
        product_id="8901207010497",
        product_name="Real Fruit Power Mixed Fruit Juice",
        brand_name="Real",
        food_form=FoodForm.LIQUID,
        food_category="Beverages & Juices",
        package_size="1000ml",
        serving_size_value=Decimal("200.0"),
        serving_size_unit="ml",
        nutrients={
<<<<<<< Updated upstream
            "energy": _obs("energy", 56.0, "kcal", val_serving=112.0),
            "protein": _obs("protein", 0.4, "g", val_serving=0.8),
            "carbohydrates": _obs("carbohydrates", 13.5, "g", val_serving=27.0),
            "total_sugars": _obs("total_sugars", 13.0, "g", val_serving=26.0),
            "added_sugars": _obs("added_sugars", 11.5, "g", val_serving=23.0),
            "total_fat": _obs("total_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "saturated_fat": _obs("saturated_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "sodium": _obs("sodium", 10.0, "mg", val_serving=20.0),
            "dietary_fibre": _obs("dietary_fibre", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
=======
            "energy": _obs("energy", 56.0, "kcal"),
            "protein": _obs("protein", 0.4, "g"),
            "carbohydrates": _obs("carbohydrates", 14.0, "g"),
            "total_sugars": _obs("total_sugars", 13.0, "g"),
            "added_sugars": _obs("added_sugars", 11.5, "g"),
            "total_fat": _obs("total_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
            "saturated_fat": _obs("saturated_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
            "sodium": _obs("sodium", 10.0, "mg"),
            "dietary_fibre": _obs("dietary_fibre", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
>>>>>>> Stashed changes
        },
        ingredients=[
            IngredientObservationInput(
                ingredient_code="water", declared_label_text="Water",
                sequence_order=1
            ),
            IngredientObservationInput(
                ingredient_code="fruit_concentrate", declared_label_text="Mixed Fruit Concentrate (18%)",
                sequence_order=2
            ),
            IngredientObservationInput(
                ingredient_code="sugar", declared_label_text="Sugar",
                sequence_order=3
            ),
            IngredientObservationInput(
                ingredient_code="acidity_regulator", declared_label_text="Acidity Regulator (INS 330)",
                sequence_order=4
            ),
        ],
        declared_claims=[
            DeclaredClaimInput(claim_code="SOURCE_VITAMIN_C", raw_label_statement="Source of Vitamin C"),
        ],
        data_source_id="curated_demo_catalog",
    ),

    # 6. Cadbury Bournvita Chocolate Drink (Demo Case #3)
    "8901233024013": ProductEvaluationInput(
        product_id="8901233024013",
        product_name="Bournvita Chocolate Health Drink",
        brand_name="Cadbury",
        food_form=FoodForm.SOLID,
        food_category="Malted Food Drink",
        package_size="500g",
        serving_size_value=Decimal("20.0"),
        serving_size_unit="g",
        nutrients={
<<<<<<< Updated upstream
            "energy": _obs("energy", 388.0, "kcal", val_serving=77.6),
            "protein": _obs("protein", 7.0, "g", val_serving=1.4),
            "carbohydrates": _obs("carbohydrates", 85.2, "g", val_serving=17.04),
            "total_sugars": _obs("total_sugars", 32.0, "g", val_serving=6.4),
            "added_sugars": _obs("added_sugars", 28.0, "g", val_serving=5.6),
            "total_fat": _obs("total_fat", 1.8, "g", val_serving=0.36),
            "saturated_fat": _obs("saturated_fat", 0.9, "g", val_serving=0.18),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO, val_serving=0.0),
            "sodium": _obs("sodium", 150.0, "mg", val_serving=30.0),
            "dietary_fibre": _obs("dietary_fibre", 1.5, "g", val_serving=0.3),
=======
            "energy": _obs("energy", 388.0, "kcal"),
            "protein": _obs("protein", 7.0, "g"),
            "carbohydrates": _obs("carbohydrates", 85.4, "g"),
            "total_sugars": _obs("total_sugars", 32.0, "g"),
            "added_sugars": _obs("added_sugars", 28.0, "g"),
            "total_fat": _obs("total_fat", 1.8, "g"),
            "saturated_fat": _obs("saturated_fat", 0.9, "g"),
            "trans_fat": _obs("trans_fat", 0.0, "g", NutrientDataStatus.EXPLICITLY_ZERO),
            "sodium": _obs("sodium", 150.0, "mg"),
            "dietary_fibre": _obs("dietary_fibre", 1.5, "g"),
>>>>>>> Stashed changes
        },
        ingredients=[
            IngredientObservationInput(
                ingredient_code="cereal_extract", declared_label_text="Cereal Extract (Barley, Wheat)",
                sequence_order=1
            ),
            IngredientObservationInput(
                ingredient_code="sugar", declared_label_text="Sugar",
                sequence_order=2
            ),
            IngredientObservationInput(
                ingredient_code="cocoa_solids", declared_label_text="Cocoa Solids",
                sequence_order=3
            ),
            IngredientObservationInput(
                ingredient_code="milk_solids", declared_label_text="Milk Solids",
                sequence_order=4, is_fssai_major_allergen=True
            ),
        ],
        declared_claims=[
            DeclaredClaimInput(claim_code="IMMUNITY_GROWTH", raw_label_statement="Immunity & Growth"),
        ],
        data_source_id="curated_demo_catalog",
    ),
}

BARCODE_ALIASES: Dict[str, str] = {
    "8901030383701": "8901063142022",  # NutriChoice candidate -> verified
    "8901063142022": "8901030383701",  # NutriChoice verified -> candidate
    "8901058860002": "8901058851298",  # Maggi candidate -> verified
    "8901058851298": "8901058860002",  # Maggi verified -> candidate
    "8901233024013": "8901233023724",  # Bournvita candidate -> verified
    "8901233023724": "8901233024013",  # Bournvita verified -> candidate
    "8904063200150": "8904063218124",  # Haldiram's candidate -> verified
    "8904063218124": "8904063200150",  # Haldiram's verified -> candidate
    "8901491101838": "8901491101837",  # Lay's candidate -> verified
    "8901491101837": "8901491101838",  # Lay's verified -> candidate
}

CURATED_IMAGE_URLS: Dict[str, str] = {
    "8901063142022": "/static/products/8901063142022.png",
    "8901030383701": "/static/products/8901030383701.png",
    "8901058851298": "/static/products/8901058851298.png",
    "8901058860002": "/static/products/8901058860002.png",
    "8901233023724": "/static/products/8901233023724.png",
    "8901233024013": "/static/products/8901233024013.png",
    "8906010500863": "/static/products/8906010500863.png",
    "8901764061103": "/static/products/8901764061103.png",
    "7622201756697": "/static/products/7622201756697.png",
    "8901491101837": "/static/products/8901491101837.png",
    "8901491101838": "/static/products/8901491101838.png",
    "8901491100519": "/static/products/8901491100519.png",
    "8901719100956": "/static/products/8901719100956.png",
    "8904063218124": "/static/products/8904063218124.png",
    "8904063200150": "/static/products/8904063200150.png",
    "8901058868036": "/static/products/8901058868036.png",
    "8901030825279": "/static/products/8901030825279.png",
    "8901262010017": "/static/products/8901262010017.png",
    "8901207010497": "/static/products/8901207010497.png",
}


def get_curated_product(barcode: str) -> Optional[ProductEvaluationInput]:
    """Retrieves a pre-calibrated product from the curated demonstration catalog."""
    clean_barcode = barcode.strip()
    target_barcode = BARCODE_ALIASES.get(clean_barcode, clean_barcode)
    return CURATED_DEMO_PRODUCTS.get(clean_barcode) or CURATED_DEMO_PRODUCTS.get(target_barcode)


def get_curated_image_url(barcode: str) -> Optional[str]:
    """Retrieves product front packaging image URL from curated catalogue."""
    clean_barcode = barcode.strip()
    target_barcode = BARCODE_ALIASES.get(clean_barcode, clean_barcode)
    return CURATED_IMAGE_URLS.get(clean_barcode) or CURATED_IMAGE_URLS.get(target_barcode) or f"/static/products/{clean_barcode}.png"
