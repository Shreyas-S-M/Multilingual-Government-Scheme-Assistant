"""
Unit Tests for Adaptive Questioning and Near-Miss Recommendations.
"""
import pytest
from backend.schemas.eligibility import SchemeEligibilityResult, EligibilityStatus
from backend.schemas.user_profile import UserProfile
from backend.eligibility.adaptive_questioner import AdaptiveQuestioner
from backend.eligibility.near_miss import NearMissRecommender


def test_adaptive_questioner_picks_most_frequent_missing_field():
    profile = UserProfile(age=25)

    res1 = SchemeEligibilityResult(
        scheme_id="s1",
        scheme_name="Scheme 1",
        overall_status=EligibilityStatus.UNKNOWN,
        missing_attributes=["annual_income", "state"],
        summary_explanation="Need income and state",
    )
    res2 = SchemeEligibilityResult(
        scheme_id="s2",
        scheme_name="Scheme 2",
        overall_status=EligibilityStatus.UNKNOWN,
        missing_attributes=["annual_income"],
        summary_explanation="Need income",
    )

    q_en, target = AdaptiveQuestioner.select_next_question([res1, res2], profile, language="en")
    assert target == "annual_income"
    assert "income" in q_en.lower()

    # In Kannada
    q_kn, target_kn = AdaptiveQuestioner.select_next_question([res1, res2], profile, language="kn")
    assert target_kn == "annual_income"
    assert "ಆದಾಯ" in q_kn


def test_near_miss_recommender_finds_viable_alternative():
    # User who is a student with income 3 Lakh (Fails SC scholarship income ceiling)
    profile = UserProfile(
        age=20,
        occupation="student",
        is_student=True,
        annual_income=300000.0,
        social_category="sc",
    )

    failed_scheme = SchemeEligibilityResult(
        scheme_id="post-matric-sc",
        scheme_name="Post Matric SC Scholarship",
        overall_status=EligibilityStatus.FAIL,
        mandatory_failed_count=1,
        summary_explanation="Fails income limit",
    )

    # Candidate alternative with higher income ceiling: NMMSS (<= 3.5 Lakh)
    candidate_schemes = [
        {
            "scheme_id": "post-matric-sc",
            "name": "Post Matric SC Scholarship",
            "category": "Education",
            "rules": [],
        },
        {
            "scheme_id": "nmmss",
            "name": "National Means-cum-Merit Scholarship Scheme (NMMSS)",
            "category": "Education",
            "rules": [
                {
                    "criterion_id": "nm_inc",
                    "name": "Income <= 3.5 Lakh",
                    "field": "annual_income",
                    "operator": "less_than_or_equal",
                    "expected_value": 350000.0,
                    "is_mandatory": True,
                    "source_citation": "Section 3",
                },
                {
                    "criterion_id": "nm_stu",
                    "name": "Is Student",
                    "field": "is_student",
                    "operator": "boolean_is",
                    "expected_value": True,
                    "is_mandatory": True,
                    "source_citation": "Section 2",
                },
            ],
        },
    ]

    alts = NearMissRecommender.find_alternatives_for_failed_schemes(
        failed_results=[failed_scheme],
        all_candidate_schemes=candidate_schemes,
        profile=profile,
    )

    assert len(alts) == 1
    assert alts[0].scheme_id == "nmmss"
    assert alts[0].overall_status == EligibilityStatus.PASS
    assert alts[0].is_near_miss is True
