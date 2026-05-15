# utils/ui_helpers.py
# ─────────────────────────────────────────────────────────────
# Shared UI components: CSS injection, sidebar, KPI cards
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
from config.settings import COLORS, AGE_LABELS, CREDIT_LABELS, APP_TITLE, APP_ICON


# ── Global CSS ────────────────────────────────────────────────

CUSTOM_CSS = f"""
<style>
/* ── Import Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root & Body ── */
:root {{
    --primary:   {COLORS['primary']};
    --secondary: {COLORS['secondary']};
    --accent:    {COLORS['accent']};
    --danger:    {COLORS['danger']};
    --success:   {COLORS['success']};
    --neutral:   {COLORS['neutral']};
    --bg-dark:   {COLORS['bg_dark']};
    --bg-card:   {COLORS['bg_card']};
    --text:      {COLORS['text_light']};
    --text-muted:{COLORS['text_muted']};
}}

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-dark) !important;
    color: var(--text) !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0F1B2D 0%, #1A2A40 100%) !important;
    border-right: 1px solid rgba(46,134,171,0.25) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--text) !important; }}

/* ── Main content area ── */
.main .block-container {{
    padding: 1.5rem 2rem 2rem 2rem !important;
    max-width: 1400px;
}}

/* ── Page header banner ── */
.page-header {{
    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.5rem;
    border-left: 5px solid {COLORS['accent']};
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
}}
.page-header h1 {{
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 0 !important;
}}
.page-header p {{
    font-size: 0.9rem;
    color: rgba(255,255,255,0.75);
    margin: 0.3rem 0 0 0;
}}

/* ── KPI Cards ── */
.kpi-card {{
    background: linear-gradient(145deg, var(--bg-card), #243347);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    border: 1px solid rgba(46,134,171,0.2);
    box-shadow: 0 3px 15px rgba(0,0,0,0.3);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 0.6rem;
}}
.kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
}}
.kpi-label {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
}}
.kpi-value {{
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}}
.kpi-delta {{
    font-size: 0.78rem;
    margin-top: 0.25rem;
    color: var(--text-muted);
}}

/* ── Section divider ── */
.section-title {{
    font-size: 1.05rem;
    font-weight: 600;
    color: {COLORS['secondary']};
    padding: 0.25rem 0;
    border-bottom: 2px solid {COLORS['secondary']};
    margin: 1.2rem 0 0.75rem 0;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}

/* ── Insight box ── */
.insight-box {{
    background: rgba(46,134,171,0.12);
    border: 1px solid rgba(46,134,171,0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
    font-size: 0.88rem;
    line-height: 1.6;
}}
.insight-box strong {{
    color: {COLORS['accent']};
}}

/* ── Alert / recommendation box ── */
.rec-box {{
    background: rgba(230,57,70,0.1);
    border: 1px solid rgba(230,57,70,0.35);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
    font-size: 0.88rem;
    line-height: 1.6;
}}
.rec-box strong {{ color: {COLORS['danger']}; }}

.good-box {{
    background: rgba(45,198,83,0.1);
    border: 1px solid rgba(45,198,83,0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
    font-size: 0.88rem;
    line-height: 1.6;
}}
.good-box strong {{ color: {COLORS['success']}; }}

/* ── DataFrame table ── */
.dataframe {{ font-size: 0.82rem !important; }}

/* ── Plotly chart container ── */
.stPlotlyChart {{ border-radius: 10px; overflow: hidden; }}

/* ── Streamlit metric ── */
[data-testid="metric-container"] {{
    background: var(--bg-card) !important;
    border: 1px solid rgba(46,134,171,0.2) !important;
    border-radius: 10px !important;
    padding: 0.8rem !important;
}}
[data-testid="stMetricValue"] {{
    color: {COLORS['accent']} !important;
    font-size: 1.6rem !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-dark); }}
::-webkit-scrollbar-thumb {{ background: var(--secondary); border-radius: 3px; }}
</style>
"""


def inject_css():
    """Inject custom CSS once per page render."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Page header ───────────────────────────────────────────────

def page_header(title: str, subtitle: str = ""):
    html = f"""
    <div class="page-header">
        <h1>{title}</h1>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ── Section label ─────────────────────────────────────────────

def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


# ── KPI card ─────────────────────────────────────────────────

def kpi_card(label: str, value: str, delta: str = ""):
    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-delta'>" + delta + "</div>" if delta else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ── Insight/Rec boxes ─────────────────────────────────────────

def insight(text: str):
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)

def warning_box(text: str):
    st.markdown(f'<div class="rec-box">⚠️ {text}</div>', unsafe_allow_html=True)

def success_box(text: str):
    st.markdown(f'<div class="good-box">✅ {text}</div>', unsafe_allow_html=True)


# ── Sidebar filters ───────────────────────────────────────────

def build_sidebar_filters(df: pd.DataFrame) -> dict:
    """
    Render sidebar filter widgets and return a dict of selected values.
    Call this from every page to get a consistent filter set.
    """
    with st.sidebar:
        st.markdown(
            f"<h2 style='color:{COLORS['accent']};margin-bottom:0.1rem'>🏦 BankIQ</h2>"
            f"<p style='color:{COLORS['text_muted']};font-size:0.75rem;margin-top:0'>European Banking Analytics</p>",
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("### 🔎 Filters")

        # Geography
        geo_options = sorted(df["Geography"].dropna().unique().tolist())
        geo_sel = st.multiselect(
            "🌍 Country",
            options=geo_options,
            default=geo_options,
            help="Select one or more countries",
        )

        # Gender
        gender_options = sorted(df["Gender"].dropna().unique().tolist())
        gender_sel = st.multiselect(
            "👤 Gender",
            options=gender_options,
            default=gender_options,
        )

        # Age group
        age_options = [a for a in AGE_LABELS if a in df["AgeGroup"].unique()]
        age_sel = st.multiselect(
            "🎂 Age Group",
            options=age_options,
            default=age_options,
        )

        # Balance range
        bal_min = int(df["Balance"].min())
        bal_max = int(df["Balance"].max())
        bal_sel = st.slider(
            "💶 Balance Range (EUR)",
            min_value=bal_min,
            max_value=bal_max,
            value=(bal_min, bal_max),
            step=5_000,
            format="€%d",
        )

        # Credit band
        cb_options = [c for c in CREDIT_LABELS if c in df["CreditBand"].unique()]
        cb_sel = st.multiselect(
            "💳 Credit Band",
            options=cb_options,
            default=cb_options,
        )

        st.divider()
        st.markdown(
            f"<p style='color:{COLORS['text_muted']};font-size:0.72rem;text-align:center'>"
            f"BankIQ Analytics v1.0.0<br>Data refreshed on upload</p>",
            unsafe_allow_html=True,
        )

    return dict(
        geographies=geo_sel,
        genders=gender_sel,
        age_groups=age_sel,
        balance_range=bal_sel,
        credit_bands=cb_sel,
    )
