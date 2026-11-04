"""
FastAPI Dependency Injection Providers.

Provides database sessions, repositories, external integration clients,
and application services.
"""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.product_repository import ProductRepository
from app.integrations.open_food_facts import OpenFoodFactsClient
from app.services.product_service import ProductService
from app.domain.engines.coordinator import EvaluationCoordinator, EvaluationRulesBundle


# Singleton instances for zero-allocation reuse
_off_client = OpenFoodFactsClient()
_rules_bundle = EvaluationRulesBundle.from_seed_files()
_coordinator = EvaluationCoordinator(rules_bundle=_rules_bundle)


def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    """Provides an active ProductRepository bound to the current request's session."""
    return ProductRepository(session=db)


def get_open_food_facts_client() -> OpenFoodFactsClient:
    """Provides the singleton Open Food Facts HTTP client."""
    return _off_client


def get_evaluation_coordinator() -> EvaluationCoordinator:
    """Provides the singleton EvaluationCoordinator with preloaded rules."""
    return _coordinator


def get_product_service(
    repo: ProductRepository = Depends(get_product_repository),
    coordinator: EvaluationCoordinator = Depends(get_evaluation_coordinator),
    off_client: OpenFoodFactsClient = Depends(get_open_food_facts_client),
) -> ProductService:
    """Provides a fully wired ProductService for request execution."""
    return ProductService(
        product_repository=repo,
        evaluation_coordinator=coordinator,
        off_client=off_client,
    )

