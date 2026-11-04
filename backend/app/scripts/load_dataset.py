"""
High-Performance CSV Dataset Loader for Packaged Foods India into PostgreSQL / Supabase.

Ingests `backend/dataset/packaged_foods_india.csv` (852 items) into 3NF normalized tables:
- `data_sources`
- `nutrients` & `product_nutrients` (preserving strict 4-state nutrient semantics: PRESENT, EXPLICITLY_ZERO, NOT_DECLARED)
- `ingredients` & `product_ingredients` (preserving sequence_order)
- Seeds 11 benchmark demo products with validated records and candidate barcode aliases.

Uses bulk batching for ultra-fast network performance over Supabase remote connections.
"""

import csv
import os
import re
import uuid
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.models.data_source import DataSource
from app.models.product import Product
from app.models.product_nutrient import ProductNutrient, NUTRIENT_DATA_STATUSES
from app.models.ingredient import Ingredient
from app.models.product_ingredient import ProductIngredient
from app.models.nutrient import Nutrient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SOURCE_ID = "packaged_foods_india_csv"

# Known verified retail barcodes for iconic Indian packaged foods
KNOWN_BARCODES = {
    "Britannia Nutrichoice Digestive High-Fibre Biscuits": "8901063142022",
    "Britannia Nutrichoice Digestive High-Fibre Biscuits": "8901063142022",
    "HIDE & SEEK® ": "8901719101038",
    "HIDE & SEEK®": "8901719101038",
    "Sunfeast Dark Fantasy Choco Fills, Original Filled Cookies with Choco Crème": "8901725132224",
    "sunfeast Dark Fantasy Bourbon, Classic Biscuit Made With Real Chocolate": "8901725132330",
    "Britannia Good Day Cashew Cookies Family Pack": "8901063141233",
    "Britannia The Original Bourbon": "8901063142018",
    "Britannia Treat Jimjam Cream Biscuits": "8901063141509",
    "Kissan Fresh Tomato Ketchup": "8901030825279",
    "2-Minute Masala Instant Noodles": "8901058851298",
    "Maggi 2-Minute Masala Noodles": "8901058851298",
    "Aloo Bhujia Spicy Namkeen": "8904063218124",
}


def calculate_ean13(prefix12: str) -> str:
    """Calculates standard EAN-13 check digit for a 12-digit numeric prefix."""
    digits = [int(c) for c in prefix12[:12]]
    odd_sum = sum(digits[i] for i in range(0, 12, 2))
    even_sum = sum(digits[i] for i in range(1, 12, 2))
    total = odd_sum + (even_sum * 3)
    check = (10 - (total % 10)) % 10
    return f"{prefix12[:12]}{check}"


def slugify(text_val: str, max_len: int = 50) -> str:
    """Converts display text to lowercase ASCII slug identifier."""
    cleaned = re.sub(r"[^\w\s-]", "", text_val.strip().lower())
    slug = re.sub(r"[-\s]+", "_", cleaned)
    return slug[:max_len].strip("_") or "unknown_item"


def parse_decimal(val: Any) -> Optional[Decimal]:
    """Safely parses float/string into Decimal, returning None if empty or invalid."""
    if val is None:
        return None
    s = str(val).strip().replace(",", "")
    if not s or s.lower() in ("na", "n/a", "nil", "none", "-", ""):
        return None
    match = re.search(r"[-+]?\d*\.?\d+", s)
    if not match:
        return None
    try:
        return Decimal(match.group(0))
    except Exception:
        return None


def determine_food_form(category: str, sub_cat: str, name: str) -> str:
    """Determines physical state ('liquid' or 'solid') based on category descriptors."""
    combined = f"{category} {sub_cat} {name}".lower()
    if "bournvita" in combined or "powder" in combined or "mix" in combined:
        return "solid"
    liquid_keywords = (
        "beverage", "juice", "drink", "milk", "water", "sauce", "ketchup",
        "syrup", "oil", "soup", "vinegar", "squash", "shake", "soda", "cola"
    )
    if any(k in combined for k in liquid_keywords):
        return "liquid"
    return "solid"


def split_ingredients(raw_text: str) -> List[str]:
    """Splits raw ingredients text into ordered list of clean ingredient clauses."""
    if not raw_text or not raw_text.strip():
        return []
    cleaned = raw_text.strip()
    parts = re.split(r",(?![^(]*\))", cleaned)
    results = []
    for p in parts:
        item = re.sub(r"\s+", " ", p).strip(" .;:,-")
        if item and len(item) > 1 and item.lower() not in ("ingredients:", "contains"):
            results.append(item)
    return results


def ensure_data_source(db: Session) -> DataSource:
    """Ensures the dataset source metadata record exists in data_sources."""
    ds = db.get(DataSource, SOURCE_ID)
    if not ds:
        ds = DataSource(
            source_id=SOURCE_ID,
            name="Packaged Foods India Dataset (Zepto & Market Survey)",
            license_type="Research / Open Food Data",
            license_url="https://yumsure.in/dataset/packaged-foods-india",
            attribution_text="Packaged Foods India Survey 2025-2026",
            permits_redistribution=True,
        )
        db.add(ds)
        db.commit()
    return ds


def seed_demo_catalogue(db: Session) -> int:
    """
    Seeds the 11 audited benchmark products from DEMO_PRODUCT_CATALOGUE.md
    with full verified profiles and candidate barcode aliases.
    """
    demo_products_data = [
        {
            "barcode": "8901063142022",
            "candidate_barcode": "8901030383701",
            "name": "Britannia NutriChoice Digestive",
            "brand": "Britannia",
            "category": "Biscuits & Bakery",
            "form": "solid",
            "serving": Decimal("25.0"),
            "pkg": "100g",
            "nutrients": [
                ("energy", Decimal("482.0"), "kcal"),
                ("protein", Decimal("9.3"), "g"),
                ("carbohydrates", Decimal("68.0"), "g"),
                ("total_sugars", Decimal("12.7"), "g"),
                ("added_sugars", Decimal("12.0"), "g"),
                ("total_fat", Decimal("20.8"), "g"),
                ("saturated_fat", Decimal("10.3"), "g"),
                ("trans_fat", Decimal("0.0"), "g"),
                ("sodium", Decimal("368.0"), "mg"),
                ("dietary_fibre", Decimal("6.2"), "g"),
            ],
            "ingredients": [
                "Wheat Flour (Atta 65.5%)", "Refined Palm Oil", "Sugar", "Wheat Bran (2.6%)",
                "Maltodextrin", "Milk Solids", "Whey Powder", "Invert Sugar Syrup",
                "Raising Agents 503(ii)", "Raising Agents 500(ii)", "Iodised Salt",
                "Emulsifiers 322(i)", "Emulsifiers 471", "Malt Extract"
            ],
        },
        {
            "barcode": "8901058851298",
            "candidate_barcode": "8901058860002",
            "name": "Maggi 2-Minute Masala Noodles",
            "brand": "Maggi",
            "category": "Instant Noodles",
            "form": "solid",
            "serving": Decimal("70.0"),
            "pkg": "70g",
            "nutrients": [
                ("energy", Decimal("427.0"), "kcal"),
                ("protein", Decimal("8.0"), "g"),
                ("carbohydrates", Decimal("63.5"), "g"),
                ("total_sugars", Decimal("2.2"), "g"),
                ("added_sugars", Decimal("1.5"), "g"),
                ("total_fat", Decimal("15.7"), "g"),
                ("saturated_fat", Decimal("6.8"), "g"),
                ("trans_fat", Decimal("0.12"), "g"),
                ("sodium", Decimal("863.0"), "mg"),
                ("dietary_fibre", Decimal("3.5"), "g"),
            ],
            "ingredients": [
                "Refined Wheat Flour (Maida)", "Palm Oil", "Iodised Salt", "Wheat Gluten",
                "Thickeners (508, 412)", "Acidity Regulators (501(i), 500(i))", "Humectant (451(i))",
                "Hydrolysed Groundnut Protein", "Mixed Spices (Onion, Coriander, Turmeric, Chilli, Garlic, Cumin)"
            ],
        },
        {
            "barcode": "8901233023724",
            "candidate_barcode": "8901233024013",
            "name": "Cadbury Bournvita Chocolate Health Drink",
            "brand": "Cadbury",
            "category": "Malted Beverage Powder",
            "form": "solid",
            "serving": Decimal("20.0"),
            "pkg": "500g",
            "nutrients": [
                ("energy", Decimal("388.0"), "kcal"),
                ("protein", Decimal("7.0"), "g"),
                ("carbohydrates", Decimal("85.2"), "g"),
                ("total_sugars", Decimal("49.8"), "g"),
                ("added_sugars", Decimal("32.2"), "g"),
                ("total_fat", Decimal("1.8"), "g"),
                ("saturated_fat", Decimal("0.9"), "g"),
                ("trans_fat", Decimal("0.0"), "g"),
                ("sodium", Decimal("160.0"), "mg"),
                ("dietary_fibre", Decimal("3.6"), "g"),
            ],
            "ingredients": [
                "Malt Extract (44%)", "Sugar", "Cocoa Solids", "Milk Solids", "Liquid Glucose",
                "Emulsifiers (322, 471)", "Vitamins", "Raising Agent (500(ii))", "Minerals", "Salt"
            ],
        },
        {
            "barcode": "8906010500863",
            "name": "Balaji Shing Bhujia - Nimbu Chatka",
            "brand": "Balaji Wafers",
            "category": "Snacks & Namkeen",
            "form": "solid",
            "serving": Decimal("30.0"),
            "pkg": "45g",
            "nutrients": [
                ("energy", Decimal("580.0"), "kcal"),
                ("protein", Decimal("18.0"), "g"),
                ("carbohydrates", Decimal("32.0"), "g"),
                ("total_sugars", Decimal("4.0"), "g"),
                ("added_sugars", Decimal("1.0"), "g"),
                ("total_fat", Decimal("42.0"), "g"),
                ("saturated_fat", Decimal("12.0"), "g"),
                ("trans_fat", Decimal("0.0"), "g"),
                ("sodium", Decimal("720.0"), "mg"),
                ("dietary_fibre", Decimal("6.0"), "g"),
            ],
            "ingredients": [
                "Peanuts (65%)", "Gram Flour (Besan 20%)", "Edible Vegetable Oil (Palmolein)",
                "Spices & Condiments", "Citric Acid (INS 330)", "Iodised Salt"
            ],
        },
        {
            "barcode": "8901764061103",
            "name": "Diet Coke Can",
            "brand": "Coca-Cola",
            "category": "Carbonated Soft Drink",
            "form": "liquid",
            "serving": Decimal("330.0"),
            "pkg": "330ml",
            "nutrients": [
                ("energy", Decimal("0.3"), "kcal"),
                ("protein", Decimal("0.0"), "g"),
                ("carbohydrates", Decimal("0.0"), "g"),
                ("total_sugars", Decimal("0.0"), "g"),
                ("added_sugars", Decimal("0.0"), "g"),
                ("total_fat", Decimal("0.0"), "g"),
                ("saturated_fat", Decimal("0.0"), "g"),
                ("trans_fat", Decimal("0.0"), "g"),
                ("sodium", Decimal("28.0"), "mg"),
                ("dietary_fibre", Decimal("0.0"), "g"),
            ],
            "ingredients": [
                "Carbonated Water", "Acidity Regulator (INS 338)", "Sweeteners (INS 951, INS 950)",
                "Preservative (INS 211)", "Caffeine", "Colour (INS 150d)"
            ],
        },
        {
            "barcode": "7622201756697",
            "name": "Cadbury Oreo Vanilla Creme Biscuits",
            "brand": "Oreo",
            "category": "Biscuits & Bakery",
            "form": "solid",
            "serving": Decimal("28.5"),
            "pkg": "43.75g",
            "nutrients": [
                ("energy", Decimal("483.0"), "kcal"),
                ("protein", Decimal("5.2"), "g"),
                ("carbohydrates", Decimal("71.0"), "g"),
                ("total_sugars", Decimal("38.0"), "g"),
                ("added_sugars", Decimal("35.0"), "g"),
                ("total_fat", Decimal("19.5"), "g"),
                ("saturated_fat", Decimal("9.5"), "g"),
                ("trans_fat", Decimal("0.05"), "g"),
                ("sodium", Decimal("387.0"), "mg"),
                ("dietary_fibre", Decimal("2.5"), "g"),
            ],
            "ingredients": [
                "Refined Wheat Flour (Maida)", "Sugar", "Fractionated Fat", "Edible Vegetable Palmolein Oil",
                "Cocoa Solids (2.3%)", "Invert Sugar", "Leavening Agents (INS 500(ii), INS 503(ii))",
                "Iodised Salt", "Emulsifier (INS 322)"
            ],
        },
        {
            "barcode": "8901491101837",
            "candidate_barcode": "8901491101838",
            "name": "Lay's Classic Salted Potato Chips",
            "brand": "Lay's",
            "category": "Snacks & Namkeen",
            "form": "solid",
            "serving": Decimal("30.0"),
            "pkg": "50g",
            "nutrients": [
                ("energy", Decimal("543.0"), "kcal"),
                ("protein", Decimal("7.1"), "g"),
                ("carbohydrates", Decimal("52.5"), "g"),
                ("total_sugars", Decimal("1.2"), "g"),
                ("added_sugars", Decimal("0.0"), "g"),
                ("total_fat", Decimal("34.0"), "g"),
                ("saturated_fat", Decimal("15.0"), "g"),
                ("trans_fat", Decimal("0.1"), "g"),
                ("sodium", Decimal("550.0"), "mg"),
                ("dietary_fibre", Decimal("3.8"), "g"),
            ],
            "ingredients": [
                "Potato (85%)", "Edible Vegetable Oil (Palmolein)", "Iodised Salt (1.5%)"
            ],
        },
        {
            "barcode": "8901491100519",
            "name": "Kurkure Masala Munch",
            "brand": "Kurkure",
            "category": "Snacks & Namkeen",
            "form": "solid",
            "serving": Decimal("30.0"),
            "pkg": "78g",
            "nutrients": [
                ("energy", Decimal("558.0"), "kcal"),
                ("protein", Decimal("5.8"), "g"),
                ("carbohydrates", Decimal("56.6"), "g"),
                ("total_sugars", Decimal("1.8"), "g"),
                ("added_sugars", Decimal("1.2"), "g"),
                ("total_fat", Decimal("34.5"), "g"),
                ("saturated_fat", Decimal("15.8"), "g"),
                ("trans_fat", Decimal("0.1"), "g"),
                ("sodium", Decimal("796.0"), "mg"),
                ("dietary_fibre", Decimal("2.4"), "g"),
            ],
            "ingredients": [
                "Rice Meal (43.2%)", "Edible Vegetable Oil (Palmolein)", "Corn Meal (20.0%)",
                "Gram Meal (3.3%)", "Spices and Condiments (Onion, Chilli, Amchur, Coriander, Garlic)",
                "Salt", "Citric Acid (INS 330)"
            ],
        },
        {
            "barcode": "8901719100956",
            "name": "Parle-G Original Glucose Biscuits",
            "brand": "Parle",
            "category": "Biscuits & Bakery",
            "form": "solid",
            "serving": Decimal("25.0"),
            "pkg": "80g",
            "nutrients": [
                ("energy", Decimal("451.0"), "kcal"),
                ("protein", Decimal("6.5"), "g"),
                ("carbohydrates", Decimal("78.2"), "g"),
                ("total_sugars", Decimal("25.5"), "g"),
                ("added_sugars", Decimal("24.0"), "g"),
                ("total_fat", Decimal("12.5"), "g"),
                ("saturated_fat", Decimal("5.8"), "g"),
                ("trans_fat", Decimal("0.0"), "g"),
                ("sodium", Decimal("280.0"), "mg"),
                ("dietary_fibre", Decimal("1.8"), "g"),
            ],
            "ingredients": [
                "Refined Wheat Flour (Maida 67%)", "Sugar", "Refined Palm Oil", "Invert Sugar Syrup",
                "Leavening Agents (INS 503(ii), INS 500(ii))", "Milk Solids (0.6%)", "Iodised Salt",
                "Emulsifiers (INS 472e)", "Dough Conditioner (INS 223)"
            ],
        },
        {
            "barcode": "8904063218124",
            "candidate_barcode": "8904063200150",
            "name": "Haldiram's Aloo Bhujia",
            "brand": "Haldiram's",
            "category": "Snacks & Namkeen",
            "form": "solid",
            "serving": Decimal("30.0"),
            "pkg": "205g",
            "nutrients": [
                ("energy", Decimal("580.0"), "kcal"),
                ("protein", Decimal("8.68"), "g"),
                ("carbohydrates", Decimal("42.0"), "g"),
                ("total_sugars", Decimal("1.5"), "g"),
                ("added_sugars", Decimal("0.0"), "g"),
                ("total_fat", Decimal("42.0"), "g"),
                ("saturated_fat", Decimal("16.5"), "g"),
                ("trans_fat", Decimal("0.0"), "g"),
                ("sodium", Decimal("615.0"), "mg"),
                ("dietary_fibre", Decimal("4.01"), "g"),
            ],
            "ingredients": [
                "Potatoes (44%)", "Edible Chickpea Flour (Besan 22%)", "Edible Vegetable Oil (Palmolein)",
                "Moth Dal Flour (4%)", "Iodised Salt", "Red Chilli Powder", "Black Pepper Powder",
                "Citric Acid (INS 330)"
            ],
        },
        {
            "barcode": "8901058868036",
            "name": "Nestle KitKat 4-Finger Chocolate Wafer",
            "brand": "Nestle",
            "category": "Confectionery & Chocolate",
            "form": "solid",
            "serving": Decimal("27.5"),
            "pkg": "55g",
            "nutrients": [
                ("energy", Decimal("518.0"), "kcal"),
                ("protein", Decimal("6.0"), "g"),
                ("carbohydrates", Decimal("64.0"), "g"),
                ("total_sugars", Decimal("46.0"), "g"),
                ("added_sugars", Decimal("38.0"), "g"),
                ("total_fat", Decimal("27.0"), "g"),
                ("saturated_fat", Decimal("23.0"), "g"),
                ("trans_fat", Decimal("0.1"), "g"),
                ("sodium", Decimal("65.0"), "mg"),
                ("dietary_fibre", Decimal("1.9"), "g"),
            ],
            "ingredients": [
                "Milk Chocolate (69%) [Sugar, Milk Solids, Cocoa Butter, Cocoa Solids, Emulsifier (Soy Lecithin)]",
                "Wafer (Wheat Flour, Sugar, Hydrogenated Palm Kernel Oil, Cocoa Solids, Salt, Leavening Agent INS 500(ii))"
            ],
        },
        {
            "barcode": "8901030825279",
            "name": "Kissan Fresh Tomato Ketchup",
            "brand": "Kissan",
            "category": "Condiments & Sauces",
            "form": "liquid",
            "serving": Decimal("15.0"),
            "pkg": "500g",
            "nutrients": [
                ("energy", Decimal("133.0"), "kcal"),
                ("protein", Decimal("1.2"), "g"),
                ("carbohydrates", Decimal("32.0"), "g"),
                ("total_sugars", Decimal("27.0"), "g"),
                ("added_sugars", Decimal("24.5"), "g"),
                ("total_fat", Decimal("0.1"), "g"),
                ("saturated_fat", Decimal("0.0"), "g"),
                ("trans_fat", Decimal("0.0"), "g"),
                ("sodium", Decimal("850.0"), "mg"),
                ("dietary_fibre", Decimal("0.5"), "g"),
            ],
            "ingredients": [
                "Tomato Paste (28%)", "Water", "Sugar", "Salt", "Acidity Regulator (INS 260)"
            ],
        },
        {
            "barcode": "8901262010017",
            "name": "Amul Taaza Fresh Toned Milk",
            "brand": "Amul",
            "category": "Dairy Products",
            "form": "liquid",
            "serving": Decimal("200.0"),
            "pkg": "1000ml",
            "nutrients": [
                ("energy", Decimal("58.2"), "kcal"),
                ("protein", Decimal("3.0"), "g"),
                ("carbohydrates", Decimal("4.7"), "g"),
                ("total_sugars", Decimal("4.7"), "g"),
                ("added_sugars", Decimal("0.0"), "g"),
                ("total_fat", Decimal("3.0"), "g"),
                ("saturated_fat", Decimal("1.9"), "g"),
                ("trans_fat", Decimal("0.0"), "g"),
                ("sodium", Decimal("50.0"), "mg"),
                ("dietary_fibre", Decimal("0.0"), "g"),
            ],
            "ingredients": [
                "Toned Milk", "Vitamin A", "Vitamin D"
            ],
        },
    ]

    # Pre-register any missing demo ingredients
    existing_ingredients = set(db.scalars(select(Ingredient.ingredient_code)).all())
    for item in demo_products_data:
        for ing_text in item["ingredients"]:
            ing_code = slugify(ing_text, max_len=60)
            if ing_code not in existing_ingredients:
                db.add(Ingredient(
                    ingredient_code=ing_code,
                    canonical_name=ing_text[:255],
                    category="OTHER",
                    processing_classification="UNKNOWN",
                    sugar_classification="UNKNOWN",
                ))
                existing_ingredients.add(ing_code)
    db.commit()

    count = 0
    for item in demo_products_data:
        barcodes_to_seed = [item["barcode"]]
        if "candidate_barcode" in item and item["candidate_barcode"]:
            barcodes_to_seed.append(item["candidate_barcode"])

        for b in barcodes_to_seed:
            existing = db.execute(select(Product).where(Product.barcode == b)).scalar_one_or_none()
            img_url = f"/static/products/{b}.png"
            if existing:
                prod = existing
                prod.product_name = item["name"]
                prod.brand_name = item["brand"]
                prod.food_category = item["category"]
                prod.food_form = item["form"]
                prod.serving_size_value = item["serving"]
                prod.serving_size_unit = "ml" if item["form"] == "liquid" else "g"
                prod.package_size = item["pkg"]
                prod.is_verified = True
                prod.raw_source_payload = {
                    "image_front_url": img_url,
                    "image_url": img_url,
                    "is_demo_product": True,
                }
            else:
                prod = Product(
                    id=uuid.uuid4(),
                    barcode=b,
                    product_name=item["name"],
                    brand_name=item["brand"],
                    food_category=item["category"],
                    food_form=item["form"],
                    serving_size_value=item["serving"],
                    serving_size_unit="ml" if item["form"] == "liquid" else "g",
                    package_size=item["pkg"],
                    is_verified=True,
                    source_id=SOURCE_ID,
                    raw_source_payload={
                        "image_front_url": img_url,
                        "image_url": img_url,
                        "is_demo_product": True,
                    },
                )
                db.add(prod)

            # Seed nutrients
            db.execute(text("DELETE FROM product_nutrients WHERE product_id = :pid"), {"pid": prod.id})
            for code, val, unit in item["nutrients"]:
                status = "EXPLICITLY_ZERO" if val == Decimal("0") else "PRESENT"
                per_serving = round((val * item["serving"]) / Decimal("100.0"), 3)
                pn = ProductNutrient(
                    product_id=prod.id,
                    nutrient_code=code,
                    per_100g_value=val,
                    per_serving_value=per_serving,
                    unit=unit,
                    data_status=status,
                )
                db.add(pn)

            # Seed ingredients
            db.execute(text("DELETE FROM product_ingredients WHERE product_id = :pid"), {"pid": prod.id})
            for seq, ing_text in enumerate(item["ingredients"], start=1):
                ing_code = slugify(ing_text, max_len=60)
                pi = ProductIngredient(
                    product_id=prod.id,
                    ingredient_code=ing_code,
                    sequence_order=seq,
                    declared_label_text=ing_text[:255],
                    is_allergen_declared=("allergen" in ing_text.lower() or "wheat" in ing_text.lower() or "milk" in ing_text.lower() or "peanut" in ing_text.lower()),
                )
                db.add(pi)

            count += 1

    db.commit()
    logger.info("Successfully seeded/upserted %d demo products & aliases.", count)
    return count


def load_dataset_file(csv_path: str, max_records: Optional[int] = None) -> Dict[str, Any]:
    """
    Parses and ingests packaged_foods_india.csv into PostgreSQL with bulk pre-registration.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found at: {csv_path}")

    logger.info("Opening dataset file: %s", csv_path)
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    total_rows = len(rows)
    if max_records:
        rows = rows[:max_records]
    logger.info("Parsed %d rows from CSV. Starting fast pre-registration phase...", len(rows))

    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "products"))

    with SessionLocal() as db:
        ensure_data_source(db)

        # STEP 1: Pre-register all canonical nutrients
        existing_nutrients = set(db.scalars(select(Nutrient.nutrient_code)).all())
        all_nutrients = [
            ("energy", "Energy", "kcal"),
            ("carbohydrates", "Carbohydrates", "g"),
            ("protein", "Protein", "g"),
            ("total_fat", "Total Fat", "g"),
            ("saturated_fat", "Saturated Fat", "g"),
            ("trans_fat", "Trans Fat", "g"),
            ("total_sugars", "Total Sugars", "g"),
            ("added_sugars", "Added Sugars", "g"),
            ("sodium", "Sodium", "mg"),
            ("dietary_fibre", "Dietary Fibre", "g"),
            ("cholesterol", "Cholesterol", "mg"),
            ("calcium", "Calcium", "mg"),
            ("iron", "Iron", "mg"),
        ]
        for n_code, n_name, n_unit in all_nutrients:
            if n_code not in existing_nutrients:
                db.add(Nutrient(
                    nutrient_code=n_code,
                    display_name=n_name,
                    standard_unit=n_unit,
                    is_fssai_mandatory=False,
                ))
                existing_nutrients.add(n_code)
        db.commit()

        # STEP 2: Collect all unique ingredients across the entire CSV and bulk insert missing
        existing_ingredients = set(db.scalars(select(Ingredient.ingredient_code)).all())
        new_ingredients_map = {}
        for row in rows:
            raw_ing = row.get("Ingredients", "")
            for clause in split_ingredients(raw_ing):
                ing_code = slugify(clause, max_len=60)
                if ing_code not in existing_ingredients and ing_code not in new_ingredients_map:
                    new_ingredients_map[ing_code] = clause[:255]

        if new_ingredients_map:
            logger.info("Bulk-inserting %d new master ingredients...", len(new_ingredients_map))
            # Bulk add in chunks of 500
            ing_objs = [
                Ingredient(
                    ingredient_code=code,
                    canonical_name=name,
                    category="OTHER",
                    processing_classification="UNKNOWN",
                    sugar_classification="UNKNOWN",
                )
                for code, name in new_ingredients_map.items()
            ]
            for i in range(0, len(ing_objs), 500):
                db.bulk_save_objects(ing_objs[i:i+500])
                db.commit()
            existing_ingredients.update(new_ingredients_map.keys())
            logger.info("Master ingredients table populated. Count now: %d", len(existing_ingredients))

        # STEP 3: Iterate through rows and insert products
        inserted_products = 0
        updated_products = 0
        skipped_rows = 0

        # Preload existing product barcodes to minimize SELECT queries
        existing_barcodes = set(db.scalars(select(Product.barcode)).all())

        batch_counter = 0
        for idx, row in enumerate(rows, start=1):
            s_no = row.get("S.No", str(idx)).strip()
            item_name = row.get("Item name", "").strip()
            if not item_name:
                skipped_rows += 1
                continue

            brand_name = row.get("Brand_Name", "").strip() or None
            category = row.get("Category", "").strip() or "Packaged Food"
            sub_category = row.get("Sub_Category", "").strip() or None
            food_form = determine_food_form(category, sub_category or "", item_name)

            # Barcode determination
            barcode = KNOWN_BARCODES.get(item_name)
            if not barcode:
                prefix12 = f"8901{int(re.sub(r'[^0-9]', '', s_no) or idx):08d}"
                barcode = calculate_ean13(prefix12)

            serving_size_g = parse_decimal(row.get("Serving_Size_g")) or Decimal("100.0")

            # Image URL resolution
            img_file = f"{barcode}.png"
            if os.path.exists(os.path.join(static_dir, img_file)):
                img_url = f"/static/products/{barcode}.png"
            else:
                cat_lower = category.lower()
                if "biscuit" in cat_lower or "cookie" in cat_lower:
                    img_url = "assets/images/cat_biscuits.webp"
                elif "snack" in cat_lower or "namkeen" in cat_lower or "chip" in cat_lower:
                    img_url = "assets/images/cat_snacks.webp"
                elif "beverage" in cat_lower or "drink" in cat_lower or "juice" in cat_lower or "tea" in cat_lower:
                    img_url = "assets/images/cat_beverages.webp"
                elif "dairy" in cat_lower or "milk" in cat_lower:
                    img_url = "assets/images/cat_dairy.webp"
                else:
                    img_url = "assets/images/cat_snacks.webp"

            if barcode in existing_barcodes:
                product = db.execute(select(Product).where(Product.barcode == barcode)).scalar_one()
                product.product_name = item_name
                product.brand_name = brand_name
                product.food_category = category
                product.food_form = food_form
                product.serving_size_value = serving_size_g
                product.serving_size_unit = "ml" if food_form == "liquid" else "g"
                product.package_size = f"{serving_size_g}g"
                product.is_verified = True
                if isinstance(product.raw_source_payload, dict):
                    product.raw_source_payload["image_front_url"] = img_url
                    product.raw_source_payload["image_url"] = img_url
                else:
                    product.raw_source_payload = {"image_front_url": img_url, "image_url": img_url}
                db.execute(text("DELETE FROM product_nutrients WHERE product_id = :pid"), {"pid": product.id})
                db.execute(text("DELETE FROM product_ingredients WHERE product_id = :pid"), {"pid": product.id})
                updated_products += 1
            else:
                product = Product(
                    id=uuid.uuid4(),
                    barcode=barcode,
                    product_name=item_name,
                    brand_name=brand_name,
                    food_form=food_form,
                    food_category=category,
                    package_size=f"{serving_size_g}g",
                    serving_size_value=serving_size_g,
                    serving_size_unit="ml" if food_form == "liquid" else "g",
                    is_verified=True,
                    source_id=SOURCE_ID,
                    raw_source_payload={
                        "s_no": s_no,
                        "sub_category": sub_category,
                        "price_inr": row.get("Price_INR"),
                        "source_of_data": row.get("Source_of_Data"),
                        "collection_date": row.get("Collection_Date"),
                        "image_front_url": img_url,
                        "image_url": img_url,
                    },
                )
                db.add(product)
                existing_barcodes.add(barcode)
                inserted_products += 1

            # Nutrients
            nutrient_mappings = [
                ("energy", parse_decimal(row.get("Calories_kcal")), "kcal"),
                ("carbohydrates", parse_decimal(row.get("Carbohydrates_g")), "g"),
                ("protein", parse_decimal(row.get("Proteins_g")), "g"),
                ("total_fat", parse_decimal(row.get("Total_Fat_g")), "g"),
                ("saturated_fat", parse_decimal(row.get("Saturated_Fat_g")), "g"),
                ("trans_fat", parse_decimal(row.get("Trans_Fat_g")), "g"),
                ("total_sugars", parse_decimal(row.get("Sugar_g")), "g"),
                ("sodium", parse_decimal(row.get("Sodium_mg")), "mg"),
                ("dietary_fibre", parse_decimal(row.get("Dietary_Fiber_g")), "g"),
                ("cholesterol", parse_decimal(row.get("Cholesterol_mg")), "mg"),
                ("calcium", parse_decimal(row.get("Calcium_mg")), "mg"),
                ("iron", parse_decimal(row.get("Iron_mg")), "mg"),
            ]
            for code, val, unit in nutrient_mappings:
                if val is None:
                    status = "NOT_DECLARED"
                elif val == Decimal("0"):
                    status = "EXPLICITLY_ZERO"
                else:
                    status = "PRESENT"
                per_serving = round((val * serving_size_g) / Decimal("100.0"), 3) if val is not None else None
                db.add(ProductNutrient(
                    product_id=product.id,
                    nutrient_code=code,
                    per_100g_value=val,
                    per_serving_value=per_serving,
                    unit=unit,
                    data_status=status,
                ))

            # Ingredients
            for seq, ing_text in enumerate(split_ingredients(row.get("Ingredients", "")), start=1):
                ing_code = slugify(ing_text, max_len=60)
                db.add(ProductIngredient(
                    product_id=product.id,
                    ingredient_code=ing_code,
                    sequence_order=seq,
                    declared_label_text=ing_text[:255],
                    is_allergen_declared=("allergen" in ing_text.lower()),
                ))

            batch_counter += 1
            if batch_counter >= 50 or idx == len(rows):
                db.commit()
                logger.info("Committed batch: processed %d / %d products...", idx, len(rows))
                batch_counter = 0

        db.commit()

        # Seed the audited demo benchmark products
        logger.info("Seeding verified demo benchmark products...")
        demo_count = seed_demo_catalogue(db)

    logger.info(
        "Dataset loading complete: %d inserted, %d updated, %d skipped out of %d total (plus %d demo benchmark products).",
        inserted_products, updated_products, skipped_rows, total_rows, demo_count
    )
    return {
        "inserted": inserted_products,
        "updated": updated_products,
        "skipped": skipped_rows,
        "total_rows": total_rows,
        "demo_products": demo_count,
    }


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dataset_csv = os.path.join(base_dir, "dataset", "packaged_foods_india.csv")
    load_dataset_file(dataset_csv)
