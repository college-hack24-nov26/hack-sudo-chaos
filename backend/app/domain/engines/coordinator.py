"""
Framework-Independent Evaluation Coordinator & Rules Bundle.

Coordinates the four deterministic intelligence engines (Nutrition, ICMR-HFSS,
FSSAI Claims, and Ingredients) in a single unified pipeline with microsecond
latency benchmarking.

Guarantees:
1. Zero framework dependencies (no FastAPI, no Starlette).
2. Zero database dependencies (no SQLAlchemy ORM, no database connections).
3. Pure, offline-capable, deterministic rule execution.
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.domain.engines.contracts import (
    ProductEvaluationInput,
    EngineBatchResult,
)
from app.domain.engines.nutrition_engine import evaluate_nutrition
from app.domain.engines.icmr_hfss_engine import evaluate_icmr_hfss
from app.domain.engines.claims_engine import evaluate_claims
from app.domain.engines.ingredient_engine import evaluate_ingredients

logger = logging.getLogger(__name__)


class EvaluationRulesBundle(BaseModel):
    """
    Typed container holding the complete set of verified regulatory rules
    required by all four deterministic engines.
    """
    icmr_threshold_rules: List[Dict[str, Any]] = Field(default_factory=list)
    icmr_matrix_rules: List[Dict[str, Any]] = Field(default_factory=list)
    claims_rules: List[Dict[str, Any]] = Field(default_factory=list)
    synonym_registry: Dict[str, List[str]] = Field(default_factory=dict)
    ingredient_rules: List[Dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def from_seeds(cls, seeds_dir: Optional[str] = None) -> "EvaluationRulesBundle":
        """
        Factory method loading verified rule datasets from JSON seed files.
        """
        if seeds_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            seeds_dir = os.path.join(base_dir, "data", "seeds")

        def _load(filename: str) -> Any:
            path = os.path.join(seeds_dir, filename)
            if not os.path.exists(path):
                logger.warning("Seed dataset file not found: %s", path)
                return {} if filename.endswith("synonyms_seed.json") else []
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        return cls(
            icmr_threshold_rules=_load("icmr_table_15_1_seed.json"),
            icmr_matrix_rules=_load("icmr_table_15_2_seed.json"),
            claims_rules=_load("fssai_schedule_i_claims_seed.json"),
            synonym_registry=_load("fssai_schedule_ii_synonyms_seed.json"),
            ingredient_rules=_load("ingredient_rules_seed.json"),
        )


class EvaluationCoordinatorResult(BaseModel):
    """
    Unified result produced by EvaluationCoordinator executing all four engines.
    """
    product_id: Optional[str] = None
    nutrition_evaluation: EngineBatchResult
    icmr_hfss_evaluation: EngineBatchResult
    claims_evaluation: EngineBatchResult
    ingredient_evaluation: EngineBatchResult
    latencies_ms: Dict[str, float] = Field(default_factory=dict)


class EvaluationCoordinator:
    """
    Framework-independent domain coordinator that dispatches a ProductEvaluationInput
    to the four deterministic engines and aggregates their atomic batch results.
    """

    _default_instance: Optional["EvaluationCoordinator"] = None

    def __init__(self, rules_bundle: Optional[EvaluationRulesBundle] = None) -> None:
        """
        Initializes coordinator with preloaded rules bundle.
        """
        self.rules = rules_bundle or EvaluationRulesBundle.from_seeds()

    def evaluate(self, product: ProductEvaluationInput) -> EvaluationCoordinatorResult:
        """
        Executes all four deterministic engines sequentially against the product DTO.
        Captures microsecond-precision latencies for each engine.
        """
        # 1. Nutrition Engine
        t0 = time.perf_counter()
        nutrition_res = evaluate_nutrition(product)
        t_nut = (time.perf_counter() - t0) * 1000.0

        # 2. ICMR HFSS Engine
        t0 = time.perf_counter()
        icmr_res = evaluate_icmr_hfss(
            product,
            threshold_rules=self.rules.icmr_threshold_rules,
            matrix_rules=self.rules.icmr_matrix_rules,
        )
        t_icmr = (time.perf_counter() - t0) * 1000.0

        # 3. Claims Engine
        t0 = time.perf_counter()
        claims_res = evaluate_claims(
            product,
            rules=self.rules.claims_rules,
            synonym_registry=self.rules.synonym_registry,
        )
        t_claims = (time.perf_counter() - t0) * 1000.0

        # 4. Ingredient Engine
        t0 = time.perf_counter()
        ingredient_res = evaluate_ingredients(
            product,
            ingredient_rules=self.rules.ingredient_rules,
        )
        t_ing = (time.perf_counter() - t0) * 1000.0

        latencies = {
            "nutrition_ms": round(t_nut, 3),
            "icmr_ms": round(t_icmr, 3),
            "claims_ms": round(t_claims, 3),
            "ingredient_ms": round(t_ing, 3),
            "engines_total_ms": round(t_nut + t_icmr + t_claims + t_ing, 3),
        }

        return EvaluationCoordinatorResult(
            product_id=product.product_id,
            nutrition_evaluation=nutrition_res,
            icmr_hfss_evaluation=icmr_res,
            claims_evaluation=claims_res,
            ingredient_evaluation=ingredient_res,
            latencies_ms=latencies,
        )

    @classmethod
    def get_default(cls) -> "EvaluationCoordinator":
        """Singleton accessor for default EvaluationCoordinator."""
        if cls._default_instance is None:
            cls._default_instance = cls()
        return cls._default_instance

