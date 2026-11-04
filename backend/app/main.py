"""
YumSure FastAPI Main Application.

Entry point for the YumSure Indian Packaged Food Nutrition Intelligence backend.
Mounts versioned API endpoints, configures CORS, and establishes centralized error handling.
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.session import check_db_connectivity
from app.api.v1.router import api_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("yumsure")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "YumSure Nutrition Intelligence Engine. "
        "Provides deterministic FSSAI statutory claim verification, "
        "ICMR-NIN 2024 Table 15.1/15.2 HFSS classification, and ingredient audits."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,
    redoc_url=None,
)

# CORS Configuration for Flutter Web and Mobile Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized Error Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed", "errors": errors},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled server exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# System Probes
@app.get("/", tags=["System"])
async def root():
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "api_v1": settings.API_V1_STR,
        "docs_url": f"{settings.API_V1_STR}/docs",
        "status": "online",
    }


@app.get("/health", tags=["System"])
async def health_check():
    db_ok, db_msg = check_db_connectivity()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": {
            "connected": db_ok,
            "message": db_msg,
        },
    }


# Direct Documentation Endpoints (Accessible at both root and versioned paths)
@app.get("/docs", include_in_schema=False)
@app.get(f"{settings.API_V1_STR}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.APP_NAME} - Swagger UI",
    )


@app.get("/redoc", include_in_schema=False)
@app.get(f"{settings.API_V1_STR}/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.APP_NAME} - ReDoc",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_root_openapi():
    return JSONResponse(content=app.openapi())


# Mount Versioned API Router
import os
from fastapi.staticfiles import StaticFiles

# Dynamic Product Packet Image Resolver & Static Fallback
from fastapi import Response, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.image_service import image_service

@app.get("/static/products/{filename}", tags=["Media"])
async def serve_static_product_image(filename: str, db: Session = Depends(get_db)):
    barcode = filename.split(".")[0].strip()
    img_bytes, media_type = await image_service.resolve_and_cache_image(barcode=barcode, db=db)
    if img_bytes:
        return Response(
            content=img_bytes,
            media_type=media_type,
            headers={"Cache-Control": "public, max-age=86400"}
        )
    return Response(status_code=404)

# Mount static directory for other static assets
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

app.include_router(api_router, prefix=settings.API_V1_STR)
