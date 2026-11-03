"""
YumSure Domain Deterministic Evaluation Engines and Contracts.

Located under approved architecture path: `app.domain.engines`

Pure deterministic rule evaluation engines with zero external API dependencies:
- NutritionEngine: FSSAI Schedule II % Daily Value (RDI) & mandatory nutrient checks
- ClaimsEngine: FSSAI Schedule I compound conditions & Schedule II authorized synonyms
- ICMRHFSSEngine: ICMR-NIN Table 15.1 nutrient thresholds & Table 15.2 processing-nutrient matrix
- IngredientEngine: Additive limits, mandatory statutory warnings & uncharacterized notices
"""

from app.domain.engines.contracts import (
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
    IngredientProcessingClass,
    IngredientSugarClass,
    EvaluationStatus,
    NutrientObservationInput,
    IngredientObservationInput,
    DeclaredClaimInput,
    ProductEvaluationInput,
    RuleEvaluationResult,
    EngineBatchResult,
)
from app.domain.engines.nutrition_engine import evaluate_nutrition
from app.domain.engines.claims_engine import evaluate_claims
from app.domain.engines.icmr_hfss_engine import evaluate_icmr_hfss
from app.domain.engines.ingredient_engine import evaluate_ingredients
from app.domain.engines.coordinator import (
    EvaluationRulesBundle,
    EvaluationCoordinator,
    EvaluationCoordinatorResult,
)

__all__ = [
    "FoodForm",
    "NutrientDataStatus",
    "MeasurementBasis",
    "IngredientProcessingClass",
    "IngredientSugarClass",
    "EvaluationStatus",
    "NutrientObservationInput",
    "IngredientObservationInput",
    "DeclaredClaimInput",
    "ProductEvaluationInput",
    "RuleEvaluationResult",
    "EngineBatchResult",
    "EvaluationRulesBundle",
    "EvaluationCoordinator",
    "EvaluationCoordinatorResult",
    "evaluate_nutrition",
    "evaluate_claims",
    "evaluate_icmr_hfss",
    "evaluate_ingredients",
]
