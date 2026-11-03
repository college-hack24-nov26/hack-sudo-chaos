"""
Product Service Implementation.

Coordinates product retrieval via ProductRepository, transforms ORM entities
into domain DTOs via ProductMapper, and invokes the framework-independent
EvaluationCoordinator to execute the four deterministic engines.

Architecture Separation:
- Tejas: ProductRepository, ProductMapper, ProductService, FastAPI Integration.
- Abhishek: EvaluationCoordinator, EvaluationRulesBundle, Deterministic Domain Engines.
"""

import time
import logging
from typing import Optional, List, Union
import uuid

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.domain.mappers.product_mapper import ProductMapper
from app.domain.engines.contracts import (
    ProductEvaluationInput,
    DeclaredClaimInput,
)
from app.domain.engines.coordinator import (
    EvaluationCoordinator,
    EvaluationCoordinatorResult,
)
from app.schemas.product_analysis import (
    ProductSummaryResponse,
    EnginePerformanceMetrics,
    ProductAnalysisResponse,
)

logger = logging.getLogger(__name__)


class ProductService:
    """
    Application Service responsible for product retrieval, ORM-to-domain mapping,
    and invoking the domain EvaluationCoordinator for multi-engine evaluation.
    """

    def __init__(
        self,
        product_repository: ProductRepository,
        evaluation_coordinator: Optional[EvaluationCoordinator] = None,
    ) -> None:
        """
        Initializes ProductService with required repository and evaluation coordinator.
        """
        self.repository = product_repository
        self.coordinator = evaluation_coordinator or EvaluationCoordinator.get_default()

    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """
        Retrieves ORM Product entity with all relationships eagerly loaded (eliminating N+1).
        """
        return self.repository.get_by_barcode(barcode, load_relationships=True)

    def get_product_by_id(self, product_id: Union[uuid.UUID, str]) -> Optional[Product]:
        """
        Retrieves ORM Product entity by UUID primary key.
        """
        return self.repository.get_by_id(product_id, load_relationships=True)

    def get_domain_product_by_barcode(
        self,
        barcode: str,
        extra_claims: Optional[List[DeclaredClaimInput]] = None,
    ) -> Optional[ProductEvaluationInput]:
        """
        Retrieves product by barcode and maps it to framework-independent domain DTO.
        Returns None if product does not exist in local database.
        """
        product = self.get_product_by_barcode(barcode)
        if not product:
            return None
        return ProductMapper.map_product(product, extra_claims=extra_claims)

    def analyze_product_by_barcode(
        self,
        barcode: str,
        extra_claims: Optional[List[DeclaredClaimInput]] = None,
    ) -> Optional[ProductAnalysisResponse]:
        """
        Complete end-to-end barcode analysis workflow:
        1. Eagerly queries local database via ProductRepository (eliminating N+1).
        2. Converts ORM entity to ProductEvaluationInput domain DTO via ProductMapper.
        3. Dispatches DTO to framework-independent EvaluationCoordinator.
        4. Benchmarks high-resolution latencies.
        5. Packages structured ProductAnalysisResponse for Flutter client.

        Returns None if product is not found in local database.
        """
        t_total_start = time.perf_counter()

        # Step 1: Database Lookup
        t_db_start = time.perf_counter()
        product = self.get_product_by_barcode(barcode)
        db_ms = (time.perf_counter() - t_db_start) * 1000.0

        if not product:
            logger.info("Product lookup miss for barcode: %s", barcode)
            return None

        # Step 2: Domain Mapping
        t_map_start = time.perf_counter()
        domain_product = ProductMapper.map_product(product, extra_claims=extra_claims)
        map_ms = (time.perf_counter() - t_map_start) * 1000.0

        # Step 3: Multi-Engine Evaluation via EvaluationCoordinator
        coord_result: EvaluationCoordinatorResult = self.coordinator.evaluate(domain_product)

        total_ms = (time.perf_counter() - t_total_start) * 1000.0

        # Step 4: Assemble Summary
        summary = ProductSummaryResponse(
            product_id=str(product.id),
            barcode=product.barcode,
            product_name=product.product_name,
            brand_name=product.brand_name,
            food_form=product.food_form,
            food_category=product.food_category,
            package_size=product.package_size,
            serving_size_value=product.serving_size_value,
            serving_size_unit=product.serving_size_unit or "g",
            is_verified=bool(product.is_verified) if product.is_verified is not None else False,
            source_id=product.source_id,
            nutrient_count=len(product.nutrients) if product.nutrients else 0,
            ingredient_count=len(product.ingredients) if product.ingredients else 0,
        )

        metrics = EnginePerformanceMetrics(
            db_lookup_ms=round(db_ms, 3),
            domain_mapping_ms=round(map_ms, 3),
            nutrition_engine_ms=coord_result.latencies_ms.get("nutrition_ms", 0.0),
            icmr_hfss_engine_ms=coord_result.latencies_ms.get("icmr_ms", 0.0),
            claims_engine_ms=coord_result.latencies_ms.get("claims_ms", 0.0),
            ingredient_engine_ms=coord_result.latencies_ms.get("ingredient_ms", 0.0),
            total_analysis_ms=round(total_ms, 3),
        )

        return ProductAnalysisResponse(
            product=summary,
            nutrition_evaluation=coord_result.nutrition_evaluation,
            icmr_hfss_evaluation=coord_result.icmr_hfss_evaluation,
            claims_evaluation=coord_result.claims_evaluation,
            ingredient_evaluation=coord_result.ingredient_evaluation,
            metrics=metrics,
        )
