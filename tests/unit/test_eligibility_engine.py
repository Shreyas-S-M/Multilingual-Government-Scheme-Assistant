"""
Unit Tests for Three-State Eligibility Reasoning Engine.
Verifies all predicate operators, PASS, FAIL, UNKNOWN semantics, and aggregation policies.
"""
import pytest
from backend.schemas.eligibility import (
    CriterionRule,
    EligibilityOperator,
    EligibilityStatus,
)
from backend.schemas.user_profile import UserProfile
from backend.eligibility.predicates import PredicateEvaluator
from backend.eligibility.engine import EligibilityEngine


class TestPredicateEvaluator:
    def test_equals_operator(self):
        rule = CriterionRule(
            criterion_id="r_occ",
            name="Occupation Farmer",
            field="occupation",
            operator=EligibilityOperator.EQUALS,
            expected_value="farmer",
            is_mandatory=True,
            source_citation="Section 2.1",
        )
        # PASS case
        res_pass = PredicateEvaluator.evaluate(rule, "farmer")
        assert res_pass.status == EligibilityStatus.PASS

        # FAIL case
        res_fail = PredicateEvaluator.evaluate(rule, "student")
        assert res_fail.status == EligibilityStatus.FAIL

        # UNKNOWN case (missing user value)
        res_unk = PredicateEvaluator.evaluate(rule, None)
        assert res_unk.status == EligibilityStatus.UNKNOWN
        assert res_unk.missing_field == "occupation"

    def test_range_and_comparison_operators(self):
        rule_range = CriterionRule(
            criterion_id="r_age",
            name="Age between 18 and 40",
            field="age",
            operator=EligibilityOperator.INCLUSIVE_RANGE,
            expected_value=[18, 40],
            is_mandatory=True,
            source_citation="Section 3",
        )
        assert PredicateEvaluator.evaluate(rule_range, 25).status == EligibilityStatus.PASS
        assert PredicateEvaluator.evaluate(rule_range, 17).status == EligibilityStatus.FAIL
        assert PredicateEvaluator.evaluate(rule_range, 41).status == EligibilityStatus.FAIL
        assert PredicateEvaluator.evaluate(rule_range, None).status == EligibilityStatus.UNKNOWN

    def test_income_ceiling_operator(self):
        rule_income = CriterionRule(
            criterion_id="r_inc",
            name="Income <= 2.5 Lakh",
            field="annual_income",
            operator=EligibilityOperator.LESS_THAN_OR_EQUAL,
            expected_value=250000.0,
            is_mandatory=True,
            source_citation="Means Test",
        )
        assert PredicateEvaluator.evaluate(rule_income, 200000.0).status == EligibilityStatus.PASS
        assert PredicateEvaluator.evaluate(rule_income, 250000.0).status == EligibilityStatus.PASS
        assert PredicateEvaluator.evaluate(rule_income, 250001.0).status == EligibilityStatus.FAIL
        assert PredicateEvaluator.evaluate(rule_income, None).status == EligibilityStatus.UNKNOWN

    def test_in_list_operator(self):
        rule_cat = CriterionRule(
            criterion_id="r_cat",
            name="Category in SC/ST",
            field="social_category",
            operator=EligibilityOperator.IN_LIST,
            expected_value=["sc", "st"],
            is_mandatory=True,
            source_citation="Article 15",
        )
        assert PredicateEvaluator.evaluate(rule_cat, "sc").status == EligibilityStatus.PASS
        assert PredicateEvaluator.evaluate(rule_cat, "st").status == EligibilityStatus.PASS
        assert PredicateEvaluator.evaluate(rule_cat, "general").status == EligibilityStatus.FAIL
        assert PredicateEvaluator.evaluate(rule_cat, None).status == EligibilityStatus.UNKNOWN


class TestEligibilityEngineAggregation:
    @pytest.fixture
    def mock_scheme(self):
        return {
            "scheme_id": "test-scheme",
            "name": "Test Welfare Scheme",
            "official_portal_url": "https://gov.in/test",
            "benefits_summary": "Rs. 10,000 grant",
            "rules": [
                {
                    "criterion_id": "t_age",
                    "name": "Age >= 18",
                    "field": "age",
                    "operator": "greater_than_or_equal",
                    "expected_value": 18,
                    "is_mandatory": True,
                    "source_citation": "Rule 1",
                },
                {
                    "criterion_id": "t_state",
                    "name": "State Karnataka",
                    "field": "state",
                    "operator": "state_match",
                    "expected_value": "Karnataka",
                    "is_mandatory": True,
                    "source_citation": "Rule 2",
                },
                {
                    "criterion_id": "t_income",
                    "name": "Income <= 200000",
                    "field": "annual_income",
                    "operator": "less_than_or_equal",
                    "expected_value": 200000.0,
                    "is_mandatory": True,
                    "source_citation": "Rule 3",
                },
            ],
        }

    def test_overall_pass_when_all_mandatory_pass(self, mock_scheme):
        profile = UserProfile(age=25, state="Karnataka", annual_income=150000.0)
        res = EligibilityEngine.evaluate_scheme(mock_scheme, profile)
        assert res.overall_status == EligibilityStatus.PASS
        assert res.mandatory_passed_count == 3
        assert res.mandatory_failed_count == 0
        assert res.mandatory_unknown_count == 0

    def test_overall_fail_when_one_mandatory_fails(self, mock_scheme):
        # Age fails (16 < 18)
        profile = UserProfile(age=16, state="Karnataka", annual_income=150000.0)
        res = EligibilityEngine.evaluate_scheme(mock_scheme, profile)
        assert res.overall_status == EligibilityStatus.FAIL
        assert res.mandatory_failed_count == 1
        assert len(res.failed_criteria) == 1
        assert res.failed_criteria[0].field == "age"

    def test_overall_unknown_when_mandatory_missing(self, mock_scheme):
        # Income is missing
        profile = UserProfile(age=25, state="Karnataka")
        res = EligibilityEngine.evaluate_scheme(mock_scheme, profile)
        assert res.overall_status == EligibilityStatus.UNKNOWN
        assert res.mandatory_unknown_count == 1
        assert "annual_income" in res.missing_attributes

    def test_fail_overrides_unknown(self, mock_scheme):
        # Age fails, and income is missing -> Overall must be FAIL
        profile = UserProfile(age=15, state="Karnataka")
        res = EligibilityEngine.evaluate_scheme(mock_scheme, profile)
        assert res.overall_status == EligibilityStatus.FAIL
        assert res.mandatory_failed_count == 1
        assert res.mandatory_unknown_count == 1
