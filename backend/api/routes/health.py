"""
System Health & Readiness Endpoints.
Distinguishes core API readiness from optional ML providers and vector index status.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.db.session import get_db
from backend.core.config import settings
from backend.api.deps import get_hybrid_retriever, HybridRetriever

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    # Check Database
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check FAISS Vector Index
    faiss_ok = retriever.vector_store.is_ready()
    faiss_count = (
        retriever.vector_store.index.ntotal if retriever.vector_store.index else 0
    )

    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "components": {
            "database": {
                "status": "connected" if db_ok else "unreachable",
                "engine": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
            },
            "vector_search": {
                "status": "ready" if faiss_ok else "uninitialized",
                "indexed_records": faiss_count,
                "model": settings.EMBEDDING_MODEL_NAME,
            },
            "llm_provider": {
                "status": "active",
                "provider": settings.LLM_PROVIDER,
                "model": settings.LLM_MODEL_NAME,
            },
        },
    }
