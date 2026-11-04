"""
Search & Discovery API Endpoints.

Provides product keyword search and trending food products carousel
for the YumSure Flutter search interface, backed by 850+ Indian packaged food products.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps import get_db
from app.models.product import Product
from app.models.product_nutrient import ProductNutrient
from app.domain.curated_catalog import get_curated_image_url, BARCODE_ALIASES

router = APIRouter()


class NutritionBadgeItemSchema(BaseModel):
    label: str
    severity: str  # 'HIGH', 'MODERATE', 'GOOD', 'NEUTRAL'


class SearchResultItemSchema(BaseModel):
    barcode: str
    product_name: str
    brand_name: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    image_url: Optional[str] = None
    badges: List[NutritionBadgeItemSchema] = Field(default_factory=list)


class SearchResponseSchema(BaseModel):
    items: List[SearchResultItemSchema] = Field(default_factory=list)


class TrendingProductItemSchema(BaseModel):
    barcode: str
    product_name: str
    category: str
    image_url: Optional[str] = None
    badge: Optional[NutritionBadgeItemSchema] = None


class TrendingResponseSchema(BaseModel):
    items: List[TrendingProductItemSchema] = Field(default_factory=list)


class CategoryInfoSchema(BaseModel):
    id: str
    label: str
    count: int


class CategoryListResponseSchema(BaseModel):
    items: List[CategoryInfoSchema] = Field(default_factory=list)


CATEGORY_EXPANSIONS: Dict[str, List[str]] = {
    "biscuits": ["Biscuits & Bakery", "BISCUIT", "WAFER", "Biscuit", "Cookies"],
    "biscuit": ["Biscuits & Bakery", "BISCUIT", "WAFER", "Biscuit", "Cookies"],
    "snacks": ["Snacks & Namkeen", "SNACKS", "Snack", "Namkeen", "Chips"],
    "snack": ["Snacks & Namkeen", "SNACKS", "Snack", "Namkeen", "Chips"],
    "beverages": ["Beverages & Juices", "JUICE", "Carbonated Soft Drink", "Malted Beverage Powder", "Beverage", "Drink", "Juice"],
    "beverage": ["Beverages & Juices", "JUICE", "Carbonated Soft Drink", "Malted Beverage Powder", "Beverage", "Drink", "Juice"],
    "dairy": ["Dairy & Ice Cream", "DAIRY", "Dairy Products", "ICEREAMES", "Milk", "Ice Cream"],
    "chocolates": ["Chocolates & Confectionery", "CHOCOLATE", "SWEETS", "Confectionery & Chocolate", "Chocolate", "Sweets"],
    "chocolate": ["Chocolates & Confectionery", "CHOCOLATE", "SWEETS", "Confectionery & Chocolate", "Chocolate", "Sweets"],
    "sweets": ["Chocolates & Confectionery", "SWEETS", "Sweet", "Dessert"],
    "instant food": ["Instant Food & Noodles", "INSTANT FOOD", "Instant Noodles", "Noodles"],
    "instant_food": ["Instant Food & Noodles", "INSTANT FOOD", "Instant Noodles", "Noodles"],
    "noodles": ["Instant Food & Noodles", "INSTANT FOOD", "Instant Noodles", "Noodles"],
    "cakes": ["Cakes & Bakery", "CAKE", "WAFFLE"],
    "cake": ["Cakes & Bakery", "CAKE", "WAFFLE"],
    "sauces": ["Spreads & Sauces", "SAUCE", "SPREAD", "Condiments & Sauces", "Ketchup"],
    "sauce": ["Spreads & Sauces", "SAUCE", "SPREAD", "Condiments & Sauces", "Ketchup"],
}


# Curated catalog of standard Indian packaged products with cropped local images
CURATED_DISCOVERY_CATALOG = [
    {
        "barcode": "8901063142022",
        "product_name": "Nutri-Choice Digestive Biscuits",
        "brand_name": "Britannia",
        "category": "Biscuits",
        "sub_category": "High Fibre Biscuits",
        "image_url": "/static/products/8901063142022.png",
        "badges": [
            {"label": "High Fibre", "severity": "GOOD"},
            {"label": "Moderate Sugar", "severity": "MODERATE"},
        ],
    },
    {
        "barcode": "8901058851298",
        "product_name": "2-Minute Masala Noodles",
        "brand_name": "Maggi",
        "category": "Snacks",
        "sub_category": "Instant Noodles",
        "image_url": "/static/products/8901058851298.png",
        "badges": [
            {"label": "High Sodium", "severity": "HIGH"},
            {"label": "Refined Flour", "severity": "MODERATE"},
        ],
    },
    {
        "barcode": "8901233023724",
        "product_name": "Cadbury Bournvita Chocolate Health Drink",
        "brand_name": "Cadbury",
        "category": "Beverages",
        "sub_category": "Malted Food Drink",
        "image_url": "/static/products/8901233023724.png",
        "badges": [
            {"label": "High Added Sugar", "severity": "HIGH"},
            {"label": "Fortified Vitamins", "severity": "GOOD"},
        ],
    },
    {
        "barcode": "8906010500863",
        "product_name": "Balaji Shing Bhujia - Nimbu Chatka",
        "brand_name": "Balaji Wafers",
        "category": "Snacks",
        "sub_category": "Peanuts & Namkeen",
        "image_url": "/static/products/8906010500863.png",
        "badges": [
            {"label": "High Protein", "severity": "GOOD"},
            {"label": "High Sodium", "severity": "HIGH"},
        ],
    },
    {
        "barcode": "8901764061103",
        "product_name": "Diet Coke Can",
        "brand_name": "Coca-Cola",
        "category": "Beverages",
        "sub_category": "Diet Soft Drink",
        "image_url": "/static/products/8901764061103.png",
        "badges": [
            {"label": "Zero Sugar", "severity": "GOOD"},
            {"label": "Calorie Free", "severity": "GOOD"},
        ],
    },
    {
        "barcode": "7622201756697",
        "product_name": "Cadbury Oreo Vanilla Creme Biscuits",
        "brand_name": "Oreo",
        "category": "Biscuits",
        "sub_category": "Sandwich Cookies",
        "image_url": "/static/products/7622201756697.png",
        "badges": [
            {"label": "High Sugar", "severity": "HIGH"},
            {"label": "Vegetarian", "severity": "NEUTRAL"},
        ],
    },
    {
        "barcode": "8901491101837",
        "product_name": "Lay's Classic Salted Potato Chips",
        "brand_name": "Lay's",
        "category": "Snacks",
        "sub_category": "Potato Chips",
        "image_url": "/static/products/8901491101837.png",
        "badges": [
            {"label": "High Total Fat", "severity": "HIGH"},
            {"label": "Simple Ingredients", "severity": "GOOD"},
        ],
    },
    {
        "barcode": "8904063218124",
        "product_name": "Haldiram's Aloo Bhujia",
        "brand_name": "Haldiram's",
        "category": "Snacks",
        "sub_category": "Traditional Namkeen",
        "image_url": "/static/products/8904063218124.png",
        "badges": [
            {"label": "High Total Fat", "severity": "HIGH"},
            {"label": "High Sodium", "severity": "HIGH"},
        ],
    },
    {
        "barcode": "8901030825279",
        "product_name": "Kissan Fresh Tomato Ketchup",
        "brand_name": "Kissan",
        "category": "Beverages",
        "sub_category": "Condiments & Sauces",
        "image_url": "/static/products/8901030825279.png",
        "badges": [
            {"label": "High Added Sugar", "severity": "HIGH"},
            {"label": "Zero Trans Fat", "severity": "GOOD"},
        ],
    },
    {
        "barcode": "8901262010017",
        "product_name": "Amul Taaza Fresh Toned Milk",
        "brand_name": "Amul",
        "category": "Dairy",
        "sub_category": "Toned Milk",
        "image_url": "/static/products/8901262010017.png",
        "badges": [
            {"label": "Source of Protein", "severity": "GOOD"},
            {"label": "Low Added Sugar", "severity": "GOOD"},
        ],
    },
]


def _derive_badges(p: Product) -> List[NutritionBadgeItemSchema]:
    """Derives dynamic regulatory & nutritional intelligence badges from ProductNutrient values."""
    badges = []
    nutrients = {pn.nutrient_code: pn.per_100g_value for pn in p.nutrients if pn.per_100g_value is not None}

    # Fibre
    fibre = nutrients.get("dietary_fibre")
    if fibre and fibre >= Decimal("6.0"):
        badges.append(NutritionBadgeItemSchema(label="High Fibre", severity="GOOD"))

    # Protein
    protein = nutrients.get("protein")
    if protein and protein >= Decimal("8.0"):
        badges.append(NutritionBadgeItemSchema(label="High Protein", severity="GOOD"))

    # Sodium
    sodium = nutrients.get("sodium")
    if sodium and sodium >= Decimal("800.0"):
        badges.append(NutritionBadgeItemSchema(label="High Sodium", severity="HIGH"))
    elif sodium and sodium <= Decimal("120.0"):
        badges.append(NutritionBadgeItemSchema(label="Low Sodium", severity="GOOD"))

    # Sugar
    sugar = nutrients.get("total_sugars")
    if sugar and sugar >= Decimal("22.0"):
        badges.append(NutritionBadgeItemSchema(label="High Sugar", severity="HIGH"))
    elif sugar and sugar <= Decimal("5.0"):
        badges.append(NutritionBadgeItemSchema(label="Low Sugar", severity="GOOD"))

    # Trans fat
    trans_fat = nutrients.get("trans_fat")
    if trans_fat is not None and trans_fat <= Decimal("0.2"):
        badges.append(NutritionBadgeItemSchema(label="Zero Trans Fat", severity="GOOD"))

    # Saturated fat
    sat_fat = nutrients.get("saturated_fat")
    if sat_fat and sat_fat >= Decimal("10.0"):
        badges.append(NutritionBadgeItemSchema(label="High Sat Fat", severity="HIGH"))

    if not badges:
        badges.append(NutritionBadgeItemSchema(
            label="Verified Record" if p.is_verified else "Standard Declaration",
            severity="GOOD" if p.is_verified else "NEUTRAL"
        ))

    return badges[:2]


@router.get("/search", response_model=SearchResponseSchema, summary="Search Packaged Food Products")
def search_products(
    q: str = Query("", description="Search keyword query (e.g. 'biscuit', 'maggi')"),
    category: Optional[str] = Query(None, description="Optional food category filter"),
    db: Session = Depends(get_db),
) -> SearchResponseSchema:
    """
    Search products by name or brand across database and curated catalogue.
    Supports empty keyword browsing filtered by category, and full fuzzy matching.
    """
    results: List[SearchResultItemSchema] = []
    clean_q = q.strip().lower()

    # 1. Search local DB first
    try:
        query = db.query(Product).options(
            selectinload(Product.nutrients)
        )
        if clean_q:
            query = query.filter(
                Product.product_name.ilike(f"%{clean_q}%") | 
                Product.brand_name.ilike(f"%{clean_q}%") |
                Product.barcode.ilike(f"%{clean_q}%")
            )

        if category and category.lower() != "all":
            cat_key = category.strip().lower()
            target_terms = CATEGORY_EXPANSIONS.get(cat_key, [category.strip()])
            cat_filters = [Product.food_category.ilike(f"%{t}%") for t in target_terms]
            query = query.filter(or_(*cat_filters))

        db_products = query.order_by(Product.is_verified.desc()).limit(40).all()
        for p in db_products:
            img_url = None
            if isinstance(p.raw_source_payload, dict):
                img_url = p.raw_source_payload.get("image_front_url") or p.raw_source_payload.get("image_url")
            if not img_url:
                img_url = get_curated_image_url(p.barcode)
            if not img_url:
                img_url = f"/static/products/{p.barcode}.png"

            results.append(
                SearchResultItemSchema(
                    barcode=p.barcode,
                    product_name=p.product_name,
                    brand_name=p.brand_name,
                    category=p.food_category or "Packaged Food",
                    image_url=img_url,
                    badges=_derive_badges(p),
                )
            )
    except Exception:
        pass

    # 2. Filter from curated catalogue to guarantee rich discovery experience
    for item in CURATED_DISCOVERY_CATALOG:
        if any(r.barcode == item["barcode"] for r in results):
            continue

        match_name = True
        if clean_q:
            match_name = clean_q in item["product_name"].lower() or clean_q in (item.get("brand_name") or "").lower() or clean_q == item["barcode"]

        match_cat = True
        if category and category.lower() != "all":
            cat_key = category.strip().lower()
            target_terms = CATEGORY_EXPANSIONS.get(cat_key, [category.strip()])
            match_cat = any(t.lower() in item["category"].lower() for t in target_terms)

        if match_name and match_cat:
            results.append(
                SearchResultItemSchema(
                    barcode=item["barcode"],
                    product_name=item["product_name"],
                    brand_name=item["brand_name"],
                    category=item["category"],
                    sub_category=item.get("sub_category"),
                    image_url=item.get("image_url") or f"/static/products/{item['barcode']}.png",
                    badges=[NutritionBadgeItemSchema(**b) for b in item.get("badges", [])],
                )
            )

    return SearchResponseSchema(items=results)


@router.get("/categories", response_model=CategoryListResponseSchema, summary="List Categories with Counts")
def get_categories(db: Session = Depends(get_db)) -> CategoryListResponseSchema:
    """
    Returns high-level food categories with count of available products in the database.
    """
    standard_categories = [
        {"id": "all", "label": "All", "terms": []},
        {"id": "snacks", "label": "Snacks & Namkeen", "terms": ["SNACKS", "Snacks & Namkeen", "WAFER"]},
        {"id": "biscuits", "label": "Biscuits & Bakery", "terms": ["BISCUIT", "Biscuits & Bakery", "CAKE", "WAFFLE"]},
        {"id": "beverages", "label": "Beverages & Drinks", "terms": ["JUICE", "Carbonated Soft Drink", "Malted Beverage Powder"]},
        {"id": "dairy", "label": "Dairy & Ice Cream", "terms": ["DAIRY", "Dairy Products", "ICEREAMES"]},
        {"id": "instant_food", "label": "Instant Food & Noodles", "terms": ["INSTANT FOOD", "Instant Noodles"]},
        {"id": "chocolates", "label": "Chocolates & Sweets", "terms": ["CHOCOLATE", "SWEETS", "Confectionery & Chocolate"]},
        {"id": "sauces", "label": "Sauces & Spreads", "terms": ["SAUCE", "SPREAD", "Condiments & Sauces"]},
    ]

    output = []
    try:
        total = db.query(func.count(Product.id)).scalar() or 0
        for sc in standard_categories:
            if sc["id"] == "all":
                output.append(CategoryInfoSchema(id="all", label="All", count=total))
            else:
                cat_count = db.query(func.count(Product.id)).filter(
                    or_(*(Product.food_category.ilike(f"%{t}%") for t in sc["terms"]))
                ).scalar() or 0
                output.append(CategoryInfoSchema(id=sc["id"], label=sc["label"], count=cat_count))
    except Exception:
        output = [
            CategoryInfoSchema(id="all", label="All", count=868),
            CategoryInfoSchema(id="snacks", label="Snacks & Namkeen", count=144),
            CategoryInfoSchema(id="biscuits", label="Biscuits & Bakery", count=153),
            CategoryInfoSchema(id="beverages", label="Beverages & Drinks", count=121),
            CategoryInfoSchema(id="dairy", label="Dairy & Ice Cream", count=49),
            CategoryInfoSchema(id="instant_food", label="Instant Food & Noodles", count=135),
            CategoryInfoSchema(id="chocolates", label="Chocolates & Sweets", count=227),
            CategoryInfoSchema(id="sauces", label="Sauces & Spreads", count=39),
        ]
    return CategoryListResponseSchema(items=output)


@router.get("/trending", response_model=TrendingResponseSchema, summary="Get Trending Packaged Products")
def get_trending_products() -> TrendingResponseSchema:
    """
    Returns trending discovery products with primary nutrition intelligence badge.
    """
    items: List[TrendingProductItemSchema] = []
    for item in CURATED_DISCOVERY_CATALOG:
        first_badge = item.get("badges", [None])[0]
        items.append(
            TrendingProductItemSchema(
                barcode=item["barcode"],
                product_name=item["product_name"],
                category=item["category"],
                image_url=item.get("image_url"),
                badge=NutritionBadgeItemSchema(**first_badge) if first_badge else None,
            )
        )
    return TrendingResponseSchema(items=items)
