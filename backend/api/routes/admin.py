"""
Administrative Endpoints.
Provides authenticated endpoints for scheme catalog updates, rule management,
FAISS index rebuilding, and audit logs.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.core.security import verify_admin_key
from backend.repositories.scheme_repo import SchemeRepository
from backend.schemas.admin import (
    SystemStatsResponse,
    SchemeImportRequest,
    SchemeImportReport,
    IndexRebuildResponse,
)
from backend.schemas.scheme import SchemeCreate, SchemeUpdate
from backend.models.database import AuditLogModel
from backend.api.deps import get_hybrid_retriever, HybridRetriever
from backend.core.config import settings

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(verify_admin_key)],
)


@router.get("/stats", response_model=SystemStatsResponse)
def get_admin_system_stats(
    db: Session = Depends(get_db),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    repo = SchemeRepository(db)
    stats = repo.get_stats()
    indexed_count = (
        retriever.vector_store.index.ntotal if retriever.vector_store.index else 0
    )

    return SystemStatsResponse(
        total_schemes=stats["total_schemes"],
        active_schemes=stats["active_schemes"],
        central_schemes=stats["central_schemes"],
        state_schemes=stats["state_schemes"],
        categories_breakdown=stats["categories_breakdown"],
        total_conversations=0,
        faiss_indexed_schemes=indexed_count,
        embedding_model=settings.EMBEDDING_MODEL_NAME,
        llm_provider=settings.LLM_PROVIDER,
    )


@router.post("/schemes")
def create_scheme(
    scheme_in: SchemeCreate,
    db: Session = Depends(get_db),
):
    repo = SchemeRepository(db)
    existing = repo.get_by_id(scheme_in.scheme_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scheme with ID '{scheme_in.scheme_id}' already exists.",
        )

    data = scheme_in.model_dump()
    created = repo.upsert_scheme(data)

    # Log audit event
    audit = AuditLogModel(
        action="CREATE_SCHEME",
        entity_type="scheme",
        entity_id=scheme_in.scheme_id,
        details={"name": scheme_in.name},
    )
    db.add(audit)
    db.commit()

    return {"status": "success", "scheme_id": created.scheme_id}


@router.put("/schemes/{scheme_id}")
def update_scheme(
    scheme_id: str,
    update_in: SchemeUpdate,
    db: Session = Depends(get_db),
):
    repo = SchemeRepository(db)
    scheme = repo.get_by_id(scheme_id)
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme '{scheme_id}' not found.",
        )

    update_dict = {k: v for k, v in update_in.model_dump().items() if v is not None}
    update_dict["scheme_id"] = scheme_id
    updated = repo.upsert_scheme(update_dict)

    audit = AuditLogModel(
        action="UPDATE_SCHEME",
        entity_type="scheme",
        entity_id=scheme_id,
        details=update_dict,
    )
    db.add(audit)
    db.commit()

    return {"status": "success", "scheme_id": updated.scheme_id}


@router.post("/index/rebuild", response_model=IndexRebuildResponse)
def rebuild_vector_index(
    db: Session = Depends(get_db),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    repo = SchemeRepository(db)
    all_schemes = repo.get_all(active_only=True)
    scheme_dicts = [
        {
            "scheme_id": s.scheme_id,
            "name": s.name,
            "name_kannada": s.name_kannada,
            "aliases": s.aliases or [],
            "category": s.category,
            "subcategory": s.subcategory,
            "department": s.department,
            "short_description": s.short_description,
            "description_kannada": s.description_kannada,
            "benefits_summary": s.benefits_summary,
            "benefits_amount": s.benefits_amount,
            "target_occupations": s.target_occupations or [],
            "eligible_categories": s.eligible_categories or [],
            "required_documents": s.required_documents or [],
        }
        for s in all_schemes
    ]

    retriever.initialize_indexes(scheme_dicts)

    audit = AuditLogModel(
        action="REBUILD_INDEX",
        entity_type="vector_store",
        entity_id="faiss_index",
        details={"total_indexed": len(scheme_dicts)},
    )
    db.add(audit)
    db.commit()

    return IndexRebuildResponse(
        success=True,
        scheme_count=len(scheme_dicts),
        embedding_model=settings.EMBEDDING_MODEL_NAME,
        faiss_index_path=settings.FAISS_INDEX_PATH,
        message=f"Successfully rebuilt FAISS vector index with {len(scheme_dicts)} schemes.",
    )


@router.post("/schemes/import", response_model=SchemeImportReport)
def import_schemes(
    payload: SchemeImportRequest,
    db: Session = Depends(get_db),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    repo = SchemeRepository(db)
    valid_count = 0
    imported_count = 0
    updated_count = 0
    errors = []

    for item in payload.schemes:
        if "scheme_id" not in item or "name" not in item:
            errors.append(f"Invalid record: missing 'scheme_id' or 'name': {item.get('name', 'unknown')}")
            continue

        valid_count += 1
        existing = repo.get_by_id(item["scheme_id"])
        if existing and not payload.overwrite_existing:
            errors.append(f"Scheme '{item['scheme_id']}' already exists. Use overwrite_existing=true to update.")
            continue

        try:
            repo.upsert_scheme(item)
            if existing:
                updated_count += 1
            else:
                imported_count += 1
        except Exception as e:
            errors.append(f"Failed to upsert '{item['scheme_id']}': {str(e)}")

    # Re-index
    if imported_count > 0 or updated_count > 0:
        all_schemes = repo.get_all(active_only=True)
        retriever.initialize_indexes([
            {
                "scheme_id": s.scheme_id,
                "name": s.name,
                "name_kannada": s.name_kannada,
                "aliases": s.aliases or [],
                "category": s.category,
                "subcategory": s.subcategory,
                "department": s.department,
                "short_description": s.short_description,
                "benefits_summary": s.benefits_summary,
                "target_occupations": s.target_occupations or [],
                "eligible_categories": s.eligible_categories or [],
                "required_documents": s.required_documents or [],
            }
            for s in all_schemes
        ])

    return SchemeImportReport(
        total_received=len(payload.schemes),
        total_valid=valid_count,
        total_imported=imported_count,
        total_updated=updated_count,
        errors=errors,
    )
