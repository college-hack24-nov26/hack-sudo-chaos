"""
Chat & Consumer Q&A API Endpoints.

Provides interactive topic-controlled Q&A grounded in deterministic
packaged food evaluation factsheets via NVIDIA NIM (llama-3.1-nemoguard-8b-topic-control).
"""

import logging
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_product_service
from app.services.product_service import ProductService
from app.integrations.nvidia_nim import nvidia_nim_client, STATUTORY_DISCLAIMER

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class ProductQARequest(BaseModel):
    barcode: str = Field(..., description="Retail product barcode (EAN-8, UPC-A, EAN-13, etc.)")
    question: str = Field(..., description="User question about the product's nutrition, ingredients, or allergens")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Optional prior conversation turns for multi-turn contextual Q&A"
    )


class ProductQAResponse(BaseModel):
    barcode: str
    question: str
    answer: str
    provider: str
    model: str
    is_fallback: bool
    topic_status: str
    disclaimer: str


@router.post(
    "/product-qa",
    response_model=ProductQAResponse,
    summary="Interactive Product Q&A (Topic Controlled)",
    description=(
        "Answers consumer questions about a scanned packaged food product using "
        "NVIDIA NIM (llama-3.1-nemoguard-8b-topic-control). "
        "All answers are strictly grounded in deterministic regulatory findings (Nutrition, ICMR-HFSS, Claims, Ingredients). "
        "Off-topic and medical diagnosis queries are politely deflected with statutory disclaimers."
    ),
    responses={
        200: {"description": "Factual topic-controlled answer generated successfully."},
        404: {"description": "Product barcode not found."},
        422: {"description": "Invalid barcode or empty question."},
    },
)
async def ask_product_question(
    request: ProductQARequest,
    service: ProductService = Depends(get_product_service),
) -> ProductQAResponse:
    clean_barcode = request.barcode.strip()
    clean_question = request.question.strip()

    if not clean_question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question cannot be empty.",
        )

    # 1. Fetch analyzed product factsheet
    analysis = await service.analyze_product_by_barcode_async(clean_barcode)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with barcode '{clean_barcode}' not found.",
        )

    # Convert analysis to plain dictionary for grounding
    product_dict = analysis.model_dump()
    # Safe extraction of nutrients and findings
    safe_nutrients = []
    if analysis.nutrients:
        for n in analysis.nutrients:
            if hasattr(n, "model_dump"):
                safe_nutrients.append(n.model_dump())
            elif isinstance(n, dict):
                safe_nutrients.append(n)
            else:
                safe_nutrients.append(str(n))

    safe_findings = []
    if analysis.key_findings:
        for k in analysis.key_findings:
            if hasattr(k, "model_dump"):
                safe_findings.append(k.model_dump())
            elif isinstance(k, dict):
                safe_findings.append(k)
            else:
                safe_findings.append(str(k))

    # Flatten key product information for the LLM
    flat_data: Dict[str, Any] = {
        "product_name": analysis.product.product_name,
        "brand_name": analysis.product.brand_name,
        "food_form": analysis.product.food_form,
        "food_category": analysis.product.food_category,
        "nutrients": safe_nutrients,
        "icmr_hfss_evaluation": analysis.icmr_hfss_evaluation.model_dump() if analysis.icmr_hfss_evaluation else None,
        "claims_evaluation": analysis.claims_evaluation.model_dump() if analysis.claims_evaluation else None,
        "declared_allergens": analysis.ingredient_analysis.declared_allergens if analysis.ingredient_analysis else [],
        "ingredients_summary": analysis.ingredient_analysis.ingredients_summary if analysis.ingredient_analysis else "",
        "key_findings": safe_findings,
    }

    # Format history if present
    history_list = None
    if request.conversation_history:
        history_list = [{"role": m.role, "content": m.content} for m in request.conversation_history]

    # 2. Invoke topic-controlled client
    qa_result = await nvidia_nim_client.answer_product_question(
        product_data=flat_data,
        question=clean_question,
        conversation_history=history_list,
        barcode=clean_barcode,
    )

    return ProductQAResponse(**qa_result)
