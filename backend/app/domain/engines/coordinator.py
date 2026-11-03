"""
YumSure Evaluation Coordinator.

Framework-independent coordinator integrating the four deterministic engines:
- NutritionEngine (FSSAI Schedule II % Daily Value & mandatory nutrient checks)
- ICMRHFSSEngine (ICMR-NIN Table 15.1 thresholds & Table 15.2 processing-nutrient matrix)
- ClaimsEngine (FSSAI Schedule I compound conditions & Schedule II authorized synonyms)
- IngredientEngine (Additive limits, mandatory statutory warnings & uncharacterized notices)

Design guarantees:
1. Pure domain function with zero dependencies on FastAPI, SQLAlchemy, or database sessions.
2. Isolated engine execution: an unexpected crash in one engine does not crash other engines.
3. Strict separation of regulatory evaluation outcomes from infrastructure execution failures.
4. Aggregates objective outcome counts across successful engines with zero composite health score.
5. Completely immutable across repeated evaluations.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any, Callable, Union
import logging

from pydantic import BaseModel, Field

from app.domain.engines.contracts import (
    ProductEvaluationInput,
    EngineBatchResult,
    RuleEvaluationResult,
    EvaluationStatus,
    MeasurementBasis,
    FoodForm,
)
from app.domain.engines.nutrition_engine import evaluate_nutrition
from app.domain.engines.icmr_hfss_engine import evaluate_icmr_hfss
from app.domain.engines.claims_engine import evaluate_claims
from app.domain.engines.ingredient_engine import evaluate_ingredients

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Coordinator DTOs (Proposed for future unification into contracts.py)
# -----------------------------------------------------------------------------

class EvaluationRulesBundle(BaseModel):
    """
    Immutable bundle encapsulating all verified regulatory rule sets and catalogues
    required across all four deterministic engines.
    """
    nutrition_catalogue: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional custom daily RDI reference catalogue mapping nutrient codes to {'rdi_value': Decimal, 'unit': str, 'display_name': str}."
    )
    icmr_threshold_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="ICMR Table 15.1 nutrient thresholds of concern (8 seed records)"
    )
    icmr_matrix_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="ICMR Table 15.2 2D food classification matrix rules (9 seed records: A1-C3)"
    )
    claims_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="FSSAI Schedule I statutory claim rules with AST conditions (14 seed records)"
    )
    synonym_registry: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="FSSAI Schedule II authorized synonyms mapping (9 claim codes mapping to permitted synonym string lists)"
    )
    ingredient_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Statutory ingredient rules for warnings and additive limits (6 seed records)"
    )
    ingredient_catalogue: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Canonical ingredient catalogue lookup dictionary"
    )


class EngineFailureRecord(BaseModel):
    """
    Record of an engine execution failure.
    CRITICAL: Preserved separately from regulatory evaluation outcomes.
    Never converted into PASS, FAIL, INDETERMINATE, or INSUFFICIENT_DATA.
    """
    engine_name: str = Field(..., description="Name of the failed engine ('NUTRITION', 'ICMR_HFSS', 'CLAIMS', 'INGREDIENT')")
    error_type: str = Field(..., description="Exception category or class name (e.g. 'ValueError', 'RuntimeError')")
    message: str = Field(..., description="Sanitized, neutral description of the failure (no sensitive paths or stack traces)")


class CoordinatorSummaryCounts(BaseModel):
    """
    Objective aggregated rule outcome counts across all successfully executed engines.
    STRICT PROHIBITION: Never calculates or implies an overall score, letter grade, or star rating.
    """
    total_rules_evaluated: int = Field(0, description="Total atomic rules evaluated across all successfully executed engines")
    by_outcome: Dict[EvaluationStatus, int] = Field(
        default_factory=dict,
        description="Outcome counts broken down strictly by EvaluationStatus enum keys"
    )


class CoordinatorEvaluationResult(BaseModel):
    """
    Unified product evaluation result aggregating all four engine batch results.
    Preserves engine isolation, execution telemetry, and outcome counts.
    """
    product_id: Optional[str] = Field(None, description="Product identifier / UUID string")
    product_name: str = Field(..., description="Commercial product name")
    brand_name: Optional[str] = Field(None, description="Commercial brand name")
    food_form: FoodForm = Field(..., description="Physical state: 'solid' or 'liquid'")
    food_category: Optional[str] = Field(None, description="Food category (e.g. 'BEVERAGE', 'CEREAL')")
    package_size: Optional[str] = Field(None, description="Package declaration")
    serving_size_value: Optional[Decimal] = Field(None, description="Serving size value")
    serving_size_unit: str = Field("g", description="Serving size unit")
    data_source_id: Optional[str] = Field(None, description="Provenance source ID")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of evaluation execution"
    )

    # 1. Individual Engine Batch Results (None if engine execution failed)
    nutrition_evaluation: Optional[EngineBatchResult] = Field(
        None,
        description="Complete result from nutrition_engine.evaluate_nutrition"
    )
    icmr_hfss_evaluation: Optional[EngineBatchResult] = Field(
        None,
        description="Complete result from icmr_hfss_engine.evaluate_icmr_hfss"
    )
    claims_evaluation: Optional[EngineBatchResult] = Field(
        None,
        description="Complete result from claims_engine.evaluate_claims"
    )
    ingredient_evaluation: Optional[EngineBatchResult] = Field(
        None,
        description="Complete result from ingredient_engine.evaluate_ingredients"
    )

    # 2. Execution Telemetry
    engine_failures: List[EngineFailureRecord] = Field(
        default_factory=list,
        description="Isolated execution failures encountered during engine evaluation"
    )

    # 3. Objective Outcome Counts
    summary: CoordinatorSummaryCounts = Field(
        default_factory=CoordinatorSummaryCounts,
        description="Aggregated rule outcome counts across all engines (strictly no composite score)"
    )


# -----------------------------------------------------------------------------
# Evaluation Coordinator Implementation
# -----------------------------------------------------------------------------

class EvaluationCoordinator:
    """
    Framework-independent coordinator integrating all four YumSure deterministic engines.

    Usage:
        coordinator = EvaluationCoordinator(rules_bundle)
        result = coordinator.evaluate(product)
    """

    def __init__(
        self,
        rules_bundle: Optional[Union[EvaluationRulesBundle, Dict[str, Any]]] = None,
        nutrition_runner: Optional[Callable] = None,
        icmr_hfss_runner: Optional[Callable] = None,
        claims_runner: Optional[Callable] = None,
        ingredient_runner: Optional[Callable] = None,
    ):
        """
        Initialize coordinator with regulatory rules bundle and optional injected runners.
        """
        if rules_bundle is None:
            self.rules_bundle = EvaluationRulesBundle()
        elif isinstance(rules_bundle, dict):
            self.rules_bundle = EvaluationRulesBundle(**rules_bundle)
        elif isinstance(rules_bundle, EvaluationRulesBundle):
            self.rules_bundle = rules_bundle
        else:
            raise TypeError(
                f"rules_bundle must be an EvaluationRulesBundle or dict, got {type(rules_bundle).__name__}"
            )

        # Allow dependency injection for isolated unit testing of failure modes
        self._nutrition_runner = nutrition_runner or evaluate_nutrition
        self._icmr_hfss_runner = icmr_hfss_runner or evaluate_icmr_hfss
        self._claims_runner = claims_runner or evaluate_claims
        self._ingredient_runner = ingredient_runner or evaluate_ingredients

    def evaluate(self, product: ProductEvaluationInput) -> CoordinatorEvaluationResult:
        """
        Evaluate a single product across all four deterministic engines.

        Guarantees:
        - Validates product input type and measurement bases.
        - Executes all four engines with appropriate rule sub-bundles.
        - Preserves successful engine results if another engine fails.
        - Records execution failures without polluting regulatory evaluation statuses.
        - Does NOT mutate product or rules_bundle.
        - Computes exact summary counts from actual atomic rule outcomes.
        - STRICTLY NEVER computes a composite health score.
        """
        # 1. Product input validation
        if product is None:
            raise ValueError("product cannot be None")
        if not isinstance(product, ProductEvaluationInput):
            raise TypeError(
                f"product must be an instance of ProductEvaluationInput, got {type(product).__name__}"
            )

        # Validate measurement basis integrity on declared nutrients
        for nutrient_code, obs in product.nutrients.items():
            basis = getattr(obs, "measurement_basis", None)
            if basis is not None:
                if isinstance(basis, str):
                    try:
                        MeasurementBasis(basis)
                    except ValueError:
                        raise ValueError(
                            f"Invalid measurement basis '{basis}' for nutrient '{nutrient_code}'."
                        )
                elif not isinstance(basis, MeasurementBasis):
                    raise ValueError(
                        f"Invalid measurement basis '{basis}' for nutrient '{nutrient_code}'."
                    )

        engine_failures: List[EngineFailureRecord] = []
        nutrition_res: Optional[EngineBatchResult] = None
        icmr_res: Optional[EngineBatchResult] = None
        claims_res: Optional[EngineBatchResult] = None
        ingredient_res: Optional[EngineBatchResult] = None

        # 2. Nutrition Engine Execution
        try:
            nutrition_res = self._nutrition_runner(
                product,
                custom_reference_catalogue=self.rules_bundle.nutrition_catalogue
            )
        except Exception as e:
            logger.error("Nutrition engine execution failed: %s", str(e), exc_info=True)
            engine_failures.append(
                EngineFailureRecord(
                    engine_name="NUTRITION",
                    error_type=type(e).__name__,
                    message=f"Engine execution error in NUTRITION: {type(e).__name__}"
                )
            )

        # 3. ICMR-NIN HFSS Engine Execution
        try:
            icmr_res = self._icmr_hfss_runner(
                product,
                threshold_rules=self.rules_bundle.icmr_threshold_rules,
                matrix_rules=self.rules_bundle.icmr_matrix_rules
            )
        except Exception as e:
            logger.error("ICMR HFSS engine execution failed: %s", str(e), exc_info=True)
            engine_failures.append(
                EngineFailureRecord(
                    engine_name="ICMR_HFSS",
                    error_type=type(e).__name__,
                    message=f"Engine execution error in ICMR_HFSS: {type(e).__name__}"
                )
            )

        # 4. FSSAI Claims Engine Execution
        try:
            claims_res = self._claims_runner(
                product,
                rules=self.rules_bundle.claims_rules,
                synonym_registry=self.rules_bundle.synonym_registry
            )
        except Exception as e:
            logger.error("Claims engine execution failed: %s", str(e), exc_info=True)
            engine_failures.append(
                EngineFailureRecord(
                    engine_name="CLAIMS",
                    error_type=type(e).__name__,
                    message=f"Engine execution error in CLAIMS: {type(e).__name__}"
                )
            )

        # 5. Ingredient & Allergen Engine Execution
        try:
            ingredient_res = self._ingredient_runner(
                product,
                ingredient_rules=self.rules_bundle.ingredient_rules,
                ingredient_catalogue=self.rules_bundle.ingredient_catalogue
            )
        except Exception as e:
            logger.error("Ingredient engine execution failed: %s", str(e), exc_info=True)
            engine_failures.append(
                EngineFailureRecord(
                    engine_name="INGREDIENT",
                    error_type=type(e).__name__,
                    message=f"Engine execution error in INGREDIENT: {type(e).__name__}"
                )
            )

        # 6. Aggregate Outcome Counts Across Successful Engines
        total_rules = 0
        by_outcome: Dict[EvaluationStatus, int] = {
            EvaluationStatus.PASS: 0,
            EvaluationStatus.FAIL: 0,
            EvaluationStatus.INSUFFICIENT_DATA: 0,
            EvaluationStatus.INDETERMINATE: 0,
            EvaluationStatus.NOT_APPLICABLE: 0,
        }

        for batch in (nutrition_res, icmr_res, claims_res, ingredient_res):
            if batch and batch.results:
                for rule_result in batch.results:
                    total_rules += 1
                    by_outcome[rule_result.outcome] = by_outcome.get(rule_result.outcome, 0) + 1

        summary = CoordinatorSummaryCounts(
            total_rules_evaluated=total_rules,
            by_outcome=by_outcome
        )

        return CoordinatorEvaluationResult(
            product_id=product.product_id,
            product_name=product.product_name,
            brand_name=product.brand_name,
            food_form=product.food_form,
            food_category=product.food_category,
            package_size=product.package_size,
            serving_size_value=product.serving_size_value,
            serving_size_unit=product.serving_size_unit,
            data_source_id=product.data_source_id,
            evaluated_at=datetime.now(timezone.utc),
            nutrition_evaluation=nutrition_res,
            icmr_hfss_evaluation=icmr_res,
            claims_evaluation=claims_res,
            ingredient_evaluation=ingredient_res,
            engine_failures=engine_failures,
            summary=summary
        )

