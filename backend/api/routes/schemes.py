"""
Scheme Catalog API Routes.
Provides searching, filtering, pagination, and detail inspection for verified schemes.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.repositories.scheme_repo import SchemeRepository
from backend.schemas.scheme import SchemeFilterParams, SchemeResponse

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("", response_model=Dict[str, Any])
def list_schemes(
    category: Optional[str] = None,
    level: Optional[str] = None,
    state: Optional[str] = None,
    age: Optional[int] = None,
    max_income: Optional[float] = None,
    status: Optional[str] = "active",
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = SchemeRepository(db)
    params = SchemeFilterParams(
        category=category,
        level=level,
        state=state,
        age=age,
        max_income=max_income,
        status=status,
        search_query=search,
        page=page,
        page_size=page_size,
    )
    results, total = repo.filter_schemes(params)

    items = []
    for s in results:
        items.append({
            "scheme_id": s.scheme_id,
            "name": s.name,
            "name_kannada": s.name_kannada,
            "aliases": s.aliases or [],
            "level": s.level,
            "state": s.state,
            "department": s.department,
            "category": s.category,
            "subcategory": s.subcategory,
            "short_description": s.short_description,
            "benefits_summary": s.benefits_summary,
            "benefits_amount": s.benefits_amount,
            "official_portal_url": s.official_portal_url,
            "application_url": s.application_url,
            "source_title": s.source_title,
            "last_verified_date": s.last_verified_date,
            "status": s.status,
            "rules_count": len(s.rules),
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
        "items": items,
    }


@router.get("/stats/categories")
def get_categories_stats(db: Session = Depends(get_db)):
    repo = SchemeRepository(db)
    return repo.get_stats()


@router.get("/{scheme_id}")
def get_scheme_by_id(scheme_id: str, db: Session = Depends(get_db)):
    repo = SchemeRepository(db)
    scheme = repo.get_by_id(scheme_id)
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID '{scheme_id}' not found.",
        )

    return {
        "scheme_id": scheme.scheme_id,
        "name": scheme.name,
        "name_kannada": scheme.name_kannada,
        "aliases": scheme.aliases or [],
        "level": scheme.level,
        "state": scheme.state,
        "department": scheme.department,
        "category": scheme.category,
        "subcategory": scheme.subcategory,
        "short_description": scheme.short_description,
        "detailed_description": scheme.detailed_description,
        "description_kannada": scheme.description_kannada,
        "min_age": scheme.min_age,
        "max_age": scheme.max_age,
        "max_income": scheme.max_income,
        "eligible_genders": scheme.eligible_genders,
        "eligible_categories": scheme.eligible_categories,
        "target_occupations": scheme.target_occupations,
        "benefits_summary": scheme.benefits_summary,
        "benefits_amount": scheme.benefits_amount,
        "required_documents": scheme.required_documents or [],
        "application_process": scheme.application_process or [],
        "official_portal_url": scheme.official_portal_url,
        "application_url": scheme.application_url,
        "source_title": scheme.source_title,
        "source_excerpt": scheme.source_excerpt,
        "effective_date": scheme.effective_date,
        "last_verified_date": scheme.last_verified_date,
        "source_reliability": scheme.source_reliability,
        "status": scheme.status,
        "is_active": scheme.is_active,
        "rules": [
            {
                "criterion_id": r.criterion_id,
                "name": r.name,
                "field": r.field,
                "operator": r.operator,
                "expected_value": r.expected_value,
                "is_mandatory": r.is_mandatory,
                "source_citation": r.source_citation,
                "description_kannada": r.description_kannada,
                "clarification_question_en": r.clarification_question_en,
                "clarification_question_kn": r.clarification_question_kn,
            }
            for r in scheme.rules
        ],
        "sources": [
            {
                "source_url": src.source_url,
                "source_title": src.source_title,
                "last_checked_date": src.last_checked_date,
                "verification_status": src.verification_status,
                "verification_notes": src.verification_notes,
            }
            for src in scheme.sources
        ],
    }
