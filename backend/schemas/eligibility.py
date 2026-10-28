"""
Three-State Eligibility Schemas.
Implements the core academic innovation: PASS, FAIL, and UNKNOWN semantics
with criterion-level provenance, missing-information tracking, and aggregation.
"""
from enum import Enum
from typing import Any, List, Optional, Union
from pydantic import BaseModel, Field


class EligibilityStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class EligibilityOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    IN_LIST = "in_list"
    INCLUSIVE_RANGE = "inclusive_range"
    BOOLEAN_IS = "boolean_is"
    STATE_MATCH = "state_match"
    CUSTOM = "custom"


class CriterionRule(BaseModel):
    """Structured rule definition stored in a Scheme."""
    criterion_id: str = Field(description="Unique rule ID, e.g. 'pm_kisan_land'")
    name: str = Field(description="Human readable rule name, e.g. 'Farmer Landholding'")
    field: str = Field(description="User profile field being evaluated, e.g. 'occupation'")
    operator: EligibilityOperator = Field(description="Evaluation predicate operator")
    expected_value: Any = Field(description="Target value, range [min, max], or allowed list")
    is_mandatory: bool = Field(default=True, description="Whether passing this condition is strictly required")
    source_citation: str = Field(description="Official portal clause or document citation")
    description_kannada: Optional[str] = Field(default=None, description="Kannada translation of rule")
    clarification_question_en: Optional[str] = Field(
        default=None, description="Targeted follow-up question in English if unknown"
    )
    clarification_question_kn: Optional[str] = Field(
        default=None, description="Targeted follow-up question in Kannada if unknown"
    )


class CriterionResult(BaseModel):
    """Result of evaluating a single criterion against a user profile."""
    criterion_id: str
    name: str
    field: str
    operator: EligibilityOperator
    expected_value: Any
    user_value: Any = None
    status: EligibilityStatus
    reason: str
    missing_field: Optional[str] = None
    is_mandatory: bool = True
    source_citation: str
    warning: Optional[str] = None


class SchemeEligibilityResult(BaseModel):
    """Aggregated eligibility evaluation for an entire scheme."""
    scheme_id: str
    scheme_name: str
    overall_status: EligibilityStatus
    mandatory_passed_count: int = 0
    mandatory_failed_count: int = 0
    mandatory_unknown_count: int = 0
    optional_passed_count: int = 0
    optional_failed_count: int = 0
    optional_unknown_count: int = 0
    criteria_results: List[CriterionResult] = Field(default_factory=list)
    summary_explanation: str
    missing_attributes: List[str] = Field(default_factory=list)
    failed_criteria: List[CriterionResult] = Field(default_factory=list)
    official_portal_url: str = ""
    benefits_summary: str = ""
    is_near_miss: bool = False
    near_miss_reason: Optional[str] = None
