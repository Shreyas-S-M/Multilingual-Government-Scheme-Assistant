"""
Database Initialization & Idempotent Schema Creation.
Creates tables and seeds verified government scheme records if catalog is empty.
"""
from backend.models.database import Base
from backend.db.session import engine, SessionLocal
from backend.core.logging import logger


def init_db():
    """Initializes tables using SQLAlchemy metadata."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")


if __name__ == "__main__":
    init_db()
