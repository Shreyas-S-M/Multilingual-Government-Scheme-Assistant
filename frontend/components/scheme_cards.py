"""
Streamlit Scheme Card Component.
Renders responsive cards with status badges, benefits callouts, and official links.
"""
import streamlit as st
from typing import Dict, Any


def render_status_badge(status: str) -> str:
    s = status.upper()
    if s == "PASS":
        return '<span class="badge-pass">✔ PASS (Eligible)</span>'
    elif s == "UNKNOWN":
        return '<span class="badge-unknown">⏳ UNKNOWN (Info Needed)</span>'
    elif s == "FAIL":
        return '<span class="badge-fail">✖ FAIL (Ineligible)</span>'
    return f"<span>{status}</span>"


def render_scheme_card(scheme_result: Dict[str, Any], full_scheme: Dict[str, Any] = None):
    s_name = scheme_result.get("scheme_name") or (full_scheme.get("name") if full_scheme else "Scheme")
    s_id = scheme_result.get("scheme_id", "")
    overall_status = scheme_result.get("overall_status", "UNKNOWN")
    benefits = scheme_result.get("benefits_summary") or (full_scheme.get("benefits_summary") if full_scheme else "")
    summary = scheme_result.get("summary_explanation", "")
    portal_url = scheme_result.get("official_portal_url") or (full_scheme.get("official_portal_url") if full_scheme else "")
    
    badge_html = render_status_badge(overall_status)
    category = full_scheme.get("category", "General") if full_scheme else "Welfare"
    level = full_scheme.get("level", "Central") if full_scheme else "Govt"

    with st.container():
        st.markdown(
            f"""
            <div class="scheme-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div>
                        <div class="scheme-card-title">{s_name}</div>
                        <div class="scheme-meta">🏷️ {category} | 🏛️ {level.capitalize()} Scheme</div>
                    </div>
                    <div>{badge_html}</div>
                </div>
                <div class="scheme-benefit-box">
                    <strong>💰 Benefits:</strong> {benefits}
                </div>
                <p style="font-size: 0.9rem; margin: 0.5rem 0;">{summary}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if portal_url:
                st.link_button(
                    "🌐 Official Portal",
                    url=portal_url,
                    use_container_width=True,
                )
        with col2:
            with st.expander("🔍 View Criterion Details"):
                criteria = scheme_result.get("criteria_results", [])
                if criteria:
                    for cr in criteria:
                        status_sym = "✔" if cr["status"] == "PASS" else ("⏳" if cr["status"] == "UNKNOWN" else "✖")
                        mand_label = "[Mandatory]" if cr.get("is_mandatory", True) else "[Optional]"
                        st.markdown(f"**{status_sym} {cr['name']}** `{cr['status']}` {mand_label}")
                        st.caption(f"Reason: {cr['reason']}")
                        st.caption(f"Source: {cr['source_citation']}")
                        st.divider()
                else:
                    st.info("No detailed criteria breakdown recorded.")
