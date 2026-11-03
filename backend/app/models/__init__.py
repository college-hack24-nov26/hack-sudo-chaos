"""
YumSure ORM Models Package.

Central registry exporting all declarative entities and the SQLAlchemy DeclarativeBase.
Importing this package registers all table schemas with Base.metadata for Alembic discovery.
"""

from app.db.base import Base
from app.models.data_source import DataSource
from app.models.nutrient import Nutrient
from app.models.ingredient import Ingredient
from app.models.product import Product
from app.models.product_nutrient import ProductNutrient, NUTRIENT_DATA_STATUSES
from app.models.product_ingredient import ProductIngredient
from app.models.nutrition_rule import NutritionRule
from app.models.regulatory_claim_rule import RegulatoryClaimRule
from app.models.ingredient_rule import IngredientRule
from app.models.ai_explanation import AIExplanation
from app.models.scan_history import ScanHistory

__all__ = [
    "Base",
    "DataSource",
    "Product",
    "Nutrient",
    "ProductNutrient",
    "Ingredient",
    "ProductIngredient",
    "NutritionRule",
    "RegulatoryClaimRule",
    "IngredientRule",
    "AIExplanation",
    "ScanHistory",
    "NUTRIENT_DATA_STATUSES"
]

