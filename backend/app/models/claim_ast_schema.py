"""
AST Schema and Validator for FSSAI Regulatory Claim Condition Expressions.

Safety Guarantees:
- Strictly prohibits Python eval() or exec() execution.
- Validates nested AND/OR condition trees against an explicit schema.
- Enforces allowlisted operators and supported measurement bases.
- Maximum nesting depth enforced iteratively (max 5 levels) to prevent recursion exhaustion.
"""

from enum import Enum
from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, model_validator

MAX_AST_DEPTH = 5


class EvaluationStatus(str, Enum):
    """
    Standardized five-state evaluation outcomes across all YumSure intelligence engines.
    """
    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INDETERMINATE = "INDETERMINATE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ComparisonOperator(str, Enum):
    """
    Allowlisted comparison operators supported in condition expressions.
    """
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"
    EQ = "EQ"


class LogicalOperator(str, Enum):
    """
    Allowlisted boolean operators for expression tree branches.
    """
    AND = "AND"
    OR = "OR"


class MeasurementBasis(str, Enum):
    """
    Allowlisted measurement bases recognized under FSSAI statutory claims.
    """
    PER_100G = "PER_100G"
    PER_100ML = "PER_100ML"
    PER_100KCAL = "PER_100KCAL"
    PER_SERVING = "PER_SERVING"
    PCT_TOTAL_ENERGY = "PCT_TOTAL_ENERGY"
    PCT_TOTAL_FAT = "PCT_TOTAL_FAT"


class ConditionType(str, Enum):
    """
    Allowlisted condition leaf and branch node types.
    """
    NUTRIENT_THRESHOLD = "NUTRIENT_THRESHOLD"
    ENERGY_PERCENTAGE = "ENERGY_PERCENTAGE"
    INGREDIENT_CHECK = "INGREDIENT_CHECK"
    EXPRESSION_GROUP = "EXPRESSION_GROUP"


class IngredientCriteria(BaseModel):
    """
    Criteria for statutory ingredient-dependent claims (e.g. FSSAI Reg 6(1) No Added Sugar).
    """
    disallowed_sugar_classes: Optional[List[str]] = None
    disallowed_ingredient_codes: Optional[List[str]] = None
    allow_intrinsic_sugars: bool = True
    mandatory_disclosure_required: Optional[str] = None


class ClaimConditionNode(BaseModel):
    """
    Single condition node in a regulatory claim expression tree.
    """
    type: ConditionType
    nutrient_code: Optional[str] = None
    operator: Optional[ComparisonOperator] = None
    threshold_value: Optional[float] = None
    measurement_basis: Optional[MeasurementBasis] = None
    food_form: Optional[str] = None  # 'solid', 'liquid', 'both'
    formula: Optional[str] = None
    ingredient_criteria: Optional[IngredientCriteria] = None
    nested_expression: Optional["ClaimConditionGroup"] = None

    @model_validator(mode="after")
    def validate_node_completeness(self) -> "ClaimConditionNode":
        if self.type == ConditionType.NUTRIENT_THRESHOLD:
            if not self.nutrient_code:
                raise ValueError("nutrient_code is required for NUTRIENT_THRESHOLD")
            if not self.operator:
                raise ValueError("operator is required for NUTRIENT_THRESHOLD")
            if self.threshold_value is None:
                raise ValueError("threshold_value is required for NUTRIENT_THRESHOLD")
            if not self.measurement_basis:
                raise ValueError("measurement_basis is required for NUTRIENT_THRESHOLD")
        elif self.type == ConditionType.ENERGY_PERCENTAGE:
            if not self.nutrient_code:
                raise ValueError("nutrient_code is required for ENERGY_PERCENTAGE")
            if not self.operator:
                raise ValueError("operator is required for ENERGY_PERCENTAGE")
            if self.threshold_value is None:
                raise ValueError("threshold_value is required for ENERGY_PERCENTAGE")
        elif self.type == ConditionType.INGREDIENT_CHECK:
            if not self.ingredient_criteria:
                raise ValueError("ingredient_criteria is required for INGREDIENT_CHECK")
        elif self.type == ConditionType.EXPRESSION_GROUP:
            if not self.nested_expression:
                raise ValueError("nested_expression is required for EXPRESSION_GROUP")
        return self


class ClaimConditionGroup(BaseModel):
    """
    Root or nested branch node representing a boolean combination of conditions.
    """
    logical_operator: LogicalOperator = LogicalOperator.AND
    conditions: List[ClaimConditionNode] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_non_empty(self) -> "ClaimConditionGroup":
        if not self.conditions:
            raise ValueError("ClaimConditionGroup must contain at least one condition")
        return self


# Resolve forward reference
ClaimConditionNode.model_rebuild()


def check_ast_depth_iterative(raw_data: Any, max_depth: int = MAX_AST_DEPTH) -> int:
    """
    Iteratively checks the nesting depth of an expression group tree
    to prevent stack overflow / recursion exhaustion before parsing.
    Returns the maximum depth found (1-based), or raises ValueError if depth exceeds max_depth.
    """
    if not isinstance(raw_data, dict):
        return 0

    stack = [(raw_data, 1)]
    max_observed_depth = 1

    while stack:
        current_node, current_depth = stack.pop()
        if current_depth > max_depth:
            raise ValueError(
                f"AST nesting depth exceeds maximum permitted limit of {max_depth} levels "
                f"(detected depth: {current_depth})"
            )
        if current_depth > max_observed_depth:
            max_observed_depth = current_depth

        # Look for child expression groups
        conditions = current_node.get("conditions")
        if isinstance(conditions, list):
            for cond in conditions:
                if isinstance(cond, dict):
                    nested = cond.get("nested_expression")
                    if isinstance(nested, dict):
                        stack.append((nested, current_depth + 1))

    return max_observed_depth


def validate_ast_structure(
    expression: Optional[Union[Dict[str, Any], ClaimConditionGroup]],
    allow_none: bool = False
) -> Optional[ClaimConditionGroup]:
    """
    Validates an expression against the ClaimConditionGroup Pydantic schema and depth limits.
    
    If expression is None:
    - returns None if allow_none=True.
    - raises ValueError if allow_none=False.
    """
    if expression is None:
        if allow_none:
            return None
        raise ValueError("Condition expression cannot be None")

    if isinstance(expression, ClaimConditionGroup):
        # Dump to dict to verify depth
        check_ast_depth_iterative(expression.model_dump(), max_depth=MAX_AST_DEPTH)
        return expression

    if not isinstance(expression, dict):
        raise TypeError(f"Condition expression must be a dict, got {type(expression).__name__}")

    # Iterative pre-check to prevent recursion exhaustion attacks
    check_ast_depth_iterative(expression, max_depth=MAX_AST_DEPTH)

    return ClaimConditionGroup.model_validate(expression)
