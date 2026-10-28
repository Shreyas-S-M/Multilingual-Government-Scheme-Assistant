"""
FastAPI Backend Application Entrypoint.
Initializes REST API server, CORS policies, routes, database tables, and retrieval index.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.logging import setup_logging, logger
from backend.db.init_db import init_db
from backend.db.session import SessionLocal
from backend.repositories.scheme_repo import SchemeRepository
from backend.api.deps import get_hybrid_retriever
from pathlib import Path

# Setup structured logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: Database initialization, initial seed, and FAISS vector index loading."""
    logger.info(f"Starting {settings.APP_NAME} (v{settings.APP_VERSION})...")
    
    # 1. Initialize DB schema
    init_db()

    # 2. Check and seed verified schemes if catalog is empty
    db = SessionLocal()
    try:
        repo = SchemeRepository(db)
        if repo.count_schemes() == 0:
            seed_file = Path(settings.SCHEMES_DATA_DIR).parent / "seed" / "verified_schemes.json"
            if seed_file.exists():
                logger.info(f"Seeding catalog from {seed_file}...")
                repo.seed_from_file(str(seed_file))

        # 3. Initialize or verify FAISS and BM25 index
        retriever = get_hybrid_retriever()
        if not retriever.vector_store.is_ready():
            logger.info("Building initial FAISS vector and BM25 indexes...")
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
            logger.info("Retrieval indexes initialized successfully.")

        # 4. Pre-warm embedding model to ensure sub-second response on first query
        try:
            logger.info("Pre-warming multilingual embedding model...")
            retriever.embedder.encode(["warmup query"])
            logger.info("Multilingual embedding model pre-warmed and ready.")
        except Exception as e:
            logger.warning(f"Embedding model pre-warming note: {e}")
    finally:
        db.close()

    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Multilingual Government Scheme Assistant with Transparent Three-State Eligibility Reasoning",
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
from backend.api.routes.health import router as health_router
from backend.api.routes.schemes import router as schemes_router
from backend.api.routes.chat import router as chat_router
from backend.api.routes.eligibility import router as eligibility_router
from backend.api.routes.admin import router as admin_router
from backend.api.routes.evaluation import router as evaluation_router

app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(schemes_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(eligibility_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)
app.include_router(evaluation_router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs_url": f"{settings.API_PREFIX}/docs",
        "health_check": f"{settings.API_PREFIX}/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
