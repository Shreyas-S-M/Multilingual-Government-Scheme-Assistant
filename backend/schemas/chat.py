"""
Chat & Conversational Interaction Schemas.
Supports multilingual queries, profile accumulation, follow-up questions,
and transparent eligibility outputs.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.schemas.user_profile import UserProfile
from backend.schemas.eligibility import SchemeEligibilityResult


class ChatMessageRequest(BaseModel):
    message: str = Field(description="User natural language message in English, Kannada, Telugu, Tamil, Malayalam, or code-mixed")
    conversation_id: Optional[str] = Field(default=None, description="Active conversation session ID")
    language: Optional[str] = Field(default=None, description="Preferred response language ('en', 'kn', 'te', 'ta', 'ml'), or auto-detected")
    current_profile: Optional[UserProfile] = Field(default=None, description="Current accumulated user profile")


class SourceReference(BaseModel):
    scheme_id: str
    scheme_name: str
    official_portal_url: str
    source_title: str
    last_verified_date: str


class ChatMessageResponse(BaseModel):
    reply: str = Field(description="Conversational assistant response")
    language: str = Field(description="Language used in response ('en', 'kn', 'te', 'ta', 'ml')")
    detected_language: str = Field(description="Detected language of the query")
    intent: str = Field(description="Classified user intent")
    conversation_id: str = Field(description="Session identifier")
    extracted_entities: Dict[str, Any] = Field(default_factory=dict, description="Attributes extracted from this turn")
    updated_profile: UserProfile = Field(description="Full accumulated profile after this turn")
    recommended_schemes: List[SchemeEligibilityResult] = Field(default_factory=list)
    near_miss_schemes: List[SchemeEligibilityResult] = Field(default_factory=list)
    follow_up_question: Optional[str] = Field(default=None, description="Targeted question to resolve missing UNKNOWN field")
    follow_up_target_attribute: Optional[str] = Field(default=None, description="Attribute name being resolved")
    sources: List[SourceReference] = Field(default_factory=list)
    is_llm_generated: bool = Field(default=False)
    has_conflicts: bool = Field(default=False)
    conflicting_fields: List[str] = Field(default_factory=list)
