"""
Database Engine & Session Management.
Supports PostgreSQL for production and SQLite with WAL mode & busy timeout for zero-setup concurrent dev/testing.
"""
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.core.config import settings

# Ensure sqlite parent dir exists and configure concurrency pragmas
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connect_args = {
        "check_same_thread": False,
        "timeout": 30.0,  # Wait up to 30s before failing on lock
    }
else:
    connect_args = {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def configure_sqlite_pragmas(dbapi_connection, connection_record):
    """
    Enables WAL (Write-Ahead Logging) mode, 10s busy timeout, and foreign keys
    for SQLite to eliminate file write-locking during concurrent multi-user chat sessions.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA busy_timeout=10000;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")
        finally:
            cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI Dependency providing database session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

