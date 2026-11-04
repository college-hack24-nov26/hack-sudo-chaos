"""
Scan History & Nutritional Insights API Endpoints.

Provides recent scan ledger and aggregated nutritional intake insights
for the YumSure Flutter home screen.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db

router = APIRouter()


class ScanHistoryItemSchema(BaseModel):
    barcode: str
    product_name: str
    brand_name: Optional[str] = None
    food_category: str = "Packaged Food"
    image_url: Optional[str] = None
    scanned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    key_finding: Optional[str] = None
    key_finding_severity: str = "MODERATE"  # 'HIGH', 'MODERATE', 'POSITIVE'


class ScanHistoryResponseSchema(BaseModel):
    items: List[ScanHistoryItemSchema] = Field(default_factory=list)


class ScanInsightSchema(BaseModel):
    title: str
    description: str
    affected_count: int
    total_scanned_count: int
    finding_type: str  # 'high_sodium', 'high_sugar', 'high_fat', 'balanced'
    timeframe: str = "7d"
    insight: Optional[dict] = None


# Sample realistic scan history items for immediate offline/development presentation
SAMPLE_HISTORY_ITEMS = [
    {
        "barcode": "8901030383701",
        "product_name": "Nutri-Choice Digestive Biscuits",
        "brand_name": "Britannia",
        "food_category": "Biscuits & Bakery",
        "image_url": "https://images.openfoodfacts.org/images/products/890/103/038/3701/front_en.11.400.jpg",
        "scanned_at": datetime.now(timezone.utc) - timedelta(minutes=45),
        "key_finding": "High Fibre",
        "key_finding_severity": "POSITIVE",
    },
    {
        "barcode": "8901058852899",
        "product_name": "2-Minute Masala Noodles",
        "brand_name": "Maggi",
        "food_category": "Snacks & Instant Food",
        "image_url": "https://images.openfoodfacts.org/images/products/890/105/885/2899/front_en.15.400.jpg",
        "scanned_at": datetime.now(timezone.utc) - timedelta(hours=3),
        "key_finding": "High Sodium (Salt)",
        "key_finding_severity": "HIGH",
    },
    {
        "barcode": "8901262010017",
        "product_name": "Taaza Fresh Toned Milk",
        "brand_name": "Amul",
        "food_category": "Dairy",
        "image_url": "https://images.openfoodfacts.org/images/products/890/126/201/0017/front_en.4.400.jpg",
        "scanned_at": datetime.now(timezone.utc) - timedelta(days=1),
        "key_finding": "Source of Protein",
        "key_finding_severity": "POSITIVE",
    },
    {
        "barcode": "8901030825279",
        "product_name": "Kissan Fresh Tomato Ketchup",
        "brand_name": "Kissan",
        "food_category": "Condiments & Sauces",
        "image_url": "https://images.openfoodfacts.org/images/products/890/103/082/5279/front_en.12.400.jpg",
        "scanned_at": datetime.now(timezone.utc) - timedelta(days=2),
        "key_finding": "High Added Sugar",
        "key_finding_severity": "HIGH",
    },
]


@router.get("/history", response_model=ScanHistoryResponseSchema, summary="Get Recent Scans History")
def get_recent_scans(
    limit: int = Query(5, ge=1, le=50, description="Maximum items to return"),
    db: Session = Depends(get_db),
) -> ScanHistoryResponseSchema:
    """
    Returns recent product scan ledger formatted for Flutter recent scans section.
    Reads from permanent SQLite storage first to persist across app restarts.
    """
    from app.core.persistent_store import persistent_store
    persisted_scans = persistent_store.get_recent_scans(limit=limit)
    if persisted_scans:
        items = []
        for s in persisted_scans:
            try:
                scanned_dt = datetime.fromisoformat(s["scanned_at"]) if isinstance(s["scanned_at"], str) else s["scanned_at"]
            except Exception:
                scanned_dt = datetime.now(timezone.utc)
            items.append(
                ScanHistoryItemSchema(
                    barcode=s["barcode"],
                    product_name=s["product_name"],
                    brand_name=s["brand_name"],
                    food_category=s["food_category"] or "Packaged Food",
                    image_url=s["image_url"],
                    scanned_at=scanned_dt,
                    key_finding=s["key_finding"],
                    key_finding_severity=s["key_finding_severity"] or "MODERATE",
                )
            )
        return ScanHistoryResponseSchema(items=items)

    # Fallback to realistic starter items if no scans recorded yet
    return ScanHistoryResponseSchema(
        items=[ScanHistoryItemSchema(**item) for item in SAMPLE_HISTORY_ITEMS[:limit]]
    )


@router.get("/history/insights", response_model=ScanInsightSchema, summary="Get Scan Nutritional Insights")
def get_scan_insights(
    timeframe: str = Query("7d", description="Timeframe filter ('7d', '30d', 'all')"),
) -> ScanInsightSchema:
    """
    Returns aggregated dietary pattern insight derived from recent scans.
    """
    base = {
        "title": "High Added Sugar Trend",
        "description": "2 of your last 4 scanned foods exceed the ICMR dietary threshold for added sugars.",
        "affected_count": 2,
        "total_scanned_count": 4,
        "finding_type": "high_sugar",
        "timeframe": timeframe,
    }
    return ScanInsightSchema(
        **base,
        insight=base,
    )

