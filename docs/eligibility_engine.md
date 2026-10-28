# Three-State Eligibility Reasoning Engine

## 1. Formal Three-State Semantics

A primary academic limitation of conventional RAG and chatbot systems is the **closed-world assumption**, where missing user information is implicitly treated as a failure or hallucinated.

The **Three-State Eligibility Reasoning Engine** introduces formal three-state logic:

$$\text{Eligibility}(c) \in \{\text{PASS}, \text{FAIL}, \text{UNKNOWN}\}$$

1. **`PASS`**: The citizen has explicitly provided the relevant attribute, and it strictly satisfies the official predicate condition:
   $$\text{Eval}(r, u) = \text{PASS} \iff u \models r$$
2. **`FAIL`**: The citizen has provided the attribute, and the value explicitly violates the official threshold or restriction:
   $$\text{Eval}(r, u) = \text{FAIL} \iff u \not\models r$$
3. **`UNKNOWN`**: The applicant has not yet specified the attribute, or the provided statement is conflicting/ambiguous.
   $$\text{Eval}(r, u) = \text{UNKNOWN} \iff u = \bot \lor u \in \text{Conflict}$$
   
> **Non-Negotiable Rule:** `UNKNOWN` is never treated as a synonym for `FAIL`. Missing information triggers targeted clarification rather than rejection.

---

## 2. Supported Predicate Operators

| Operator | Syntax Identifier | Semantic Definition | Example Application |
| :--- | :--- | :--- | :--- |
| **Equals** | `equals` | $u = \text{exp}$ | `occupation == "farmer"` |
| **Not Equals** | `not_equals` | $u \ne \text{exp}$ | `status != "tax_payer"` |
| **Greater Than / Equal** | `greater_than_or_equal` | $u \ge \text{exp}$ | `age >= 18` |
| **Less Than / Equal** | `less_than_or_equal` | $u \le \text{exp}$ | `annual_income <= 250000.0` |
| **Inclusive Range** | `inclusive_range` | $\text{low} \le u \le \text{high}$ | `18 <= age <= 40` |
| **In List** | `in_list` | $u \in \text{allowed\_set}$ | `social_category in ['sc', 'st']` |
| **Boolean Match** | `boolean_is` | $\text{bool}(u) = \text{bool}(\text{exp})$ | `has_bpl_card == True` |
| **State Match** | `state_match` | $u_{\text{state}} = \text{exp}_{\text{state}}$ | `state == "Karnataka"` |

---

## 3. Scheme-Level Aggregation Policy

Let a scheme $S$ have a set of mandatory rules $M = \{m_1, m_2, \dots, m_k\}$ and optional rules $O = \{o_1, \dots, o_j\}$.

The overall eligibility status $\Phi(S, u)$ is aggregated as follows:

$$\Phi(S, u) = \begin{cases}
\text{FAIL} & \text{if } \exists m \in M \text{ such that } \text{Eval}(m, u) = \text{FAIL} \\
\text{UNKNOWN} & \text{if } (\forall m \in M, \text{Eval}(m, u) \ne \text{FAIL}) \land (\exists m \in M \text{ such that } \text{Eval}(m, u) = \text{UNKNOWN}) \\
\text{PASS} & \text{if } \forall m \in M, \text{Eval}(m, u) = \text{PASS}
\end{cases}$$

### Key Properties:
- **Mandatory Failure Dominance:** A confirmed failure of any mandatory criterion immediately classifies the scheme as `FAIL`. High semantic vector similarity cannot override a mandatory failure.
- **Uncertainty Propagation:** If no mandatory condition fails, but at least one mandatory condition is unknown, the overall status remains `UNKNOWN`.
- **Optional Criteria Isolation:** Optional criteria track additional bonuses or entitlements without causing false disqualifications.

---

## 4. Adaptive Clarification Question Selection

When relevant candidate schemes remain in `UNKNOWN` status:
1. The engine aggregates all missing mandatory attributes across active candidate schemes:
   $$\text{Score}(a) = \sum_{S \in \text{Viable}} \mathbb{I}[a \in \text{Missing}(S)]$$
2. The attribute $a^*$ that maximizes information gain across the highest number of pending schemes is selected.
3. A localized, targeted clarification question is formulated in English or Kannada.
4. Once the applicant responds, the user profile is updated and eligibility is recalculated immediately.

---

## 5. Near-Miss Alternative Recommendation

When an applicant is confirmed ineligible (`FAIL`) for their desired scheme:
1. The engine retrieves other schemes within the same sector or targeting similar social needs.
2. The eligibility engine evaluates each alternative against the current profile.
3. Viable alternatives (status `PASS` or `UNKNOWN` with zero mandatory failures) are prioritized.
4. Comparative reasoning is provided, explicitly stating why the original scheme failed and why the alternative is a credible option.
