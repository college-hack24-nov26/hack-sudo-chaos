"""
Product Analysis Response Schemas for Flutter and API Clients.

Standardized Pydantic v2 schemas packaging product details alongside the
four deterministic engine batch results, with complete execution metrics.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.domain.engines.contracts import EngineBatchResult


class ProductSummaryResponse(BaseModel):
    """Clean summary of core product attributes for client display."""
    product_id: str
    barcode: str
    product_name: str
    brand_name: Optional[str] = None
    image_url: Optional[str] = None
    food_form: str
    food_category: Optional[str] = None
    package_size: Optional[str] = None
    serving_size_value: Optional[Decimal] = None
    serving_size_unit: str = "g"
    is_verified: bool = False
    source_id: Optional[str] = None
    nutrient_count: int = 0
    ingredient_count: int = 0
    is_persisted: bool = True


class EnginePerformanceMetrics(BaseModel):
    """Detailed latency metrics for database lookup and deterministic engines."""
    db_lookup_ms: float = Field(..., description="Database query time in milliseconds")
    external_lookup_ms: Optional[float] = Field(None, description="External Open Food Facts query time in milliseconds")
    domain_mapping_ms: float = Field(..., description="ORM to domain mapping time in milliseconds")
    nutrition_engine_ms: float = Field(..., description="Nutrition engine evaluation time in milliseconds")
    icmr_hfss_engine_ms: float = Field(..., description="ICMR HFSS engine evaluation time in milliseconds")
    claims_engine_ms: float = Field(..., description="Claims engine evaluation time in milliseconds")
    ingredient_engine_ms: float = Field(..., description="Ingredient engine evaluation time in milliseconds")
    total_analysis_ms: float = Field(..., description="Total end-to-end execution time in milliseconds")


class ProductAnalysisResponse(BaseModel):
    """
    Complete analysis payload returned by ProductService and API endpoints.
    Fully compatible with Flutter client rendering models.
    """
    product: ProductSummaryResponse
    nutrition_evaluation: EngineBatchResult
    icmr_hfss_evaluation: EngineBatchResult
    claims_evaluation: EngineBatchResult
    ingredient_evaluation: EngineBatchResult
    metrics: EnginePerformanceMetrics
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
