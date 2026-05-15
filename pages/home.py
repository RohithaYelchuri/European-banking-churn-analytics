# pages/home.py
# ─────────────────────────────────────────────────────────────
# Home Dashboard – executive overview
# ─────────────────────────────────────────────────────────────

import streamlit as st
import plotly.graph_objects as go
from utils.ui_helpers import (
    page_header, section_title, kpi_card, insight,
    warning_box, success_box, build_sidebar_filters,
)
from utils.data_loader import apply_filters
from utils.charts import (
    kpi_data, churn_pie, churn_by_geography,
    segment_churn_bar, balance_distribution,
)
from config.settings import COLORS


def render():
    # ── Guard: no data yet ────────────────────────────────────
    if "df_raw" not in st.session_state:
        _show_landing()
        return

    df_raw = st.session_state["df_raw"]
    filters = build_sidebar_filters(df_raw)
    df = apply_filters(df_raw, **filters)

    if df.empty:
        st.warning("No customers match the selected filters.")
        return

    # ── Header ────────────────────────────────────────────────
    page_header(
        "🏠 Executive Dashboard",
        "Real-time customer segmentation & churn intelligence across European markets",
    )

    # ── Top-level KPIs ────────────────────────────────────────
    kpis = kpi_data(df)
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        kpi_card("Total Customers", f"{kpis['total']:,}")
    with c2:
        kpi_card("Churned", f"{kpis['churned']:,}", "⚠️ at risk")
    with c3:
        kpi_card("Churn Rate", f"{kpis['churn_rate']:.1f}%")
    with c4:
        kpi_card("Avg Balance", f"€{kpis['avg_balance']:,.0f}")
    with c5:
        kpi_card("High-Value", f"{kpis['high_value']:,}")
    with c6:
        kpi_card("Revenue Risk", f"€{kpis['revenue_risk']/1e6:.2f}M", "estimated annual")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Churn pie + Geography bar ─────────────────────
    section_title("Churn Overview")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("##### Overall Churn Split")
        st.plotly_chart(churn_pie(df), use_container_width=True)

    with col2:
        st.markdown("##### Churn by Country")
        st.plotly_chart(churn_by_geography(df), use_container_width=True)

    # ── Row 2: Age-group churn + Balance dist ─────────────────
    section_title("Segment Snapshot")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("##### Churn Rate by Age Group")
        st.plotly_chart(segment_churn_bar(df, "AgeGroup"), use_container_width=True)

    with col4:
        st.markdown("##### Balance Distribution")
        st.plotly_chart(balance_distribution(df), use_container_width=True)

    # ── Insight boxes ─────────────────────────────────────────
    section_title("Key Findings")
    col5, col6 = st.columns(2)

    churn_rt = kpis["churn_rate"]
    rev_risk = kpis["revenue_risk"]

    with col5:
        insight(
            f"<strong>{churn_rt:.1f}%</strong> overall churn rate across "
            f"<strong>{kpis['total']:,}</strong> filtered customers. "
            f"Industry benchmark is typically 10–15% for retail banking."
        )
        insight(
            f"<strong>{kpis['high_value']:,}</strong> high-value customers "
            f"(balance ≥ €100K) represent disproportionate revenue concentration."
        )

    with col6:
        warning_box(
            f"<strong>Estimated annual revenue risk: €{rev_risk/1e6:.2f}M</strong> "
            f"based on a 1.5% fee proxy on churned balances. "
            f"Immediate retention campaigns are advised."
        )
        success_box(
            f"<strong>{kpis['active_pct']:.1f}%</strong> active membership rate. "
            f"Active members churn at significantly lower rates — engagement is your "
            f"most powerful retention lever."
        )


# ── Landing (no data) ──────────────────────────────────────────

def _show_landing():
    st.markdown(
        f"""
        <div style="text-align:center;padding:3rem 1rem;">
            <div style="font-size:5rem">🏦</div>
            <h1 style="color:{COLORS['accent']};font-size:2.2rem;margin-top:0.5rem">
                BankIQ Analytics
            </h1>
            <p style="color:{COLORS['text_muted']};font-size:1.05rem;max-width:560px;margin:0.8rem auto 2rem">
                Customer Segmentation & Churn Pattern Analytics for European Banking.
                Upload your Excel dataset via the sidebar to begin.
            </p>
            <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;">
                {"".join(_feature_card(icon, label) for icon, label in [
                    ("📊","7 Analytics Pages"),
                    ("🔎","Sidebar Filters"),
                    ("💡","AI Insights"),
                    ("📈","Interactive Charts"),
                ])}
            </div>
            <br>
            <p style="color:{COLORS['text_muted']};font-size:0.85rem">
                ← Upload your <code>bank_churn.xlsx</code> file in the sidebar to get started
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _feature_card(icon, label):
    return (
        f"<div style='background:{COLORS['bg_card']};border:1px solid "
        f"rgba(46,134,171,0.25);border-radius:12px;padding:1.2rem 1.6rem;"
        f"min-width:130px;'>"
        f"<div style='font-size:2rem'>{icon}</div>"
        f"<div style='color:{COLORS['text_light']};font-size:0.85rem;"
        f"margin-top:0.4rem;font-weight:600'>{label}</div>"
        f"</div>"
    )
