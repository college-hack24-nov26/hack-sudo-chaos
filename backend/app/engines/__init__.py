"""
Compatibility Shim for YumSure Evaluation Engines.

Canonical implementation has relocated to approved directory: `app.domain.engines`
This module re-exports all contracts and engines to ensure zero disruption.
"""

from app.domain.engines import (
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
    evaluate_nutrition,
    evaluate_claims,
    evaluate_icmr_hfss,
    evaluate_ingredients,
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
    "evaluate_nutrition",
    "evaluate_claims",
    "evaluate_icmr_hfss",
    "evaluate_ingredients",
]
