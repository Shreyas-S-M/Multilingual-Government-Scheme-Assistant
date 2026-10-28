"""
Streamlit Page 3: Administrative Dashboard.
Role-protected catalog management, index rebuilding, JSON batch import, and system metrics.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json
import streamlit as st
from frontend.services.api_client import APIClient

st.set_page_config(
    page_title="Admin Dashboard | Multilingual Govt Scheme Assistant",
    page_icon="🛡️",
    layout="wide",
)

# Load CSS
css_path = Path(__file__).resolve().parent.parent / "styles" / "main.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🛡️ Administrative & Data Quality Dashboard")
st.caption("Authorized access for scheme catalog curation, index rebuilding, and provenance management.")

# Authentication
if "admin_api_key" not in st.session_state:
    st.session_state.admin_api_key = "admin-secret-dev-key-change-in-production"

with st.sidebar:
    st.subheader("Admin Authentication")
    key_input = st.text_input(
        "Enter Admin API Key",
        value=st.session_state.admin_api_key,
        type="password",
        help="Header key for administrative endpoint authorization (X-Admin-API-Key)",
    )
    if st.button("Authenticate Key"):
        st.session_state.admin_api_key = key_input
        st.success("API Key updated in session.")

# Check Admin API Key
stats = APIClient.get_admin_stats(st.session_state.admin_api_key)

if not stats:
    st.error("🔒 Unauthorized or Backend Unreachable. Please enter a valid Admin API Key in the sidebar.")
    st.info("Default local dev key: `admin-secret-dev-key-change-in-production` (configured in `.env`).")
    st.stop()

# 1. Statistics Cards
st.subheader("📊 Catalog & Search Engine Statistics")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Schemes", stats.get("total_schemes", 0))
m2.metric("Active Schemes", stats.get("active_schemes", 0))
m3.metric("Central Schemes", stats.get("central_schemes", 0))
m4.metric("State Schemes", stats.get("state_schemes", 0))
m5.metric("FAISS Indexed", stats.get("faiss_indexed_schemes", 0))

# 2. Categories Breakdown
cat_breakdown = stats.get("categories_breakdown", {})
if cat_breakdown:
    st.markdown("##### 📁 Schemes by Sector")
    cat_cols = st.columns(len(cat_breakdown))
    for idx, (cat_name, count) in enumerate(cat_breakdown.items()):
        cat_cols[idx % len(cat_cols)].metric(cat_name, count)

st.divider()

# Administrative Actions Tabs
tab_index, tab_import, tab_catalog = st.tabs([
    "⚡ FAISS Vector Index Management",
    "📥 Bulk JSON Scheme Ingestion",
    "📚 Active Catalog Inspection",
])

with tab_index:
    st.subheader("Rebuild Multilingual FAISS Index")
    st.markdown(
        """
        Re-indexes all active schemes into the local FAISS dense vector store using multilingual embeddings.
        Run this after importing new schemes or updating descriptions/rules.
        """
    )
    if st.button("🚀 Trigger Full FAISS Rebuild", type="primary"):
        with st.spinner("Rebuilding FAISS vector index and BM25 representations..."):
            rebuild_res = APIClient.rebuild_index(st.session_state.admin_api_key)
            if rebuild_res.get("success"):
                st.success(f"Index rebuilt successfully: {rebuild_res.get('message')}")
                st.rerun()
            else:
                st.error(f"Rebuild failed: {rebuild_res.get('message')}")

with tab_import:
    st.subheader("Validated Batch Scheme Ingestion")
    st.markdown("Upload a JSON file containing verified government schemes formatted according to the schema.")
    
    uploaded_file = st.file_uploader("Upload Scheme JSON", type=["json"])
    overwrite_toggle = st.checkbox("Overwrite Existing Scheme Records (if IDs match)", value=True)

    if uploaded_file is not None:
        try:
            content = json.load(uploaded_file)
            schemes_list = content if isinstance(content, list) else [content]
            st.info(f"Loaded {len(schemes_list)} scheme record(s) from uploaded file.")

            if st.button("Commit Ingestion to Database"):
                with st.spinner("Validating and inserting records..."):
                    report = APIClient.import_schemes(schemes_list, overwrite=overwrite_toggle, api_key=st.session_state.admin_api_key)
                    st.success(
                        f"Import Completed: {report.get('total_imported', 0)} created, "
                        f"{report.get('total_updated', 0)} updated out of {report.get('total_received', 0)} received."
                    )
                    if report.get("errors"):
                        st.warning("Encountered notices:")
                        for err in report["errors"]:
                            st.write(f"- {err}")
                    st.rerun()
        except Exception as e:
            st.error(f"Failed to parse JSON file: {e}")

with tab_catalog:
    st.subheader("Curated Catalog Inspection")
    res = APIClient.list_schemes(page_size=50)
    for s in res.get("items", []):
        with st.expander(f"{s['name']} [{s['scheme_id']}] — {s['category']}"):
            st.write(f"**Department:** {s['department']}")
            st.write(f"**Official Source:** {s.get('source_title')}")
            st.write(f"**Last Verified:** {s.get('last_verified_date')}")
            st.write(f"**Official Link:** {s.get('official_portal_url')}")
            st.write(f"**Benefits:** {s.get('benefits_summary')}")
