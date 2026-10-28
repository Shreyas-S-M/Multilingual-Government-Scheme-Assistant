"""
Eligibility Predicate Evaluator.
Implements rigorous three-state evaluation: PASS, FAIL, UNKNOWN for each criterion.
Ensures that missing data yields UNKNOWN and is never conflated with FAIL.
"""
from typing import Any, Tuple, Optional
from backend.schemas.eligibility import (
    CriterionRule,
    CriterionResult,
    EligibilityStatus,
    EligibilityOperator,
)


class PredicateEvaluator:
    @staticmethod
    def evaluate(
        rule: CriterionRule, user_val: Any
    ) -> CriterionResult:
        """
        Evaluates a single criterion rule against a user profile value.
        Returns:
            CriterionResult with status in {PASS, FAIL, UNKNOWN} and human explanation.
        """
        # If user has not provided this attribute -> UNKNOWN
        if user_val is None:
            return CriterionResult(
                criterion_id=rule.criterion_id,
                name=rule.name,
                field=rule.field,
                operator=rule.operator,
                expected_value=rule.expected_value,
                user_value=None,
                status=EligibilityStatus.UNKNOWN,
                reason=f"Requirement requires '{rule.field}', which has not yet been specified by the user.",
                missing_field=rule.field,
                is_mandatory=rule.is_mandatory,
                source_citation=rule.source_citation,
            )

        op = rule.operator
        exp = rule.expected_value

        try:
            if op == EligibilityOperator.EQUALS:
                passed = (
                    str(user_val).strip().lower() == str(exp).strip().lower()
                    if isinstance(user_val, str)
                    else user_val == exp
                )
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User {rule.field} '{user_val}' matches required '{exp}'."
                    if passed
                    else f"User {rule.field} '{user_val}' does not match required '{exp}'."
                )

            elif op == EligibilityOperator.NOT_EQUALS:
                passed = user_val != exp
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User {rule.field} '{user_val}' is not '{exp}' as required."
                    if passed
                    else f"User {rule.field} cannot be '{exp}'."
                )

            elif op == EligibilityOperator.GREATER_THAN:
                passed = float(user_val) > float(exp)
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User {rule.field} ({user_val}) exceeds minimum {exp}."
                    if passed
                    else f"User {rule.field} ({user_val}) does not exceed required {exp}."
                )

            elif op == EligibilityOperator.GREATER_THAN_OR_EQUAL:
                passed = float(user_val) >= float(exp)
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User {rule.field} ({user_val}) meets minimum requirement of {exp}."
                    if passed
                    else f"User {rule.field} ({user_val}) is below required minimum of {exp}."
                )

            elif op == EligibilityOperator.LESS_THAN:
                passed = float(user_val) < float(exp)
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User {rule.field} ({user_val}) is below maximum ceiling of {exp}."
                    if passed
                    else f"User {rule.field} ({user_val}) is not below {exp}."
                )

            elif op == EligibilityOperator.LESS_THAN_OR_EQUAL:
                passed = float(user_val) <= float(exp)
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User {rule.field} ({user_val}) is within allowable limit of {exp}."
                    if passed
                    else f"User {rule.field} ({user_val}) exceeds allowable ceiling of {exp}."
                )

            elif op == EligibilityOperator.INCLUSIVE_RANGE:
                low, high = float(exp[0]), float(exp[1])
                val = float(user_val)
                passed = low <= val <= high
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User {rule.field} ({val}) is within required range [{low}, {high}]."
                    if passed
                    else f"User {rule.field} ({val}) is outside required range [{low}, {high}]."
                )

            elif op == EligibilityOperator.IN_LIST:
                allowed_list = [str(x).strip().lower() for x in exp] if isinstance(exp, list) else [str(exp).lower()]
                u_str = str(user_val).strip().lower()
                passed = u_str in allowed_list
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User {rule.field} '{user_val}' is in permitted categories {allowed_list}."
                    if passed
                    else f"User {rule.field} '{user_val}' is not among permitted categories {allowed_list}."
                )

            elif op == EligibilityOperator.BOOLEAN_IS:
                b_user = bool(user_val)
                b_exp = bool(exp)
                passed = b_user == b_exp
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"Condition '{rule.name}' is satisfied ({user_val})."
                    if passed
                    else f"Condition '{rule.name}' is not satisfied."
                )

            elif op == EligibilityOperator.STATE_MATCH:
                exp_state = str(exp).strip().lower()
                user_state = str(user_val).strip().lower()
                passed = user_state == exp_state
                status = EligibilityStatus.PASS if passed else EligibilityStatus.FAIL
                reason = (
                    f"User residence '{user_val}' satisfies requirement for '{exp}'."
                    if passed
                    else f"Scheme is restricted to residents of '{exp}', but user residence is '{user_val}'."
                )

            else:
                # Custom predicate fallback
                status = EligibilityStatus.UNKNOWN
                reason = f"Operator '{op}' requires manual review."

            return CriterionResult(
                criterion_id=rule.criterion_id,
                name=rule.name,
                field=rule.field,
                operator=rule.operator,
                expected_value=rule.expected_value,
                user_value=user_val,
                status=status,
                reason=reason,
                missing_field=None,
                is_mandatory=rule.is_mandatory,
                source_citation=rule.source_citation,
            )

        except Exception as e:
            # Type error or parsing exception -> UNKNOWN with warning
            return CriterionResult(
                criterion_id=rule.criterion_id,
                name=rule.name,
                field=rule.field,
                operator=rule.operator,
                expected_value=rule.expected_value,
                user_value=user_val,
                status=EligibilityStatus.UNKNOWN,
                reason=f"Could not reliably evaluate predicate due to type discrepancy: {str(e)}",
                missing_field=rule.field,
                is_mandatory=rule.is_mandatory,
                source_citation=rule.source_citation,
                warning=str(e),
            )
