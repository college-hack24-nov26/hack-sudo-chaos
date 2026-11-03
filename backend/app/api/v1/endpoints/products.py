"""
Products API Endpoints.

Provides barcode scan lookup, deterministic regulatory evaluation,
and Open Food Facts external fallback.
"""

import re
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_product_service
from app.services.product_service import ProductService
from app.schemas.product_analysis import ProductAnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Supports EAN-8, UPC-E (8), UPC-A (12), EAN-13 (13), ITF-14 / GTIN-14 (14)
BARCODE_REGEX = re.compile(r"^[0-9A-Za-z]{8,14}$")


@router.get(
    "/{barcode}",
    response_model=ProductAnalysisResponse,
    summary="Analyze Product by Barcode",
    description=(
        "Retrieves a packaged food product by barcode (EAN-8, UPC-A, EAN-13, etc.), "
        "checking local catalog first and falling back to Open Food Facts. "
        "Executes all four deterministic engines (Nutrition, ICMR-HFSS, FSSAI Claims, Ingredients) "
        "and returns structured, evidence-grounded evaluation results."
    ),
    responses={
        200: {"description": "Product found and multi-engine analysis successfully generated."},
        404: {"description": "Product not found in local catalog or Open Food Facts."},
        422: {"description": "Invalid barcode format."},
        500: {"description": "Internal server execution failure."},
    },
)
async def get_product_by_barcode(
    barcode: str,
    service: ProductService = Depends(get_product_service),
) -> ProductAnalysisResponse:
    """
    Executes the barcode lookup and regulatory evaluation pipeline.
    """
    clean_barcode = barcode.strip()

    # Validate barcode structure
    if not clean_barcode or not BARCODE_REGEX.match(clean_barcode):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid barcode '{clean_barcode}'. "
                "Expected standard retail barcode format (8 to 14 alphanumeric digits)."
            ),
        )

    try:
        analysis = await service.analyze_product_by_barcode_async(clean_barcode)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with barcode '{clean_barcode}' not found in local database or Open Food Facts.",
            )
        return analysis

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected failure evaluating product barcode %s: %s", clean_barcode, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred while analyzing the product.",
        )

