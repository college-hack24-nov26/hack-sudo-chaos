"""
YumSure Deterministic Engine Contracts and DTOs.

Pure Python / Pydantic V2 definitions with zero framework dependencies (no FastAPI, no SQLAlchemy ORM).
Preserves strict four-state nutrient semantics and five standardized evaluation outcomes.
"""

from enum import Enum
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FoodForm(str, Enum):
    SOLID = "solid"
    LIQUID = "liquid"


class NutrientDataStatus(str, Enum):
    """Strict four-state nutrient declaration semantics."""
    PRESENT = "PRESENT"
    EXPLICITLY_ZERO = "EXPLICITLY_ZERO"
    NOT_DECLARED = "NOT_DECLARED"
    UNKNOWN = "UNKNOWN"


class MeasurementBasis(str, Enum):
    """Allowlisted statutory and analytical measurement bases."""
    PER_100G = "PER_100G"
    PER_100ML = "PER_100ML"
    PER_100KCAL = "PER_100KCAL"
    PER_SERVING = "PER_SERVING"
    PCT_TOTAL_ENERGY = "PCT_TOTAL_ENERGY"
    PCT_TOTAL_FAT = "PCT_TOTAL_FAT"


class IngredientProcessingClass(str, Enum):
    """Scientific processing classification for ICMR Table 15.2 UPF matrix."""
    WHOLE_FOOD = "WHOLE_FOOD"
    CULINARY_PROCESSED = "CULINARY_PROCESSED"
    FUNCTIONAL_ADDITIVE = "FUNCTIONAL_ADDITIVE"
    COSMETIC_ADDITIVE = "COSMETIC_ADDITIVE"
    INDUSTRIAL_FRACTION = "INDUSTRIAL_FRACTION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNKNOWN = "UNKNOWN"


class IngredientSugarClass(str, Enum):
    """Chemical sugar classification for FSSAI claims & ICMR HFSS evaluation."""
    NOT_SUGAR = "NOT_SUGAR"
    INTRINSIC_SUGAR = "INTRINSIC_SUGAR"
    ADDED_FREE_SUGAR = "ADDED_FREE_SUGAR"
    SUGAR_SUBSTITUTE_SWEETENER = "SUGAR_SUBSTITUTE_SWEETENER"
    NON_NUTRITIVE_SWEETENER = "NON_NUTRITIVE_SWEETENER"
    POLYOL = "POLYOL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNKNOWN = "UNKNOWN"


class EvaluationStatus(str, Enum):
    """Standardized five evaluation outcomes across all YumSure engines."""
    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INDETERMINATE = "INDETERMINATE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


# -----------------------------------------------------------------------------
# Input Observation DTOs
# -----------------------------------------------------------------------------

class NutrientObservationInput(BaseModel):
    """
    Standardized observation of a single declared nutrient.
    Missing values are NEVER converted to zero.
    """
    nutrient_code: str = Field(..., description="Canonical nutrient slug (e.g. 'protein', 'sodium')")
    per_100g_value: Optional[Decimal] = Field(None, description="Numeric value per 100g or 100ml")
    per_serving_value: Optional[Decimal] = Field(None, description="Numeric value per serving")
    unit: str = Field(..., description="Measurement unit (e.g. 'g', 'mg', 'kcal')")
    data_status: NutrientDataStatus = Field(..., description="Four-state declaration status from label")


class IngredientObservationInput(BaseModel):
    """
    Standardized observation of an ingredient from the label in descending weight order.
    """
    ingredient_code: str = Field(..., description="Canonical ingredient slug or INS number")
    declared_label_text: str = Field(..., description="Verbatim text from product ingredient list")
    sequence_order: int = Field(..., ge=1, description="1-based descending weight order")
    declared_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Quantitative QUID %")
    ins_number: Optional[str] = Field(None, description="INS additive number (e.g. '330', '951')")
    is_fssai_major_allergen: bool = Field(False, description="Flag for FSSAI major allergens")
    processing_classification: IngredientProcessingClass = Field(
        default=IngredientProcessingClass.UNKNOWN,
        description="Scientific processing classification"
    )
    sugar_classification: IngredientSugarClass = Field(
        default=IngredientSugarClass.UNKNOWN,
        description="Chemical sugar classification"
    )
    classification_evidence: Optional[str] = Field(None, description="Scientific provenance note")


class DeclaredClaimInput(BaseModel):
    """Voluntary marketing claim printed on product packaging."""
    claim_code: str = Field(..., description="Claim code (e.g. 'TRANS_FAT_FREE', 'HIGH_PROTEIN')")
    raw_label_statement: str = Field(..., description="Verbatim marketing text on pack")


class ProductEvaluationInput(BaseModel):
    """
    Unified framework-independent input DTO for all YumSure evaluation engines.
    """
    product_id: Optional[str] = Field(None, description="Product identifier or barcode")
    product_name: str = Field(..., description="Commercial product name")
    brand_name: Optional[str] = Field(None, description="Brand name")
    food_form: FoodForm = Field(..., description="Physical state: 'solid' or 'liquid'")
    food_category: Optional[str] = Field(None, description="Food category (e.g. 'BEVERAGE', 'CEREAL')")
    package_size: Optional[str] = Field(None, description="Package declaration (e.g. '200g', '1L')")
    serving_size_value: Optional[Decimal] = Field(None, description="Serving size numeric value")
    serving_size_unit: str = Field("g", description="Serving unit (e.g. 'g', 'ml')")
    
    nutrients: Dict[str, NutrientObservationInput] = Field(
        default_factory=dict,
        description="Nutrient observations keyed by canonical nutrient_code"
    )
    ingredients: List[IngredientObservationInput] = Field(
        default_factory=list,
        description="Ordered ingredient observations"
    )
    declared_claims: List[DeclaredClaimInput] = Field(
        default_factory=list,
        description="Marketing claims on package requiring verification"
    )
    data_source_id: Optional[str] = Field(None, description="Provenance ID")


# -----------------------------------------------------------------------------
# Output Result DTOs
# -----------------------------------------------------------------------------

class RuleEvaluationResult(BaseModel):
    """
    Standard atomic evaluation result emitted for a single rule by any engine.
    """
    engine_name: str = Field(..., description="'NUTRITION', 'CLAIMS', 'ICMR_HFSS', or 'INGREDIENT'")
    rule_id: str = Field(..., description="Unique persistent identifier of the rule")
    rule_code: str = Field(..., description="Human-readable rule code")
    outcome: EvaluationStatus = Field(..., description="Standardized five-state evaluation outcome")
    title: str = Field(..., description="Plain-language descriptive title")
    human_readable_explanation: str = Field(..., description="Factual, neutral, evidence-grounded consumer explanation")
    evidence_used: Dict[str, Any] = Field(default_factory=dict, description="Observed values and thresholds evaluated")
    missing_evidence: List[str] = Field(default_factory=list, description="Missing fields causing INSUFFICIENT_DATA")
    statutory_citation: str = Field(..., description="Exact legal or institutional citation")
    official_source_url: str = Field(..., description="Direct link to official source")
    source_version: str = Field(..., description="Document publication or amendment version")
    warnings_or_limitations: Optional[str] = Field(None, description="Contextual warnings or scientific scope notes")


class EngineBatchResult(BaseModel):
    """
    Collection of atomic rule results from an engine run.
    Explicitly does NOT compute a composite score or product grade.
    """
    engine_name: str
    product_id: Optional[str]
    food_form: str
    results: List[RuleEvaluationResult] = Field(default_factory=list)
    summary_counts: Dict[EvaluationStatus, int] = Field(default_factory=dict)

