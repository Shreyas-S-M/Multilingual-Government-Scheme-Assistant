"""
Typed User Profile Schema.
Stores structured attributes extracted from user queries or collected via follow-up questions.
Maintains field provenance, confidence, and conflict detection.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    # Core demographic attributes
    age: Optional[int] = Field(default=None, description="Age in years (e.g. 24)")
    annual_income: Optional[float] = Field(
        default=None, description="Annual family income in INR (e.g. 150000.0)"
    )
    state: Optional[str] = Field(
        default=None, description="State of residence (e.g. 'Karnataka', 'Delhi')"
    )
    residence_type: Optional[str] = Field(
        default=None, description="Rural, Urban, or Semi-Urban residence"
    )

    # Professional & Educational attributes
    occupation: Optional[str] = Field(
        default=None,
        description="Primary occupation (e.g. farmer, student, street_vendor, artisan, unemployed, salaried)",
    )
    education_level: Optional[str] = Field(
        default=None,
        description="Highest education attained or ongoing (e.g. 10th_pass, 12th_pass, undergraduate, postgraduate)",
    )
    is_student: Optional[bool] = Field(
        default=None, description="Whether currently enrolled as an active student"
    )

    # Social & Personal attributes (explicitly provided only, never guessed)
    gender: Optional[str] = Field(
        default=None, description="Self-reported gender ('female', 'male', 'transgender')"
    )
    social_category: Optional[str] = Field(
        default=None,
        description="Social category ('general', 'obc', 'sc', 'st', 'minority', 'ews')",
    )
    is_disabled: Optional[bool] = Field(
        default=None, description="Whether person has a benchmark disability"
    )
    disability_percentage: Optional[float] = Field(
        default=None, description="Percentage of disability if documented"
    )

    # Scheme-specific economic attributes
    land_ownership_ha: Optional[float] = Field(
        default=None, description="Agricultural land ownership in hectares"
    )
    has_bpl_card: Optional[bool] = Field(
        default=None, description="Whether the family holds a BPL/Antyodaya ration card"
    )
    unemployed_duration_months: Optional[int] = Field(
        default=None, description="Months of unemployment since graduation"
    )

    # Metadata & Provenance tracking
    source_spans: Dict[str, str] = Field(
        default_factory=dict, description="Query text snippet whence value was extracted"
    )
    confidences: Dict[str, float] = Field(
        default_factory=dict, description="Extraction confidence per field (0.0 to 1.0)"
    )
    field_status: Dict[str, str] = Field(
        default_factory=dict,
        description="Status per field: 'provided', 'derived', 'unknown', 'conflict'",
    )

    def get_known_attributes(self) -> Dict[str, Any]:
        """Returns non-null profile fields excluding internal metadata."""
        excluded = {"source_spans", "confidences", "field_status"}
        return {
            k: v
            for k, v in self.model_dump().items()
            if v is not None and k not in excluded
        }

    def update_field(
        self,
        field_name: str,
        value: Any,
        span: str = "",
        confidence: float = 1.0,
        status: str = "provided",
    ):
        """Updates a single field with provenance and conflict detection."""
        if hasattr(self, field_name):
            current_val = getattr(self, field_name)
            if current_val is not None and current_val != value:
                # Flag conflict if meaningful difference
                self.field_status[field_name] = "conflict"
            else:
                self.field_status[field_name] = status

            setattr(self, field_name, value)
            if span:
                self.source_spans[field_name] = span
            self.confidences[field_name] = confidence

    def merge_profile(self, new_profile: "UserProfile") -> List[str]:
        """
        Merges new profile into existing.
        Returns list of fields that had conflicting updates.
        """
        conflicts = []
        for key, val in new_profile.get_known_attributes().items():
            current_val = getattr(self, key)
            if current_val is not None and current_val != val:
                conflicts.append(key)
                self.field_status[key] = "conflict"
            else:
                setattr(self, key, val)
                self.field_status[key] = new_profile.field_status.get(key, "provided")
                if key in new_profile.source_spans:
                    self.source_spans[key] = new_profile.source_spans[key]
                if key in new_profile.confidences:
                    self.confidences[key] = new_profile.confidences[key]
        return conflicts

    def clear(self):
        """Clears all profile attributes."""
        for field in self.model_fields:
            if field in ("source_spans", "confidences", "field_status"):
                setattr(self, field, {})
            else:
                setattr(self, field, None)
