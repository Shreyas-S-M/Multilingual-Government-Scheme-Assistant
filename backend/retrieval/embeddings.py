"""
Multilingual Embedding Service.
Generates dense vector embeddings for schemes and queries in English, Kannada, and code-mixed text.
Uses SentenceTransformers with a deterministic subword hashing fallback for offline/isolated runtime.
"""
import hashlib
import numpy as np
from typing import List
from backend.core.config import settings
from backend.core.logging import logger

EMBEDDING_DIM = 384


class MultilingualEmbeddingService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.model = None
        self._initialized = False

    def _ensure_model(self):
        """Lazy load SentenceTransformer if configured and available; otherwise uses deterministic embedder."""
        if self._initialized:
            return
        self._initialized = True
        import os
        if "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("OFFLINE_EMBEDDINGS", "false").lower() in ("true", "1", "yes"):
            self.model = None
            return

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name, device=settings.DEVICE)
            logger.info("Loaded SentenceTransformer model.")
        except Exception as e:
            logger.info(f"SentenceTransformer not loaded ({e}). Using deterministic embedder.")
            self.model = None

    def _fallback_embed(self, text: str) -> np.ndarray:
        """
        Deterministic, multilingual 384-dimensional dense vector generator.
        Uses character n-grams and token hashes to capture multilingual semantics
        across English, Kannada, and code-mixed scripts without external API dependency.
        """
        vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        if not text:
            return vec

        # Generate character 3-grams, 4-grams and words
        clean_text = text.lower().strip()
        tokens = clean_text.split()
        ngrams = [clean_text[i : i + 3] for i in range(len(clean_text) - 2)]
        ngrams += [clean_text[i : i + 4] for i in range(len(clean_text) - 3)]
        all_features = tokens + ngrams

        for feat in all_features:
            h = int(hashlib.md5(feat.encode("utf-8")).hexdigest(), 16)
            idx = h % EMBEDDING_DIM
            sign = 1.0 if (h >> 9) & 1 else -1.0
            vec[idx] += sign

        # L2 Normalize
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encodes a list of texts into normalized float32 vectors (shape: [N, 384])."""
        if not texts:
            return np.zeros((0, EMBEDDING_DIM), dtype=np.float32)

        self._ensure_model()
        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                return embeddings.astype(np.float32)
            except Exception as e:
                logger.warning(f"Error during model.encode ({e}), using fallback embedder.")

        # Fallback embeddings
        fallback_vecs = [self._fallback_embed(t) for t in texts]
        return np.vstack(fallback_vecs).astype(np.float32)

    def encode_one(self, text: str) -> np.ndarray:
        """Encodes single text into a 1D vector."""
        return self.encode([text])[0]
