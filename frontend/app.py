"""
Streamlit Main Application — Home / Conversational Scheme Assistant.
Provides conversational discovery, real-time profile extraction, three-state eligibility explanations,
and adaptive follow-up questions in English and Kannada.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path for direct `streamlit run frontend/app.py` execution
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import uuid
import streamlit as st
from frontend.services.api_client import APIClient
from frontend.components.chat_ui import render_profile_pills, render_follow_up_banner
from frontend.components.scheme_cards import render_scheme_card

# Page configuration
st.set_page_config(
    page_title="Multilingual Government Scheme Assistant",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
css_path = Path(__file__).resolve().parent / "styles" / "main.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_profile" not in st.session_state:
    st.session_state.current_profile = {}
if "language" not in st.session_state:
    st.session_state.language = "en"
if "last_follow_up" not in st.session_state:
    st.session_state.last_follow_up = None
if "last_target_attr" not in st.session_state:
    st.session_state.last_target_attr = None

# Sidebar Controls
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg",
        width=70,
    )
    st.title("Settings & Session")

    # Language Selector
    lang_choice = st.selectbox(
        "🌐 Response Language",
        options=["English", "ಕನ್ನಡ (Kannada)"],
        index=0 if st.session_state.language == "en" else 1,
    )
    st.session_state.language = "kn" if "Kannada" in lang_choice else "en"

    st.divider()

    # Session Profile Display
    render_profile_pills(st.session_state.current_profile)

    if st.button("🔄 Reset Conversation / Profile", use_container_width=True):
        st.session_state.conversation_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.current_profile = {}
        st.session_state.last_follow_up = None
        st.session_state.last_target_attr = None
        APIClient.check_health()
        st.rerun()

    st.divider()

    # System Status Indicator
    health = APIClient.check_health()
    if health.get("status") == "healthy":
        st.success(f"Backend API: Connected\nFAISS Records: {health.get('components', {}).get('vector_search', {}).get('indexed_records', 0)}")
    else:
        st.warning(f"Backend API: {health.get('status', 'offline')}")

    st.caption("Multilingual Govt Scheme Assistant v1.0.0\nAcademic NLP Project")

# Main Page Header
st.markdown(
    """
    <div class="app-header">
        <h1>🇮🇳 Multilingual Government Scheme Assistant</h1>
        <p>Discover Central & Karnataka State welfare programs with transparent three-state eligibility reasoning (PASS, FAIL, UNKNOWN).</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Suggested Query Quick Prompts
st.markdown("##### 💡 Example Queries (Click to try):")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🚜 Farmer in Karnataka (Age 28, Income 1.5L)"):
        st.session_state.preset_prompt = "I am a 28 year old farmer living in Karnataka with annual income of 1.5 lakh. Which schemes am I eligible for?"
with col2:
    if st.button("🎓 ಕರ್ನಾಟಕ ನಿರುದ್ಯೋಗಿ ಯುವಕ (Yuva Nidhi)"):
        st.session_state.preset_prompt = "ನಾನು ಕರ್ನಾಟಕದ ಪದವೀಧರ, 6 ತಿಂಗಳಿಂದ ಕೆಲಸವಿಲ್ಲ. ನನಗೆ ಸಿಗುವ ಸರ್ಕಾರಿ ಯೋಜನೆ ತಿಳಿಸಿ."
with col3:
    if st.button("🏥 Low Income Family Health Insurance"):
        st.session_state.preset_prompt = "What healthcare or hospital insurance scheme is available for a poor family with income below 2.5 lakh?"

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "recommended_schemes" in msg and msg["recommended_schemes"]:
            with st.expander(f"📋 Verified Schemes Breakdown ({len(msg['recommended_schemes'])})", expanded=True):
                for res in msg["recommended_schemes"][:4]:
                    render_scheme_card(res)

        if "near_miss_schemes" in msg and msg["near_miss_schemes"]:
            with st.expander(f"💡 Near-Miss Alternatives ({len(msg['near_miss_schemes'])})", expanded=True):
                for alt in msg["near_miss_schemes"]:
                    render_scheme_card(alt)

# Active Follow-Up Question Banner
if st.session_state.last_follow_up:
    render_follow_up_banner(
        st.session_state.last_follow_up, st.session_state.last_target_attr
    )

# Chat Input Area
prompt = st.chat_input("Describe your circumstances or ask about government schemes (in English or ಕನ್ನಡ)...")
if "preset_prompt" in st.session_state and st.session_state.preset_prompt:
    prompt = st.session_state.preset_prompt
    st.session_state.preset_prompt = None

if prompt:
    # 1. Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call Backend API
    with st.chat_message("assistant"):
        with st.spinner("Analyzing query, extracting profile, and evaluating eligibility rules..."):
            response = APIClient.send_chat_message(
                message=prompt,
                conversation_id=st.session_state.conversation_id,
                language=st.session_state.language,
                current_profile=st.session_state.current_profile,
            )

            # Update session state with accumulated profile
            if response.get("updated_profile"):
                st.session_state.current_profile = response["updated_profile"]

            reply_text = response.get("reply", "No response generated.")
            st.markdown(reply_text)

            rec_schemes = response.get("recommended_schemes", [])
            near_misses = response.get("near_miss_schemes", [])

            # Render Scheme Cards
            if rec_schemes:
                with st.expander(f"📋 Scheme Evaluation Cards ({len(rec_schemes)})", expanded=True):
                    for r in rec_schemes[:4]:
                        render_scheme_card(r)

            if near_misses:
                with st.expander(f"💡 Alternative Scheme Options ({len(near_misses)})", expanded=True):
                    for alt in near_misses:
                        render_scheme_card(alt)

            # Update follow-up status
            st.session_state.last_follow_up = response.get("follow_up_question")
            st.session_state.last_target_attr = response.get("follow_up_target_attribute")

            # Save in message history
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply_text,
                "recommended_schemes": rec_schemes,
                "near_miss_schemes": near_misses,
            })

    st.rerun()

# Disclaimer Footer
st.markdown(
    """
    <div class="disclaimer-banner">
        <strong>Official Disclaimer:</strong> Recommendations generated by this assistant are for informational discovery purposes.
        Eligibility conditions and benefit awards are determined solely by the respective government ministries and official authorities.
        Information is verified against official sources including <em>myscheme.gov.in</em>, <em>scholarships.gov.in</em>, and <em>sevasindhu.karnataka.gov.in</em>.
    </div>
    """,
    unsafe_allow_html=True,
)
