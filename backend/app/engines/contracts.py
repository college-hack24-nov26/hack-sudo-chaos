"""
Compatibility Shim for YumSure Evaluation Contracts.

Canonical implementation has relocated to approved directory: `app.domain.engines.contracts`
This module re-exports all contracts to ensure zero disruption and avoid divergent DTO definitions.
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
]
