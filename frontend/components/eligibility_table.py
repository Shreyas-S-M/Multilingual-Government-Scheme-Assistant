"""
Streamlit Criterion-Level Eligibility Assessment Table Component.
Displays granular evidence linking applicant values against official requirements.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any


def render_eligibility_table(criteria_results: List[Dict[str, Any]]):
    """Renders a comprehensive, styled breakdown table for individual scheme criteria."""
    if not criteria_results:
        st.info("No criteria records available to display.")
        return

    rows = []
    for cr in criteria_results:
        status_val = cr.get("status", "UNKNOWN")
        icon = "✅ PASS" if status_val == "PASS" else ("⏳ UNKNOWN" if status_val == "UNKNOWN" else "❌ FAIL")
        user_val = str(cr.get("user_value")) if cr.get("user_value") is not None else "Not Provided"
        exp_val = str(cr.get("expected_value"))
        rule_type = "Mandatory" if cr.get("is_mandatory", True) else "Optional"

        rows.append({
            "Criterion": cr.get("name", ""),
            "Rule Type": rule_type,
            "Required Value": exp_val,
            "Your Value": user_val,
            "Status": icon,
            "Reason": cr.get("reason", ""),
            "Official Source Citation": cr.get("source_citation", ""),
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status", help="PASS, FAIL, or UNKNOWN"),
            "Reason": st.column_config.TextColumn("Reason / Evaluation", width="medium"),
            "Official Source Citation": st.column_config.TextColumn("Source / Gazette Clause", width="medium"),
        },
    )
