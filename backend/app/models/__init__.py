"""
YumSure ORM Models Package.

Central registry exporting all declarative entities, AST schemas, and the SQLAlchemy DeclarativeBase.
Importing this package registers all table schemas with Base.metadata for Alembic discovery.
"""

from app.db.base import Base
from app.models.data_source import DataSource
from app.models.nutrient import Nutrient
from app.models.ingredient import (
    Ingredient,
    INGREDIENT_CATEGORIES,
    INGREDIENT_PROCESSING_CLASSES,
    INGREDIENT_SUGAR_CLASSES
)
from app.models.product import Product
from app.models.product_nutrient import ProductNutrient, NUTRIENT_DATA_STATUSES
from app.models.product_ingredient import ProductIngredient
from app.models.regulatory_claim_rule import RegulatoryClaimRule
from app.models.icmr_threshold_rule import IcmrNutrientThresholdRule
from app.models.icmr_matrix_rule import (
    IcmrMatrixRule,
    ICMR_PROCESSING_GROUPS,
    ICMR_NUTRITIONAL_CATEGORIES,
    ICMR_MATRIX_CELLS
)
from app.models.ingredient_rule import IngredientRule, INGREDIENT_RULE_TYPES
from app.models.ai_explanation import AIExplanation
from app.models.scan_history import ScanHistory
from app.models.claim_ast_schema import (
    EvaluationStatus,
    ComparisonOperator,
    LogicalOperator,
    MeasurementBasis,
    ConditionType,
    ClaimConditionNode,
    ClaimConditionGroup,
    MAX_AST_DEPTH,
    validate_ast_structure
)

# Retained for backward compatibility during phased transition
from app.models.nutrition_rule import NutritionRule

__all__ = [
    "Base",
    "DataSource",
    "Product",
    "Nutrient",
    "ProductNutrient",
    "Ingredient",
    "INGREDIENT_CATEGORIES",
    "INGREDIENT_PROCESSING_CLASSES",
    "INGREDIENT_SUGAR_CLASSES",
    "ProductIngredient",
    "RegulatoryClaimRule",
    "IcmrNutrientThresholdRule",
    "IcmrMatrixRule",
    "ICMR_PROCESSING_GROUPS",
    "ICMR_NUTRITIONAL_CATEGORIES",
    "ICMR_MATRIX_CELLS",
    "IngredientRule",
    "INGREDIENT_RULE_TYPES",
    "NutritionRule",  # [DEPRECATED]
    "AIExplanation",
    "ScanHistory",
    "NUTRIENT_DATA_STATUSES",
    "EvaluationStatus",
    "ComparisonOperator",
    "LogicalOperator",
    "MeasurementBasis",
    "ConditionType",
    "ClaimConditionNode",
    "ClaimConditionGroup",
    "MAX_AST_DEPTH",
    "validate_ast_structure"
]
