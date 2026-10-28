"""
Application Configuration Module.
Provides centralized settings via Pydantic BaseSettings, loading from .env file.
"""
from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


# Base project directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App General
    APP_NAME: str = "Multilingual Government Scheme Assistant"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Frontend
    BACKEND_API_BASE_URL: str = "http://127.0.0.1:8000/api/v1"

    # Database
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'processed' / 'scheme_assistant.db'}"

    # Security & Auth
    SECRET_KEY: str = "multilingual-scheme-assistant-dev-secret-key-2025"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    ADMIN_API_KEY: str = "admin-secret-dev-key-change-in-production"

    # NLP & Embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    DEVICE: str = "cpu"
    SCHEMES_DATA_DIR: str = str(PROJECT_ROOT / "data" / "schemes")
    FAISS_INDEX_PATH: str = str(PROJECT_ROOT / "data" / "processed" / "faiss_index.bin")
    INDEX_METADATA_PATH: str = str(PROJECT_ROOT / "data" / "processed" / "index_metadata.json")

    # LLM & RAG Configuration
    LLM_PROVIDER: str = "deterministic"  # "deterministic", "gemini", "openai"
    LLM_MODEL_NAME: str = "gemini-1.5-flash"
    LLM_API_KEY: Optional[str] = None

    # Feature Flags
    ENABLE_HYBRID_RETRIEVAL: bool = True
    ENABLE_ADAPTIVE_QUESTIONING: bool = True
    ENABLE_NEAR_MISS_RECOMMENDATIONS: bool = True
    ENABLE_CANONICAL_LOGGING: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
