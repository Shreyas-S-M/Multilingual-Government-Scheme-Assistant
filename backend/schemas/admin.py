"""
Administrative and Auditing Schemas.
For scheme catalog management, index rebuilding, validation reports, and evaluation stats.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SchemeImportRequest(BaseModel):
    schemes: List[Dict[str, Any]]
    overwrite_existing: bool = False


class SchemeImportReport(BaseModel):
    total_received: int
    total_valid: int
    total_imported: int
    total_updated: int
    errors: List[str] = Field(default_factory=list)


class IndexRebuildResponse(BaseModel):
    success: bool
    scheme_count: int
    embedding_model: str
    faiss_index_path: str
    message: str


class SystemStatsResponse(BaseModel):
    total_schemes: int
    active_schemes: int
    central_schemes: int
    state_schemes: int
    categories_breakdown: Dict[str, int]
    total_conversations: int
    faiss_indexed_schemes: int
    embedding_model: str
    llm_provider: str


class AuditLogEntry(BaseModel):
    timestamp: str
    action: str
    entity_type: str
    entity_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
