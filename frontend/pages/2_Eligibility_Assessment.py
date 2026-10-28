"""
Streamlit Page 2: Standalone Eligibility Assessment.
Enables citizens to input profile parameters directly and view granular,
criterion-level evaluations with PASS, FAIL, UNKNOWN reasoning.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from frontend.services.api_client import APIClient
from frontend.components.eligibility_table import render_eligibility_table

st.set_page_config(
    page_title="Eligibility Assessment | Multilingual Govt Scheme Assistant",
    page_icon="⚖️",
    layout="wide",
)

# Load CSS
css_path = Path(__file__).resolve().parent.parent / "styles" / "main.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("⚖️ Comprehensive Eligibility Assessment")
st.markdown("Enter your parameters to test eligibility against structured predicates derived from official government orders.")

with st.form("profile_form"):
    st.subheader("1. Demographic & Economic Details")
    c1, c2, c3 = st.columns(3)
    with c1:
        age_input = st.number_input("Age (Years)", min_value=0, max_value=110, value=25)
    with c2:
        income_input = st.number_input(
            "Annual Family Income (₹ INR)", min_value=0.0, max_value=10000000.0, value=150000.0, step=10000.0
        )
    with c3:
        state_input = st.selectbox("State of Residence", options=["Karnataka", "Delhi", "Maharashtra", "Tamil Nadu", "Other"])

    st.subheader("2. Occupation & Education")
    c4, c5, c6 = st.columns(3)
    with c4:
        occ_input = st.selectbox(
            "Primary Occupation",
            options=["farmer", "student", "unemployed", "artisan", "street_vendor", "salaried", "self_employed", "other"],
        )
    with c5:
        edu_input = st.selectbox(
            "Highest Education",
            options=["none", "10th_pass", "12th_pass", "graduate", "diploma", "postgraduate"],
        )
    with c6:
        is_student_input = st.checkbox("Currently Enrolled as Active Student", value=(occ_input == "student"))

    st.subheader("3. Social Category & Special Attributes")
    c7, c8, c9 = st.columns(3)
    with c7:
        gender_input = st.selectbox("Gender", options=["female", "male", "transgender", "all"])
    with c8:
        category_input = st.selectbox("Social Category", options=["general", "obc", "sc", "st", "minority", "ews"])
    with c9:
        bpl_input = st.checkbox("Family Holds BPL / Antyodaya Ration Card", value=True)

    submitted = st.form_submit_button("🚀 Run Comprehensive Eligibility Evaluation", use_container_width=True)

if submitted:
    profile_payload = {
        "age": age_input,
        "annual_income": income_input,
        "state": state_input,
        "occupation": occ_input,
        "education_level": edu_input,
        "is_student": is_student_input,
        "gender": gender_input,
        "social_category": category_input,
        "has_bpl_card": bpl_input,
    }

    with st.spinner("Evaluating criteria predicates across all government schemes..."):
        eval_results = APIClient.check_eligibility(profile_payload)

    if not eval_results:
        st.error("No evaluation output received. Ensure backend API server is running.")
    else:
        passed_schemes = [r for r in eval_results if r["overall_status"] == "PASS"]
        unknown_schemes = [r for r in eval_results if r["overall_status"] == "UNKNOWN"]
        failed_schemes = [r for r in eval_results if r["overall_status"] == "FAIL"]

        st.markdown(f"### Evaluation Summary: **{len(passed_schemes)} Eligible** | **{len(unknown_schemes)} Need Info** | **{len(failed_schemes)} Ineligible**")

        tab_pass, tab_unknown, tab_fail = st.tabs([
            f"✅ Confirmed Eligible ({len(passed_schemes)})",
            f"⏳ More Information Needed ({len(unknown_schemes)})",
            f"❌ Ineligible ({len(failed_schemes)})",
        ])

        with tab_pass:
            if not passed_schemes:
                st.info("No schemes currently satisfy 100% of mandatory conditions with the current inputs.")
            for r in passed_schemes:
                st.success(f"**{r['scheme_name']}** — {r['summary_explanation']}")
                st.caption(f"Benefits: {r['benefits_summary']}")
                render_eligibility_table(r.get("criteria_results", []))
                if r.get("official_portal_url"):
                    st.link_button(f"🌐 Apply on Official Portal", url=r["official_portal_url"])
                st.divider()

        with tab_unknown:
            if not unknown_schemes:
                st.info("No schemes in undetermined status.")
            for r in unknown_schemes:
                st.warning(f"**{r['scheme_name']}** — {r['summary_explanation']}")
                st.caption(f"Missing attributes to determine eligibility: `{', '.join(r.get('missing_attributes', []))}`")
                render_eligibility_table(r.get("criteria_results", []))
                st.divider()

        with tab_fail:
            if not failed_schemes:
                st.info("No failed schemes.")
            for r in failed_schemes:
                st.error(f"**{r['scheme_name']}** — {r['summary_explanation']}")
                render_eligibility_table(r.get("criteria_results", []))
                st.divider()
