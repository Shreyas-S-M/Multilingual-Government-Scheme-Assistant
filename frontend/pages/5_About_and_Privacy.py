"""
Streamlit Page 5: About, Architecture, and Citizen Privacy Policy.
Explains academic contribution, architecture flow, and ethical non-inference guidelines.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="About & Privacy | Multilingual Govt Scheme Assistant",
    page_icon="ℹ️",
    layout="wide",
)

# Load CSS
css_path = Path(__file__).resolve().parent.parent / "styles" / "main.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("ℹ️ About the Project & Citizen Privacy Notice")

st.markdown(
    """
    ### 🏛️ Academic Affiliation & Project Team
    - **Institution:** School of Computer Science and Engineering, RV University, Bengaluru
    - **Faculty Guide:** Dr. Roopesh
    - **Project Team Members:**
      1. Shreyas Kamath D (`1RUA24CSE0444`)
      2. Shreyas S M (`1RUA24CSE0446`)
      3. Shreyash Annegowda (`1RUA24CSE0447`)
      4. Skanda C H (`1RUA24CSE0463`)

    ---

    ### 🎯 Project Overview
    The **Multilingual Government Scheme Assistant** is an academic NLP project engineered to democratize access to
    social welfare programs in India, focusing on **English, Kannada, and code-mixed Kannada-English queries**.

    #### 💡 Academic Innovation & Contributions (vs. Existing Literature)
    Unlike generic chatbots, probabilistic ML predictors, or naive RAG search engines:
    1. **Three-State Eligibility Reasoning (`PASS`, `FAIL`, `UNKNOWN`):**
       Formally implements three-state logic. Incomplete citizen data strictly produces `UNKNOWN` with targeted follow-up prompts,
       avoiding false disqualifications caused by the closed-world assumption.
    2. **Deterministic Eligibility Boundary:**
       The rule engine is legally authoritative. Vector similarity alone can **never** override a confirmed mandatory eligibility failure.
    3. **Adaptive Clarification Questioning:**
       Dynamically identifies and asks for the missing attribute that resolves uncertainty for the maximum number of pending schemes.
    4. **Near-Miss Alternative Discovery:**
       When an applicant is disqualified from an intended scheme, the system discovers viable alternative programs in the same sector with transparent comparative justifications.
    5. **Multilingual Entity Normalization:**
       Robust parsing of Indian currency formats (lakh, crore, ಸಾವಿರ), Kannada numerals (೦-೯), and localized occupation terms without hallucination.
    """
)

st.divider()

st.subheader("🛡️ Citizen Privacy, Ethical NLP & Non-Inference Safeguards")
st.markdown(
    """
    - **Strict Non-Inference of Sensitive Data:** Sensitive attributes such as Caste (`SC`/`ST`/`OBC`), Religion (`Minority`),
      Disability, and Income are **never inferred** from a user's name, writing style, language, or geographical location.
      They are evaluated only when voluntarily provided or confirmed by the applicant.
    - **No Mandatory Account Registration:** Citizens can discover schemes and verify eligibility completely anonymously.
    - **Zero-Data Leakage Fallback:** Core eligibility evaluation runs entirely on deterministic rules and local FAISS vector search.
      Queries are not sent to external proprietary LLMs unless explicitly configured.
    - **Session Ephemerality:** Citizens can reset their conversation profile at any time with a single click.
    """
)

st.divider()

st.subheader("🏛️ Official Source Provenance & Freshness")
st.markdown(
    """
    All scheme criteria, benefit numbers, and document checklists in this repository are curated from official portals:
    - [myScheme National Portal (myscheme.gov.in)](https://www.myscheme.gov.in/)
    - [National Scholarship Portal (scholarships.gov.in)](https://scholarships.gov.in/)
    - [Karnataka Seva Sindhu Guarantee Portal (sevasindhu.karnataka.gov.in)](https://sevasindhu.karnataka.gov.in/)
    - [PM-KISAN Portal (pmkisan.gov.in)](https://pmkisan.gov.in/)
    - [National Health Authority - PM-JAY (pmjay.gov.in)](https://pmjay.gov.in/)
    """
)

st.caption("Version: 1.0.0 | Academic NLP Capstone Build | Open Source")
