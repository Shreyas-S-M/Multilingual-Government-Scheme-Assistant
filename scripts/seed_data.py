"""
Database Seeding Script.
Loads verified schemes into the application relational database.
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.db.session import SessionLocal
from backend.db.init_db import init_db
from backend.repositories.scheme_repo import SchemeRepository
from backend.core.config import settings


def run_seed():
    init_db()
    db = SessionLocal()
    try:
        repo = SchemeRepository(db)
        seed_path = ROOT / "data" / "seed" / "verified_schemes.json"
        print(f"Seeding from: {seed_path}")
        count = repo.seed_from_file(str(seed_path))
        print(f"Successfully seeded {count} schemes.")
        stats = repo.get_stats()
        print("Database stats:", stats)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
