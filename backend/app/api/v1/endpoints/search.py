"""
Search & Discovery API Endpoints.

Provides product keyword search and trending food products carousel
for the YumSure Flutter search interface.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.product import Product

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


# Curated catalog of standard Indian packaged products for instant demo availability
CURATED_DISCOVERY_CATALOG = [
    {
        "barcode": "8901030383701",
        "product_name": "Nutri-Choice Digestive Biscuits",
        "brand_name": "Britannia",
        "category": "Biscuits",
        "sub_category": "High Fibre Biscuits",
        "image_url": "https://images.openfoodfacts.org/images/products/890/103/038/3701/front_en.11.400.jpg",
        "badges": [
            {"label": "High Fibre", "severity": "GOOD"},
            {"label": "Moderate Sugar", "severity": "MODERATE"},
        ],
    },
    {
        "barcode": "8901058852899",
        "product_name": "2-Minute Masala Noodles",
        "brand_name": "Maggi",
        "category": "Snacks",
        "sub_category": "Instant Noodles",
        "image_url": "https://images.openfoodfacts.org/images/products/890/105/885/2899/front_en.15.400.jpg",
        "badges": [
            {"label": "High Sodium", "severity": "HIGH"},
            {"label": "Refined Flour", "severity": "MODERATE"},
        ],
    },
    {
        "barcode": "8901262010017",
        "product_name": "Taaza Fresh Toned Milk",
        "brand_name": "Amul",
        "category": "Dairy",
        "sub_category": "Toned Milk",
        "image_url": "https://images.openfoodfacts.org/images/products/890/126/201/0017/front_en.4.400.jpg",
        "badges": [
            {"label": "Source of Protein", "severity": "GOOD"},
            {"label": "Low Added Sugar", "severity": "GOOD"},
        ],
    },
    {
        "barcode": "8901491101838",
        "product_name": "Aloo Bhujia Spicy Namkeen",
        "brand_name": "Haldiram's",
        "category": "Snacks",
        "sub_category": "Traditional Namkeen",
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/110/1838/front_en.8.400.jpg",
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
        "image_url": "https://images.openfoodfacts.org/images/products/890/103/082/5279/front_en.12.400.jpg",
        "badges": [
            {"label": "High Added Sugar", "severity": "HIGH"},
            {"label": "Zero Trans Fat", "severity": "GOOD"},
        ],
    },
]


@router.get("/search", response_model=SearchResponseSchema, summary="Search Packaged Food Products")
def search_products(
    q: str = Query(..., min_length=1, description="Search keyword query (e.g. 'biscuit', 'maggi')"),
    category: Optional[str] = Query(None, description="Optional food category filter"),
    db: Session = Depends(get_db),
) -> SearchResponseSchema:
    """
    Search products by name or brand across database and curated catalogue.
    """
    results: List[SearchResultItemSchema] = []
    clean_q = q.strip().lower()

    # 1. Search local DB first if connected
    try:
        query = db.query(Product).filter(
            Product.product_name.ilike(f"%{clean_q}%") | Product.brand_name.ilike(f"%{clean_q}%")
        )
        if category and category.lower() != "all":
            query = query.filter(Product.food_category.ilike(f"%{category}%"))

        db_products = query.limit(20).all()
        for p in db_products:
            results.append(
                SearchResultItemSchema(
                    barcode=p.barcode,
                    product_name=p.product_name,
                    brand_name=p.brand_name,
                    category=p.food_category or "Packaged Food",
                    image_url=p.raw_source_payload.get("image_front_url") if isinstance(p.raw_source_payload, dict) else None,
                    badges=[NutritionBadgeItemSchema(label="Verified Record" if p.is_verified else "Standard", severity="GOOD" if p.is_verified else "NEUTRAL")],
                )
            )
    except Exception:
        # Graceful fallback when database tables are unmigrated
        pass

    # 2. Filter from curated catalogue to guarantee rich discovery experience
    for item in CURATED_DISCOVERY_CATALOG:
        # Avoid duplicate barcode if already found in DB
        if any(r.barcode == item["barcode"] for r in results):
            continue

        match_name = clean_q in item["product_name"].lower() or clean_q in (item.get("brand_name") or "").lower()
        match_cat = True
        if category and category.lower() != "all":
            match_cat = category.lower() in item["category"].lower()

        if match_name and match_cat:
            results.append(
                SearchResultItemSchema(
                    barcode=item["barcode"],
                    product_name=item["product_name"],
                    brand_name=item["brand_name"],
                    category=item["category"],
                    sub_category=item.get("sub_category"),
                    image_url=item.get("image_url"),
                    badges=[NutritionBadgeItemSchema(**b) for b in item.get("badges", [])],
                )
            )

    return SearchResponseSchema(items=results)


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
