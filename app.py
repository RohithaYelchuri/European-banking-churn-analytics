# app.py
# ─────────────────────────────────────────────────────────────
# MAIN ENTRY POINT – European Banking Churn Analytics
# Run: streamlit run app.py
# ─────────────────────────────────────────────────────────────

import streamlit as st
from config.settings import APP_TITLE, APP_ICON, COLORS

# ── Page config (must be first Streamlit call) ─────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "# BankIQ Analytics\nCustomer Segmentation & Churn Pattern Analytics",
    },
)

# ── Shared state: dataset upload ──────────────────────────────
from utils.ui_helpers import inject_css
from utils.data_loader import load_data, dataset_exists

inject_css()

# ── Sidebar: file upload widget (available on every page) ─────
with st.sidebar:
    st.markdown(
        f"<h2 style='color:{COLORS['accent']};margin-bottom:0.2rem'>🏦 BankIQ</h2>"
        f"<p style='color:{COLORS['text_muted']};font-size:0.75rem;margin-top:0'>"
        f"European Banking Analytics</p>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("### 📂 Dataset")
    uploaded = st.file_uploader(
        "Upload your Excel file",
        type=["xlsx", "xls"],
        help="Upload the bank churn Excel dataset. "
             "Alternatively place it at dataset/bank_churn.xlsx",
    )

# ── Load data into session state ──────────────────────────────
if "df_raw" not in st.session_state or uploaded is not None:
    try:
        df = load_data(uploaded)
        st.session_state["df_raw"] = df
    except FileNotFoundError:
        st.session_state.pop("df_raw", None)
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        st.session_state.pop("df_raw", None)

# ── Navigation ────────────────────────────────────────────────
PAGES = {
    "🏠 Home Dashboard"          : "pages/home.py",
    "📋 Data Overview"           : "pages/data_overview.py",
    "👥 Customer Segmentation"   : "pages/segmentation.py",
    "📉 Churn Analysis"          : "pages/churn_analysis.py",
    "💎 High Value Customers"    : "pages/high_value.py",
    "📊 KPI Dashboard"           : "pages/kpi_dashboard.py",
    "💡 Recommendations"         : "pages/recommendations.py",
}

with st.sidebar:
    st.divider()
    st.markdown("### 🗺️ Navigation")
    page = st.radio(
        label="",
        options=list(PAGES.keys()),
        label_visibility="collapsed",
    )

# ── Route to selected page ────────────────────────────────────
import importlib.util, sys, os

page_file = PAGES[page]
spec = importlib.util.spec_from_file_location("page_module", page_file)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if hasattr(mod, "render"):
    mod.render()
