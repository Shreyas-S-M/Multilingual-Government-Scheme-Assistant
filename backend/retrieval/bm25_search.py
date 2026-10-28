"""
BM25 Lexical Search Module.
Provides keyword-based search over scheme documents using BM25Okapi with multilingual tokenization.
"""
import re
from typing import List, Tuple, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from backend.core.logging import logger


class BM25Retriever:
    def __init__(self):
        self.bm25: Optional[BM25Okapi] = None
        self.scheme_ids: List[str] = []
        self.corpus_size: int = 0

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Multilingual tokenization preserving Kannada words and alphanumeric terms."""
        if not text:
            return []
        # Match words in Latin or Kannada Unicode ranges
        tokens = re.findall(r"[\w\u0C80-\u0CFF]+", text.lower())
        return [t for t in tokens if len(t) > 1]

    def build_from_schemes(self, schemes: List[Dict[str, Any]]):
        """Builds BM25 index over textual scheme metadata."""
        if not schemes:
            return

        self.scheme_ids = [s["scheme_id"] for s in schemes]
        tokenized_corpus = []

        for s in schemes:
            doc_text = " ".join([
                s.get("name", ""),
                s.get("name_kannada", "") or "",
                " ".join(s.get("aliases", [])),
                s.get("category", ""),
                s.get("subcategory", "") or "",
                s.get("department", ""),
                s.get("short_description", ""),
                s.get("description_kannada", "") or "",
                s.get("benefits_summary", ""),
                " ".join(s.get("target_occupations", [])),
                " ".join(s.get("eligible_categories", [])),
            ])
            tokens = self.tokenize(doc_text)
            tokenized_corpus.append(tokens)

        self.bm25 = BM25Okapi(tokenized_corpus)
        self.corpus_size = len(schemes)
        logger.info(f"Built BM25 index over {self.corpus_size} schemes.")

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Executes lexical BM25 query.
        Returns:
            List of (scheme_id, normalized_bm25_score)
        """
        if not self.bm25 or self.corpus_size == 0:
            return []

        tokens = self.tokenize(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        max_score = max(scores) if max(scores) > 0 else 1.0

        scored_schemes = [
            (self.scheme_ids[i], float(scores[i] / max_score))
            for i in range(len(scores))
            if scores[i] > 0
        ]
        scored_schemes.sort(key=lambda x: x[1], reverse=True)
        return scored_schemes[:top_k]
