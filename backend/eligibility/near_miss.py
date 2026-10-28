"""
Near-Miss Recommendation Engine.
When a user fails a desired scheme, identifies credible alternative welfare programs
sharing thematic domain or target demographic, evaluates their eligibility, and generates
transparent comparative explanations.
"""
from typing import List, Dict, Any, Optional
from backend.schemas.user_profile import UserProfile
from backend.schemas.eligibility import (
    SchemeEligibilityResult,
    EligibilityStatus,
    CriterionResult,
)
from backend.eligibility.engine import EligibilityEngine


class NearMissRecommender:
    @classmethod
    def find_alternatives_for_failed_schemes(
        cls,
        failed_results: List[SchemeEligibilityResult],
        all_candidate_schemes: List[Any],
        profile: UserProfile,
        max_alternatives: int = 3,
    ) -> List[SchemeEligibilityResult]:
        """
        Discovers and ranks alternative schemes for candidates with confirmed failures.
        """
        if not failed_results:
            return []

        failed_scheme_ids = {r.scheme_id for r in failed_results}
        alternatives: List[SchemeEligibilityResult] = []

        # Find categories associated with failed schemes
        failed_categories = set()
        for scheme in all_candidate_schemes:
            sid = scheme.get("scheme_id") if isinstance(scheme, dict) else getattr(scheme, "scheme_id", None)
            if sid in failed_scheme_ids:
                cat = scheme.get("category") if isinstance(scheme, dict) else getattr(scheme, "category", None)
                if cat:
                    failed_categories.add(cat)

        # Evaluate candidate schemes in similar categories that were not the original failed ones
        for scheme in all_candidate_schemes:
            sid = scheme.get("scheme_id") if isinstance(scheme, dict) else getattr(scheme, "scheme_id", None)
            if sid in failed_scheme_ids:
                continue

            cat = scheme.get("category") if isinstance(scheme, dict) else getattr(scheme, "category", None)
            # Only consider same category or broad welfare
            if cat not in failed_categories and cat != "Social Welfare":
                continue

            eval_res = EligibilityEngine.evaluate_scheme(scheme, profile)

            # Near-miss candidates must NOT have confirmed mandatory failures
            if eval_res.overall_status != EligibilityStatus.FAIL:
                eval_res.is_near_miss = True
                if eval_res.overall_status == EligibilityStatus.PASS:
                    eval_res.near_miss_reason = (
                        f"Recommended alternative in {cat}: Applicant appears to fully satisfy all criteria for {eval_res.scheme_name}."
                    )
                else:
                    eval_res.near_miss_reason = (
                        f"Potential alternative in {cat}: Does not fail mandatory conditions, but requires: {', '.join(eval_res.missing_attributes)}."
                    )
                alternatives.append(eval_res)

        # Sort: First PASS, then UNKNOWN with fewest missing attributes
        alternatives.sort(
            key=lambda x: (
                0 if x.overall_status == EligibilityStatus.PASS else 1,
                len(x.missing_attributes),
                -x.mandatory_passed_count,
            )
        )

        return alternatives[:max_alternatives]
