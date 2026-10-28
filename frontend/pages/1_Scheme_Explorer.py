"""
Streamlit Page 1: Government Scheme Explorer.
Enables citizens and administrators to search, filter, and inspect verified government schemes.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from frontend.services.api_client import APIClient

st.set_page_config(
    page_title="Scheme Explorer | Multilingual Govt Scheme Assistant",
    page_icon="🔍",
    layout="wide",
)

# Load CSS
css_path = Path(__file__).resolve().parent.parent / "styles" / "main.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔍 Government Scheme Catalog & Explorer")
st.markdown("Browse, search, and inspect verified Central and Karnataka State government welfare schemes.")

# Search & Filters Bar
col_search, col_cat, col_lvl, col_state = st.columns([2, 1, 1, 1])

with col_search:
    search_query = st.text_input("🔎 Search Schemes", placeholder="e.g. Kisan, Scholarship, Health, Gruha...")
with col_cat:
    category = st.selectbox(
        "Category",
        options=["All", "Agriculture", "Education", "Employment", "Healthcare", "Social Welfare"],
    )
with col_lvl:
    level = st.selectbox("Government Level", options=["All", "central", "state"])
with col_state:
    state_opt = st.selectbox("State", options=["All", "Karnataka"])

# Query backend
res = APIClient.list_schemes(
    category=None if category == "All" else category,
    level=None if level == "All" else level,
    state=None if state_opt == "All" else state_opt,
    search=search_query.strip() if search_query else None,
    page_size=50,
)

schemes = res.get("items", [])
st.markdown(f"**Found {res.get('total', 0)} verified scheme(s)**")

if not schemes:
    st.info("No schemes matched the specified filter criteria.")
else:
    for s in schemes:
        with st.container():
            st.markdown(
                f"""
                <div class="scheme-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="scheme-card-title">{s['name']}</span>
                        <span class="badge-pass">{s['level'].upper()}</span>
                    </div>
                    <div class="scheme-meta">🏛️ {s['department']} | 🏷️ {s['category']} {f'({s.get("subcategory")})' if s.get('subcategory') else ''}</div>
                    <div class="scheme-benefit-box">💰 <strong>Benefits:</strong> {s['benefits_summary']}</div>
                    <p style="font-size:0.9rem; margin:0.5rem 0;">{s['short_description']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_details, col_link = st.columns([1, 1])
            with col_details:
                with st.expander("📄 View Scheme Guidelines & Rules"):
                    full_details = APIClient.get_scheme_details(s["scheme_id"])
                    if full_details:
                        st.markdown(f"**Official Source:** {full_details.get('source_title')}")
                        st.markdown(f"**Last Verified Date:** `{full_details.get('last_verified_date')}`")
                        
                        docs = full_details.get("required_documents", [])
                        if docs:
                            st.markdown("##### 📁 Required Documents:")
                            for d in docs:
                                st.markdown(f"- {d}")

                        rules = full_details.get("rules", [])
                        if rules:
                            st.markdown("##### ⚙️ Structured Eligibility Criteria:")
                            for r in rules:
                                st.markdown(f"- **{r['name']}**: requires `{r['field']}` `{r['operator']}` `{r['expected_value']}`")
                                st.caption(f"  *Citation: {r['source_citation']}*")

                        process = full_details.get("application_process", [])
                        if process:
                            st.markdown("##### 📝 Application Steps:")
                            for step in process:
                                st.markdown(f"1. {step}")
            with col_link:
                if s.get("official_portal_url"):
                    st.link_button("🌐 Open Official Portal", url=s["official_portal_url"], use_container_width=True)

            st.divider()
