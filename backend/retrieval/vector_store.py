"""
FAISS Vector Store Manager.
Maintains dense vector index, scheme-to-vector positional mappings, and similarity search
for multilingual scheme retrieval.
"""
import json
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import faiss
from backend.core.config import settings
from backend.core.logging import logger
from backend.retrieval.embeddings import MultilingualEmbeddingService, EMBEDDING_DIM


class VectorStore:
    def __init__(
        self,
        index_path: str = None,
        metadata_path: str = None,
        embedder: MultilingualEmbeddingService = None,
    ):
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.metadata_path = metadata_path or settings.INDEX_METADATA_PATH
        self.embedder = embedder or MultilingualEmbeddingService()
        self.index: Optional[faiss.Index] = None
        self.id_to_scheme_id: Dict[int, str] = {}
        self.scheme_id_to_id: Dict[str, int] = {}
        self.metadata: Dict[str, Any] = {}

        # Attempt to load if exists
        self.load()

    def build_search_text(self, scheme: Dict[str, Any]) -> str:
        """Constructs a comprehensive, multilingual textual representation for vector indexing."""
        parts = [
            scheme.get("name", ""),
            scheme.get("name_kannada", "") or "",
            " ".join(scheme.get("aliases", [])),
            scheme.get("category", ""),
            scheme.get("subcategory", "") or "",
            scheme.get("department", ""),
            scheme.get("short_description", ""),
            scheme.get("description_kannada", "") or "",
            scheme.get("benefits_summary", ""),
            scheme.get("benefits_amount", "") or "",
            " ".join(scheme.get("target_occupations", [])),
            " ".join(scheme.get("eligible_categories", [])),
            " ".join(scheme.get("required_documents", [])),
        ]
        return " | ".join([p.strip() for p in parts if p.strip()])

    def build_from_schemes(self, schemes: List[Dict[str, Any]]) -> int:
        """
        Builds FAISS IndexFlatIP index over all verified scheme records.
        Saves index and metadata files upon completion.
        """
        if not schemes:
            logger.warning("No schemes provided for vector index building.")
            return 0

        logger.info(f"Building vector index for {len(schemes)} schemes...")
        texts = [self.build_search_text(s) for s in schemes]
        embeddings = self.embedder.encode(texts)

        # Dimension validation
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)

        self.index = index
        self.id_to_scheme_id = {i: s["scheme_id"] for i, s in enumerate(schemes)}
        self.scheme_id_to_id = {s["scheme_id"]: i for i, s in enumerate(schemes)}
        self.metadata = {
            "total_schemes": len(schemes),
            "embedding_dimension": dim,
            "embedding_model": self.embedder.model_name,
            "scheme_ids": [s["scheme_id"] for s in schemes],
        }

        self.save()
        logger.info(f"FAISS index built and saved successfully with {len(schemes)} schemes.")
        return len(schemes)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Searches index for most semantically similar schemes.
        Returns:
            List of (scheme_id, similarity_score)
        """
        if not self.is_ready():
            logger.warning("FAISS index is not loaded or empty.")
            return []

        query_vec = self.embedder.encode_one(query).reshape(1, -1)
        k = min(top_k, self.index.ntotal)
        if k <= 0:
            return []

        distances, indices = self.index.search(query_vec, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx in self.id_to_scheme_id:
                scheme_id = self.id_to_scheme_id[idx]
                results.append((scheme_id, float(dist)))
        return results

    def is_ready(self) -> bool:
        return self.index is not None and self.index.ntotal > 0

    def save(self):
        """Serializes FAISS index binary and metadata JSON to disk."""
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)

        meta = {
            "metadata": self.metadata,
            "id_to_scheme_id": {str(k): v for k, v in self.id_to_scheme_id.items()},
        }
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    def load(self) -> bool:
        """Loads FAISS index and metadata if present on disk."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                self.metadata = meta.get("metadata", {})
                self.id_to_scheme_id = {
                    int(k): v for k, v in meta.get("id_to_scheme_id", {}).items()
                }
                self.scheme_id_to_id = {v: k for k, v in self.id_to_scheme_id.items()}
                logger.info(
                    f"Loaded FAISS index with {self.index.ntotal} schemes from {self.index_path}"
                )
                return True
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
        return False
