"""
Three-State Eligibility Reasoning Engine.
Executes criterion-level evaluations and aggregates overall scheme eligibility using
formal three-state logic (PASS, FAIL, UNKNOWN).
Independent of LLM, frontend, and vector store.
"""
from typing import List, Dict, Any, Union
from backend.schemas.user_profile import UserProfile
from backend.schemas.eligibility import (
    CriterionRule,
    CriterionResult,
    EligibilityStatus,
    SchemeEligibilityResult,
)
from backend.eligibility.predicates import PredicateEvaluator


class EligibilityEngine:
    @staticmethod
    def evaluate_scheme(
        scheme: Any, profile: UserProfile
    ) -> SchemeEligibilityResult:
        """
        Evaluates a scheme against a user profile.
        scheme can be a SchemeModel, SchemeBase, or dict.
        """
        # Extract scheme attributes safely
        if isinstance(scheme, dict):
            scheme_id = scheme.get("scheme_id", "")
            scheme_name = scheme.get("name", "")
            rules_raw = scheme.get("rules", [])
            official_url = scheme.get("official_portal_url", "")
            benefits_summary = scheme.get("benefits_summary", "")
        else:
            scheme_id = getattr(scheme, "scheme_id", "")
            scheme_name = getattr(scheme, "name", "")
            rules_raw = getattr(scheme, "rules", [])
            official_url = getattr(scheme, "official_portal_url", "")
            benefits_summary = getattr(scheme, "benefits_summary", "")

        criteria_results: List[CriterionResult] = []
        mandatory_passed = 0
        mandatory_failed = 0
        mandatory_unknown = 0
        optional_passed = 0
        optional_failed = 0
        optional_unknown = 0

        missing_attrs = []
        failed_criteria = []

        # Safeguard: A scheme entry without explicit criteria must never be marked eligible (PASS).
        if not rules_raw:
            return SchemeEligibilityResult(
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                overall_status=EligibilityStatus.UNKNOWN,
                mandatory_passed_count=0,
                mandatory_failed_count=0,
                mandatory_unknown_count=1,
                optional_passed_count=0,
                optional_failed_count=0,
                optional_unknown_count=0,
                criteria_results=[],
                summary_explanation=(
                    f"Eligibility for {scheme_name} cannot be assessed because structured, verified criteria are not yet available. "
                    "Check the official portal before relying on this entry."
                ),
                missing_attributes=["scheme_specific_criteria"],
                failed_criteria=[],
                official_portal_url=official_url,
                benefits_summary=benefits_summary,
            )

        # Evaluate every criterion rule
        for r in rules_raw:
            rule_obj = r if isinstance(r, CriterionRule) else CriterionRule(**(r if isinstance(r, dict) else r.__dict__))
            user_val = getattr(profile, rule_obj.field, None)
            res = PredicateEvaluator.evaluate(rule_obj, user_val)
            criteria_results.append(res)

            if rule_obj.is_mandatory:
                if res.status == EligibilityStatus.PASS:
                    mandatory_passed += 1
                elif res.status == EligibilityStatus.FAIL:
                    mandatory_failed += 1
                    failed_criteria.append(res)
                elif res.status == EligibilityStatus.UNKNOWN:
                    mandatory_unknown += 1
                    if rule_obj.field not in missing_attrs:
                        missing_attrs.append(rule_obj.field)
            else:
                if res.status == EligibilityStatus.PASS:
                    optional_passed += 1
                elif res.status == EligibilityStatus.FAIL:
                    optional_failed += 1
                elif res.status == EligibilityStatus.UNKNOWN:
                    optional_unknown += 1

        # Aggregation Policy (Section 8.3)
        if mandatory_failed > 0:
            overall_status = EligibilityStatus.FAIL
            summary = (
                f"Applicant does not meet {mandatory_failed} mandatory condition(s) for {scheme_name}."
            )
        elif mandatory_unknown > 0:
            overall_status = EligibilityStatus.UNKNOWN
            summary = (
                f"Eligibility for {scheme_name} cannot be confirmed yet because {mandatory_unknown} mandatory requirement(s) are unknown: {', '.join(missing_attrs)}."
            )
        else:
            overall_status = EligibilityStatus.PASS
            summary = (
                f"Applicant appears to satisfy all {mandatory_passed} mandatory criteria for {scheme_name}, subject to official document verification."
            )

        return SchemeEligibilityResult(
            scheme_id=scheme_id,
            scheme_name=scheme_name,
            overall_status=overall_status,
            mandatory_passed_count=mandatory_passed,
            mandatory_failed_count=mandatory_failed,
            mandatory_unknown_count=mandatory_unknown,
            optional_passed_count=optional_passed,
            optional_failed_count=optional_failed,
            optional_unknown_count=optional_unknown,
            criteria_results=criteria_results,
            summary_explanation=summary,
            missing_attributes=missing_attrs,
            failed_criteria=failed_criteria,
            official_portal_url=official_url,
            benefits_summary=benefits_summary,
        )

    @classmethod
    def evaluate_all(
        cls, schemes: List[Any], profile: UserProfile
    ) -> List[SchemeEligibilityResult]:
        """Evaluates a collection of schemes against the profile."""
        return [cls.evaluate_scheme(s, profile) for s in schemes]
