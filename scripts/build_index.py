"""
Index Rebuilding Script.
Builds the FAISS vector index and BM25 metadata from verified schemes.
"""
import sys
import os
from pathlib import Path

# Configure utf-8 console output on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import json
from backend.core.config import settings
from backend.retrieval.vector_store import VectorStore
from backend.retrieval.bm25_search import BM25Retriever


def build():
    seed_file = ROOT / "data" / "seed" / "verified_schemes.json"
    if not seed_file.exists():
        print(f"Error: {seed_file} does not exist. Run scripts/generate_schemes_seed.py first.")
        return

    with open(seed_file, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    print(f"Loaded {len(schemes)} schemes. Initializing vector store and BM25...")
    store = VectorStore()
    count = store.build_from_schemes(schemes)
    print(f"FAISS index built with {count} schemes at {store.index_path}")

    bm25 = BM25Retriever()
    bm25.build_from_schemes(schemes)
    print("BM25 index initialized.")

    # Test search
    test_queries = [
        "farmer scheme financial assistance",
        "ಕರ್ನಾಟಕ ವಿದ್ಯಾರ್ಥಿವೇತನ",
        "health insurance hospital",
        "unemployed youth allowance Karnataka",
    ]
    print("\n--- Test Retrieval Results ---")
    for q in test_queries:
        res = store.search(q, top_k=2)
        print(f"\nQuery: '{q}' -> Top Vector Matches: {res}")
        bm25_res = bm25.search(q, top_k=2)
        print(f"Query: '{q}' -> Top BM25 Matches: {bm25_res}")


if __name__ == "__main__":
    build()
