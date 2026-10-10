import streamlit as st
import os

# ==============================================================================
# MAIN APPLICATION ENTRYPOINT
# AI-Based Risk Mapping and Interactive Dashboard for Child Health Outcomes (NFHS-5)
# ==============================================================================

st.set_page_config(
    page_title="AI Child Health Risk Dashboard | NFHS-5",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom sidebar branding and metadata
with st.sidebar:
    st.markdown("## 👶 Child Health Risk AI")
    st.markdown("**NFHS-5 District Vulnerability Platform**")
    st.caption("707 Districts · 36 States & UTs · 12 Indicators")
    st.markdown("---")

# Navigation setup using modern Streamlit multi-page API
current_dir = os.path.dirname(os.path.abspath(__file__))

district_page = st.Page(
    os.path.join(current_dir, "pages", "1_District_Explorer.py"),
    title="District Explorer",
    icon="🔍",
    default=True
)

state_page = st.Page(
    os.path.join(current_dir, "pages", "2_State_Overview.py"),
    title="State Overview",
    icon="📊"
)

about_page = st.Page(
    os.path.join(current_dir, "pages", "3_About_and_Methodology.py"),
    title="About / Methodology",
    icon="ℹ️"
)

# Configure navigation
pg = st.navigation(
    {
        "Explore": [district_page, state_page],
        "Documentation": [about_page],
    }
)

# Sidebar footer
with st.sidebar:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("🎓 Final-Year Capstone Project")
    st.caption("Data Source: NFHS-5 (2019-21), MoHFW / IIPS")

pg.run()
