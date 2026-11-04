"""
Product Service Implementation.

Coordinates product retrieval via ProductRepository, external Open Food Facts fallback,
safe persistence boundaries, and invokes the framework-independent EvaluationCoordinator.

Architecture Separation:
- Tejas: ProductRepository, ProductMapper, ProductService, OpenFoodFactsClient, FastAPI.
- Abhishek: EvaluationCoordinator, EvaluationRulesBundle, Deterministic Domain Engines.
"""

import time
import logging
from typing import Optional, List, Union
import uuid

from sqlalchemy.exc import SQLAlchemyError
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.domain.mappers.product_mapper import ProductMapper
from app.domain.mappers.external_normalizer import ExternalProductNormalizer
from app.integrations.open_food_facts import OpenFoodFactsClient, OpenFoodFactsResponse
from app.domain.engines.contracts import (
    ProductEvaluationInput,
    DeclaredClaimInput,
)
from app.domain.engines.coordinator import (
    EvaluationCoordinator,
    EvaluationCoordinatorResult,
    EvaluationRulesBundle,
)
from app.schemas.product_analysis import (
    ProductSummaryResponse,
    EnginePerformanceMetrics,
    ProductAnalysisResponse,
)
from app.schemas.frontend_adapter import build_frontend_sections, AiExplanationModel
from app.integrations.nvidia_nim import nvidia_nim_client
from app.domain.curated_catalog import get_curated_product, get_curated_image_url
from app.core.cache import product_cache

logger = logging.getLogger(__name__)


class ProductService:
    """
    Application Service responsible for product retrieval, external fallback,
    safe persistence, and invoking the domain EvaluationCoordinator.
    """

    def __init__(
        self,
        product_repository: ProductRepository,
        evaluation_coordinator: Optional[EvaluationCoordinator] = None,
        off_client: Optional[OpenFoodFactsClient] = None,
        enable_cache: bool = True,
    ) -> None:
        """
        Initializes ProductService with required dependencies.
        Uses actual EvaluationCoordinator constructor and EvaluationRulesBundle.
        """
        self.repository = product_repository
        if evaluation_coordinator is not None:
            self.coordinator = evaluation_coordinator
        else:
            rules_bundle = EvaluationRulesBundle.from_seed_files()
            self.coordinator = EvaluationCoordinator(rules_bundle=rules_bundle)
        self.off_client = off_client or OpenFoodFactsClient()
        self.enable_cache = enable_cache

    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """
        Retrieves ORM Product entity with all relationships eagerly loaded (eliminating N+1).
        Gracefully handles database connectivity / unmigrated table failures.
        """
        try:
            return self.repository.get_by_barcode(barcode, load_relationships=True)
        except Exception as err:
            logger.warning(
                "Local database lookup failed for barcode %s (e.g. unmigrated DB or connection issue): %s",
                barcode,
                err,
            )
            session = getattr(self.repository, "session", None)
            if session:
                try:
                    session.rollback()
                except Exception:
                    pass
            return None

    def get_product_by_id(self, product_id: Union[uuid.UUID, str]) -> Optional[Product]:
        """
        Retrieves ORM Product entity by UUID primary key.
        Gracefully handles database connectivity / unmigrated table failures.
        """
        try:
            return self.repository.get_by_id(product_id, load_relationships=True)
        except Exception as err:
            logger.warning(
                "Local database lookup failed for product_id %s (e.g. unmigrated DB or connection issue): %s",
                product_id,
                err,
            )
            session = getattr(self.repository, "session", None)
            if session:
                try:
                    session.rollback()
                except Exception:
                    pass
            return None

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

    def _safe_persist_external_product(
        self,
        barcode: str,
        raw_product: dict,
        raw_payload: Optional[dict] = None
    ) -> bool:
        """
        Safely attempts to persist an external Open Food Facts product to the local database.
        Guarantees:
        - Never overwrites a verified product (is_verified = True).
        - Prevents duplicate barcode insertions.
        - Fails gracefully without throwing if tables do not exist (e.g. unmigrated DB).
        Returns True if persisted, False otherwise.
        """
        session = getattr(self.repository, "session", None)
        if not session:
            logger.info("No active DB session; skipping persistence for barcode %s", barcode)
            return False

        try:
            # 1. Existence / Verification Guard
            existing = self.repository.get_by_barcode(barcode, load_relationships=False)
            if existing:
                if existing.is_verified:
                    logger.info("Product %s is verified. Preserving curated data untouched.", barcode)
                return False

            # 2. Build transient ORM entity
            orm_product = ExternalProductNormalizer.to_orm_entity(
                barcode=barcode,
                raw_product=raw_product,
                raw_payload=raw_payload
            )

            # 3. Safe commit
            session.add(orm_product)
            session.commit()
            logger.info("Successfully persisted external product for barcode %s", barcode)
            return True

        except (SQLAlchemyError, Exception) as err:
            try:
                session.rollback()
            except Exception:
                pass
            logger.warning("Database persistence unavailable or skipped for barcode %s: %s", barcode, err)
            return False

    async def analyze_product_by_barcode_async(
        self,
        barcode: str,
        extra_claims: Optional[List[DeclaredClaimInput]] = None,
        include_ai_explanation: bool = True,
        use_cache: bool = True,
    ) -> Optional[ProductAnalysisResponse]:
        """
        Asynchronous product analysis with Open Food Facts fallback:
        1. Queries local DB first.
        2. On local miss: queries Open Food Facts asynchronously.
        3. Normalizes payload into ProductEvaluationInput.
        4. Safely attempts persistence if database is available.
        5. Executes EvaluationCoordinator across all 4 deterministic engines.
        6. Returns complete ProductAnalysisResponse.
        """
        # Step 0: Check In-Memory Cache for Sub-Millisecond Response
        cache_key = f"barcode:{barcode.strip()}:{include_ai_explanation}:{bool(extra_claims)}"
        if self.enable_cache and use_cache:
            cached_resp: Optional[ProductAnalysisResponse] = product_cache.get(cache_key)
            if cached_resp is not None:
                logger.info("In-memory cache HIT for barcode %s", barcode)
                cached_resp.metrics.is_cached = True
                return cached_resp

        t_total_start = time.perf_counter()

        # Step 1: Local Database Lookup
        t_db_start = time.perf_counter()
        product = self.get_product_by_barcode(barcode)
        db_ms = (time.perf_counter() - t_db_start) * 1000.0

        off_ms: Optional[float] = None
        domain_product: Optional[ProductEvaluationInput] = None
        is_persisted = False
        is_verified = False
        image_url: Optional[str] = None

        if product:
            # Local Database Hit
            t_map_start = time.perf_counter()
            domain_product = ProductMapper.map_product(product, extra_claims=extra_claims)
            map_ms = (time.perf_counter() - t_map_start) * 1000.0
            is_persisted = True
            is_verified = bool(product.is_verified)
            if product.raw_source_payload and isinstance(product.raw_source_payload, dict):
                image_url = product.raw_source_payload.get("image_front_url") or product.raw_source_payload.get("image_url")
            if not image_url:
                image_url = get_curated_image_url(barcode)
        else:
            # Local Database Miss -> Open Food Facts Fallback
            logger.info("Local DB miss for barcode %s. Invoking Open Food Facts fallback...", barcode)
            t_off_start = time.perf_counter()
            off_resp: OpenFoodFactsResponse = await self.off_client.get_product(barcode)
            off_ms = (time.perf_counter() - t_off_start) * 1000.0

            if not off_resp.is_found:
                logger.info("Open Food Facts lookup failed or product not found for barcode %s: %s", barcode, off_resp.status)
                # Fallback to local persistent dataset catalog (852 Indian items) or curated demonstration catalog
                from app.core.persistent_store import persistent_store
                catalog_item = persistent_store.get_catalog_product(barcode)
                if catalog_item:
                    logger.info("Resolved barcode %s from local Indian packaged foods catalog (SQLite).", barcode)
                    domain_product = catalog_item
                    is_verified = True
                    is_persisted = False
                    map_ms = 0.5
                    image_url = get_curated_image_url(barcode)
                else:
                    curated = get_curated_product(barcode)
                    if curated:
                        logger.info("Resolved barcode %s from curated demonstration catalog.", barcode)
                        domain_product = curated
                        is_verified = (curated.data_source_id == "verified_packaging")
                        is_persisted = False
                        map_ms = 0.0
                        image_url = get_curated_image_url(barcode)
                    else:
                        return None
            else:
                # Normalize external response into domain DTO
                t_map_start = time.perf_counter()
                domain_product = ExternalProductNormalizer.to_domain_dto(
                    barcode=barcode,
                    raw_product=off_resp.product_data,
                    raw_payload=off_resp.raw_payload
                )
                map_ms = (time.perf_counter() - t_map_start) * 1000.0

                image_url = off_resp.product_data.get("image_front_url") or off_resp.product_data.get("image_url")
                is_verified = False

                # Safe Persistence attempt
                is_persisted = self._safe_persist_external_product(
                    barcode=barcode,
                    raw_product=off_resp.product_data,
                    raw_payload=off_resp.raw_payload
                )

        # Step 2: Multi-Engine Evaluation via EvaluationCoordinator
        coord_result: EvaluationCoordinatorResult = self.coordinator.evaluate(domain_product)

        total_ms = (time.perf_counter() - t_total_start) * 1000.0

        # Step 3: Assemble Client Summary
        summary = ProductSummaryResponse(
            product_id=str(domain_product.product_id or barcode),
            barcode=barcode.strip(),
            product_name=domain_product.product_name,
            brand_name=domain_product.brand_name,
            image_url=image_url,
            food_form=domain_product.food_form.value,
            food_category=domain_product.food_category,
            package_size=domain_product.package_size,
            serving_size_value=domain_product.serving_size_value,
            serving_size_unit=domain_product.serving_size_unit or "g",
            is_verified=is_verified,
            source_id=domain_product.data_source_id or ("local_db" if is_persisted else "open_food_facts"),
            source_provenance="Curated Demonstration Packaging (Calibrated from Barcode 8901063142015)" if (domain_product.data_source_id == "curated_demo_catalog") else ("Curated and Verified Manufacturer Packaging" if is_verified else ("Verified Local Database" if is_persisted else "Open Food Facts (Crowdsourced / Unverified)")),
            nutrient_count=len(domain_product.nutrients),
            ingredient_count=len(domain_product.ingredients),
            is_persisted=is_persisted,
        )

        metrics = EnginePerformanceMetrics(
            db_lookup_ms=round(db_ms, 3),
            external_lookup_ms=round(off_ms, 3) if off_ms is not None else None,
            domain_mapping_ms=round(map_ms, 3),
            nutrition_engine_ms=coord_result.latencies_ms.get("nutrition_ms", 0.0),
            icmr_hfss_engine_ms=coord_result.latencies_ms.get("icmr_ms", 0.0),
            claims_engine_ms=coord_result.latencies_ms.get("claims_ms", 0.0),
            ingredient_engine_ms=coord_result.latencies_ms.get("ingredient_ms", 0.0),
            total_analysis_ms=round(total_ms, 3),
        )

        # Step 4: Assemble Frontend Section Models for Flutter UI
        fe_sections = build_frontend_sections(
            domain_product=domain_product,
            nutrition_eval=coord_result.nutrition_evaluation,
            icmr_eval=coord_result.icmr_hfss_evaluation,
            claims_eval=coord_result.claims_evaluation,
            ingredient_eval=coord_result.ingredient_evaluation,
            include_ai_explanation=include_ai_explanation,
        )

        # Enrich with NVIDIA NIM AI explanation if configured
        if include_ai_explanation and nvidia_nim_client.is_configured:
            try:
                prod_info = {
                    "product_name": domain_product.product_name,
                    "brand_name": domain_product.brand_name,
                    "food_form": domain_product.food_form,
                    "food_category": domain_product.food_category,
                    "nutrients": [
                        {
                            "nutrient_code": n.nutrient_code,
                            "per_100_value": float(n.per_100g_value) if n.per_100g_value is not None else None,
                            "unit": n.declared_unit,
                        }
                        for n in (domain_product.nutrients or [])
                    ],
                    "declared_allergens": fe_sections["ingredient_analysis"].declared_allergens if fe_sections.get("ingredient_analysis") else [],
                    "ingredients_summary": fe_sections["ingredient_analysis"].ingredients_summary if fe_sections.get("ingredient_analysis") else "",
                    "key_findings": [k.model_dump() for k in (fe_sections.get("key_findings") or [])],
                }
                expl_text, provider, is_fb = await nvidia_nim_client.generate_product_explanation(
                    prod_info, barcode=domain_product.barcode
                )
                fe_sections["ai_explanation"] = AiExplanationModel(
                    provider=provider,
                    is_fallback=is_fb,
                    text=expl_text,
                )
            except Exception as e:
                logger.warning("NVIDIA NIM explanation enrichment skipped: %s", e)

        analysis_res = ProductAnalysisResponse(
            product=summary,
            nutrition_evaluation=coord_result.nutrition_evaluation,
            icmr_hfss_evaluation=coord_result.icmr_hfss_evaluation,
            claims_evaluation=coord_result.claims_evaluation,
            ingredient_evaluation=coord_result.ingredient_evaluation,
            engine_failures=coord_result.engine_failures,
            summary=coord_result.summary,
            nutrients=domain_product.nutrients,
            ingredients=domain_product.ingredients,
            metrics=metrics,
            nutritional_interpretation=fe_sections["nutritional_interpretation"],
            regulatory_claims_validation=fe_sections["regulatory_claims_validation"],
            ingredient_analysis=fe_sections["ingredient_analysis"],
            key_findings=fe_sections["key_findings"],
            ai_explanation=fe_sections["ai_explanation"],
        )

        # Record scan into permanent SQLite storage (survives app restarts)
        try:
            from app.core.persistent_store import persistent_store
            kf_title = fe_sections["key_findings"][0].title if fe_sections.get("key_findings") else None
            kf_sev = fe_sections["key_findings"][0].severity if fe_sections.get("key_findings") else "MODERATE"
            persistent_store.record_scan(
                barcode=barcode.strip(),
                product_name=summary.product_name,
                brand_name=summary.brand_name,
                food_category=summary.food_category,
                image_url=summary.image_url,
                key_finding=kf_title,
                key_finding_severity=kf_sev,
            )
        except Exception as e:
            logger.debug("Failed to record scan in persistent store: %s", e)

        if self.enable_cache and use_cache:
            product_cache.set(cache_key, analysis_res)
        return analysis_res

    def analyze_product_by_barcode(
        self,
        barcode: str,
        extra_claims: Optional[List[DeclaredClaimInput]] = None,
        include_ai_explanation: bool = True,
        use_cache: bool = True,
    ) -> Optional[ProductAnalysisResponse]:
        """
        Synchronous variant of analyze_product_by_barcode.
        Uses synchronous OFF client if a local database miss occurs.
        """
        # Step 0: Check In-Memory Cache for Sub-Millisecond Response
        cache_key = f"barcode:{barcode.strip()}:{include_ai_explanation}:{bool(extra_claims)}"
        if self.enable_cache and use_cache:
            cached_resp: Optional[ProductAnalysisResponse] = product_cache.get(cache_key)
            if cached_resp is not None:
                logger.info("In-memory cache HIT for barcode %s", barcode)
                cached_resp.metrics.is_cached = True
                return cached_resp

        t_total_start = time.perf_counter()

        # Step 1: Local Database Lookup
        t_db_start = time.perf_counter()
        product = self.get_product_by_barcode(barcode)
        db_ms = (time.perf_counter() - t_db_start) * 1000.0

        off_ms: Optional[float] = None
        domain_product: Optional[ProductEvaluationInput] = None
        is_persisted = False
        is_verified = False
        image_url: Optional[str] = None

        if product:
            # Local Database Hit
            t_map_start = time.perf_counter()
            domain_product = ProductMapper.map_product(product, extra_claims=extra_claims)
            map_ms = (time.perf_counter() - t_map_start) * 1000.0
            is_persisted = True
            is_verified = bool(product.is_verified)
            if product.raw_source_payload and isinstance(product.raw_source_payload, dict):
                image_url = product.raw_source_payload.get("image_front_url") or product.raw_source_payload.get("image_url")
            if not image_url:
                image_url = get_curated_image_url(barcode)
        else:
            # Local Database Miss -> Open Food Facts Fallback (Sync)
            logger.info("Local DB miss for barcode %s. Invoking synchronous OFF fallback...", barcode)
            t_off_start = time.perf_counter()
            off_resp: OpenFoodFactsResponse = self.off_client.get_product_sync(barcode)
            off_ms = (time.perf_counter() - t_off_start) * 1000.0

            if not off_resp.is_found:
                logger.info("Open Food Facts lookup failed or product not found for barcode %s", barcode)
                # Fallback to local persistent dataset catalog (852 Indian items) or curated demonstration catalog
                from app.core.persistent_store import persistent_store
                catalog_item = persistent_store.get_catalog_product(barcode)
                if catalog_item:
                    logger.info("Resolved barcode %s from local Indian packaged foods catalog (SQLite).", barcode)
                    domain_product = catalog_item
                    is_verified = True
                    is_persisted = False
                    map_ms = 0.5
                    image_url = get_curated_image_url(barcode)
                else:
                    curated = get_curated_product(barcode)
                    if curated:
                        logger.info("Resolved barcode %s from curated demonstration catalog.", barcode)
                        domain_product = curated
                        is_verified = (curated.data_source_id == "verified_packaging")
                        is_persisted = False
                        map_ms = 0.0
                        image_url = get_curated_image_url(barcode)
                    else:
                        return None
            else:
                t_map_start = time.perf_counter()
                domain_product = ExternalProductNormalizer.to_domain_dto(
                    barcode=barcode,
                    raw_product=off_resp.product_data,
                    raw_payload=off_resp.raw_payload
                )
                map_ms = (time.perf_counter() - t_map_start) * 1000.0

                image_url = off_resp.product_data.get("image_front_url") or off_resp.product_data.get("image_url")
                is_verified = False

                # Safe Persistence attempt
                is_persisted = self._safe_persist_external_product(
                    barcode=barcode,
                    raw_product=off_resp.product_data,
                    raw_payload=off_resp.raw_payload
                )

        # Step 2: Multi-Engine Evaluation via EvaluationCoordinator
        coord_result: EvaluationCoordinatorResult = self.coordinator.evaluate(domain_product)

        total_ms = (time.perf_counter() - t_total_start) * 1000.0

        summary = ProductSummaryResponse(
            product_id=str(domain_product.product_id or barcode),
            barcode=barcode.strip(),
            product_name=domain_product.product_name,
            brand_name=domain_product.brand_name,
            image_url=image_url,
            food_form=domain_product.food_form.value,
            food_category=domain_product.food_category,
            package_size=domain_product.package_size,
            serving_size_value=domain_product.serving_size_value,
            serving_size_unit=domain_product.serving_size_unit or "g",
            is_verified=is_verified,
            source_id=domain_product.data_source_id or ("local_db" if is_persisted else "open_food_facts"),
            nutrient_count=len(domain_product.nutrients),
            ingredient_count=len(domain_product.ingredients),
            is_persisted=is_persisted,
        )

        metrics = EnginePerformanceMetrics(
            db_lookup_ms=round(db_ms, 3),
            external_lookup_ms=round(off_ms, 3) if off_ms is not None else None,
            domain_mapping_ms=round(map_ms, 3),
            nutrition_engine_ms=coord_result.latencies_ms.get("nutrition_ms", 0.0),
            icmr_hfss_engine_ms=coord_result.latencies_ms.get("icmr_ms", 0.0),
            claims_engine_ms=coord_result.latencies_ms.get("claims_ms", 0.0),
            ingredient_engine_ms=coord_result.latencies_ms.get("ingredient_ms", 0.0),
            total_analysis_ms=round(total_ms, 3),
        )

        # Step 4: Assemble Frontend Section Models for Flutter UI
        fe_sections = build_frontend_sections(
            domain_product=domain_product,
            nutrition_eval=coord_result.nutrition_evaluation,
            icmr_eval=coord_result.icmr_hfss_evaluation,
            claims_eval=coord_result.claims_evaluation,
            ingredient_eval=coord_result.ingredient_evaluation,
            include_ai_explanation=include_ai_explanation,
        )

        analysis_res = ProductAnalysisResponse(
            product=summary,
            nutrition_evaluation=coord_result.nutrition_evaluation,
            icmr_hfss_evaluation=coord_result.icmr_hfss_evaluation,
            claims_evaluation=coord_result.claims_evaluation,
            ingredient_evaluation=coord_result.ingredient_evaluation,
            engine_failures=coord_result.engine_failures,
            summary=coord_result.summary,
            nutrients=domain_product.nutrients,
            ingredients=domain_product.ingredients,
            metrics=metrics,
            nutritional_interpretation=fe_sections["nutritional_interpretation"],
            regulatory_claims_validation=fe_sections["regulatory_claims_validation"],
            ingredient_analysis=fe_sections["ingredient_analysis"],
            key_findings=fe_sections["key_findings"],
            ai_explanation=fe_sections["ai_explanation"],
        )

        # Record scan into permanent SQLite storage (survives app restarts)
        try:
            from app.core.persistent_store import persistent_store
            kf_title = fe_sections["key_findings"][0].title if fe_sections.get("key_findings") else None
            kf_sev = fe_sections["key_findings"][0].severity if fe_sections.get("key_findings") else "MODERATE"
            persistent_store.record_scan(
                barcode=barcode.strip(),
                product_name=summary.product_name,
                brand_name=summary.brand_name,
                food_category=summary.food_category,
                image_url=summary.image_url,
                key_finding=kf_title,
                key_finding_severity=kf_sev,
            )
        except Exception as e:
            logger.debug("Failed to record scan in persistent store: %s", e)

        if self.enable_cache and use_cache:
            product_cache.set(cache_key, analysis_res)
        return analysis_res
