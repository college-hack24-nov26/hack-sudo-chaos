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
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
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


# Documentation Convenience Redirects
@app.get("/docs", include_in_schema=False)
async def redirect_docs():
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")


@app.get("/redoc", include_in_schema=False)
async def redirect_redoc():
    return RedirectResponse(url=f"{settings.API_V1_STR}/redoc")


@app.get("/openapi.json", include_in_schema=False)
async def redirect_openapi():
    return RedirectResponse(url=f"{settings.API_V1_STR}/openapi.json")


# Mount Versioned API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

