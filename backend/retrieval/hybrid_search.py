"""
Hybrid Retrieval and Eligibility-Aware Ranking Service.
Fuses semantic vector similarity (FAISS) with lexical BM25 matching,
and ranks results with strict eligibility boundary preservation (PASS, UNKNOWN, FAIL).
"""
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from backend.core.config import settings
from backend.retrieval.vector_store import VectorStore
from backend.retrieval.bm25_search import BM25Retriever
from backend.eligibility.engine import EligibilityEngine
from backend.schemas.user_profile import UserProfile
from backend.schemas.eligibility import SchemeEligibilityResult, EligibilityStatus
from backend.core.logging import logger


class HybridRetriever:
    def __init__(
        self,
        vector_store: VectorStore = None,
        bm25_retriever: BM25Retriever = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.bm25_retriever = bm25_retriever or BM25Retriever()
        self.schemes_by_id: Dict[str, Any] = {}

    def initialize_indexes(self, schemes: List[Dict[str, Any]]):
        """Initializes both FAISS vector index and BM25 index from scheme records."""
        self.schemes_by_id = {s["scheme_id"]: s for s in schemes}
        self.vector_store.build_from_schemes(schemes)
        self.bm25_retriever.build_from_schemes(schemes)

    def retrieve_hybrid(
        self,
        query: str,
        top_k: int = 15,
        vector_weight: float = 0.65,
        bm25_weight: float = 0.35,
    ) -> List[Tuple[str, float]]:
        """
        Combines vector semantic similarity and BM25 lexical scoring.
        Returns:
            List of (scheme_id, hybrid_score)
        """
        vector_results = self.vector_store.search(query, top_k=top_k)
        bm25_results = self.bm25_retriever.search(query, top_k=top_k)

        scores: Dict[str, float] = defaultdict(float)

        # Vector scores
        for scheme_id, score in vector_results:
            scores[scheme_id] += vector_weight * max(0.0, score)

        # BM25 scores
        for scheme_id, score in bm25_results:
            scores[scheme_id] += bm25_weight * max(0.0, score)

        # Fallback if both empty: return all schemes with baseline score
        if not scores and self.schemes_by_id:
            for sid in list(self.schemes_by_id.keys())[:top_k]:
                scores[sid] = 0.1

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    def retrieve_and_evaluate(
        self,
        query: str,
        profile: UserProfile,
        schemes_pool: List[Any],
        top_k: int = 10,
    ) -> Dict[str, List[SchemeEligibilityResult]]:
        """
        Executes hybrid retrieval, runs the Three-State Eligibility Engine,
        and organizes results strictly into:
        - 'eligible' (All mandatory conditions PASS)
        - 'needs_more_info' (Mandatory conditions UNKNOWN, no FAIL)
        - 'ineligible' (Failed one or more mandatory conditions)
        """
        # Ensure scheme map is populated
        if not self.schemes_by_id and schemes_pool:
            self.schemes_by_id = {
                (s.get("scheme_id") if isinstance(s, dict) else s.scheme_id): s
                for s in schemes_pool
            }

        # 1. Retrieve hybrid ranked candidates
        hybrid_candidates = self.retrieve_hybrid(query, top_k=top_k)
        candidate_ids = [sid for sid, _ in hybrid_candidates]

        # Gather scheme records
        schemes_to_eval = [
            self.schemes_by_id[sid]
            for sid in candidate_ids
            if sid in self.schemes_by_id
        ]

        # If hybrid returned fewer, top up with other pool schemes
        if len(schemes_to_eval) < 5 and schemes_pool:
            for s in schemes_pool:
                sid = s.get("scheme_id") if isinstance(s, dict) else s.scheme_id
                if sid not in candidate_ids and len(schemes_to_eval) < top_k:
                    schemes_to_eval.append(s)

        # 2. Run Eligibility Engine
        eval_results: List[SchemeEligibilityResult] = [
            EligibilityEngine.evaluate_scheme(s, profile) for s in schemes_to_eval
        ]

        # 3. Categorize into distinct tiers (Section 7.3)
        eligible = []
        needs_more_info = []
        ineligible = []

        for res in eval_results:
            if res.overall_status == EligibilityStatus.PASS:
                eligible.append(res)
            elif res.overall_status == EligibilityStatus.UNKNOWN:
                needs_more_info.append(res)
            elif res.overall_status == EligibilityStatus.FAIL:
                ineligible.append(res)

        # Sort within each group
        eligible.sort(key=lambda x: x.mandatory_passed_count, reverse=True)
        needs_more_info.sort(
            key=lambda x: (len(x.missing_attributes), -x.mandatory_passed_count)
        )
        ineligible.sort(key=lambda x: x.mandatory_failed_count)

        return {
            "eligible": eligible,
            "needs_more_info": needs_more_info,
            "ineligible": ineligible,
            "all_evaluated": eval_results,
        }
