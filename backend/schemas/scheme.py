"""
Structured Government Scheme Schemas.
Represents verified government schemes with structured eligibility criteria,
official source citations, and multi-language descriptions.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.schemas.eligibility import CriterionRule


class SchemeBase(BaseModel):
    scheme_id: str = Field(description="Unique scheme slug/identifier, e.g. 'pm-kisan'")
    name: str = Field(description="Official English scheme name")
    name_kannada: Optional[str] = Field(default=None, description="Official Kannada scheme name")
    aliases: List[str] = Field(default_factory=list, description="Common names, acronyms, or alternate spellings")
    level: str = Field(description="'central' or 'state'")
    state: Optional[str] = Field(default=None, description="State name for state-level schemes, e.g. 'Karnataka'")
    department: str = Field(description="Nodal ministry or department")
    category: str = Field(description="Primary category, e.g. 'Agriculture', 'Education', 'Social Welfare', 'Healthcare'")
    subcategory: Optional[str] = Field(default=None, description="Specific subcategory")
    short_description: str = Field(description="Concise 1-2 sentence overview")
    detailed_description: str = Field(description="In-depth official scheme scope")
    description_kannada: Optional[str] = Field(default=None, description="Kannada overview")
    
    # Demographic & economic boundary limits (for fast filtering)
    min_age: Optional[int] = Field(default=None, description="Minimum age requirement in years")
    max_age: Optional[int] = Field(default=None, description="Maximum age requirement in years")
    max_income: Optional[float] = Field(default=None, description="Annual family income ceiling in INR")
    eligible_genders: List[str] = Field(default_factory=lambda: ["all"], description="['all'], ['female'], etc.")
    eligible_categories: List[str] = Field(default_factory=lambda: ["all"], description="['all'], ['sc', 'st'], etc.")
    target_occupations: List[str] = Field(default_factory=lambda: ["all"], description="['farmer', 'artisan'], etc.")
    
    # Structured Rules
    rules: List[CriterionRule] = Field(default_factory=list, description="Machine-checkable eligibility predicates")
    
    # Benefits & Process
    benefits_summary: str = Field(description="Summary of financial or non-financial benefits")
    benefits_amount: Optional[str] = Field(default=None, description="Explicit monetary benefit, e.g. 'Rs. 6,000 per year'")
    required_documents: List[str] = Field(default_factory=list, description="Mandatory official documentation list")
    application_process: List[str] = Field(default_factory=list, description="Step-by-step application instructions")
    
    # Official Provenance & URLs
    official_portal_url: str = Field(description="Official government portal/information URL")
    application_url: Optional[str] = Field(default=None, description="Direct online application URL if available")
    source_title: str = Field(description="Official gazette, portal name, or guidelines document")
    source_excerpt: str = Field(description="Exact excerpt verifying eligibility and benefit conditions")
    
    # Audit & Status
    effective_date: Optional[str] = Field(default=None, description="Effective or launch date of the scheme")
    last_verified_date: str = Field(description="Date when information was officially re-verified (YYYY-MM-DD)")
    source_reliability: str = Field(default="official_portal", description="Source tier: official_portal, gazette, unverified")
    status: str = Field(default="active", description="'active', 'inactive', 'verification_required'")
    is_active: bool = Field(default=True)


class SchemeCreate(SchemeBase):
    pass


class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    name_kannada: Optional[str] = None
    aliases: Optional[List[str]] = None
    short_description: Optional[str] = None
    detailed_description: Optional[str] = None
    benefits_summary: Optional[str] = None
    benefits_amount: Optional[str] = None
    max_income: Optional[float] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    rules: Optional[List[CriterionRule]] = None
    required_documents: Optional[List[str]] = None
    application_process: Optional[List[str]] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    last_verified_date: Optional[str] = None


class SchemeResponse(SchemeBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SchemeFilterParams(BaseModel):
    category: Optional[str] = None
    level: Optional[str] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    max_income: Optional[float] = None
    age: Optional[int] = None
    status: Optional[str] = "active"
    search_query: Optional[str] = None
    page: int = 1
    page_size: int = 10
