"""
API v1 Router Aggregator.

Mounts versioned resource routes under /api/v1:
- /api/v1/products
- /api/v1/search
- /api/v1/trending
- /api/v1/history
- /api/v1/chat
"""

from fastapi import APIRouter
from app.api.v1.endpoints import products, search, history, chat

api_router = APIRouter()
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(history.router, tags=["history"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
