"""
Chat UI Components.
Renders conversational bubbles, profile tags, and interactive adaptive follow-up blocks.
"""
import streamlit as st
from typing import Dict, Any, Optional


def render_profile_pills(profile_dict: Dict[str, Any]):
    """Renders active user attributes as clean chips."""
    excluded = {"source_spans", "confidences", "field_status"}
    active_attrs = {
        k: v for k, v in profile_dict.items() if v is not None and k not in excluded
    }
    if not active_attrs:
        return

    st.markdown("##### 👤 Detected Applicant Profile")
    pills_html = []
    for k, v in active_attrs.items():
        formatted_k = k.replace("_", " ").title()
        if k == "annual_income":
            formatted_v = f"₹{v:,.0f}"
        else:
            formatted_v = str(v)
        pills_html.append(
            f'<span class="profile-pill"><strong>{formatted_k}:</strong> {formatted_v}</span>'
        )
    st.markdown("".join(pills_html), unsafe_allow_html=True)


def render_follow_up_banner(
    question: Optional[str], target_attribute: Optional[str]
):
    """Renders high-visibility callout box when an adaptive follow-up question is active."""
    if not question:
        return

    st.markdown(
        f"""
        <div class="follow-up-box">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a16207; margin-bottom: 0.3rem;">
                🎯 Clarification Needed ({target_attribute.replace('_', ' ').title() if target_attribute else 'Eligibility'})
            </div>
            <div style="font-size: 1.05rem;">{question}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
