# pages/kpi_dashboard.py
# ─────────────────────────────────────────────────────────────
# KPI Dashboard – single-screen executive scorecard
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.ui_helpers import page_header, section_title, kpi_card, insight, build_sidebar_filters
from utils.data_loader import apply_filters
from utils.charts import kpi_data, churn_pie, churn_by_geography, tenure_churn_line
from config.settings import COLORS, PLOTLY_TEMPLATE


def render():
    if "df_raw" not in st.session_state:
        st.info("📂 Please upload your dataset via the sidebar.")
        return

    df_raw = st.session_state["df_raw"]
    filters = build_sidebar_filters(df_raw)
    df = apply_filters(df_raw, **filters)

    if df.empty:
        st.warning("No data matches the selected filters.")
        return

    page_header(
        "📊 KPI Dashboard",
        "Executive scorecard — all critical performance indicators at a glance",
    )

    kpis = kpi_data(df)

    # ── Row 1: Primary KPIs ───────────────────────────────────
    section_title("Customer Health KPIs")
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    pairs = [
        (c1, "Total Customers",   f"{kpis['total']:,}",              ""),
        (c2, "Churned",           f"{kpis['churned']:,}",             "⚠️"),
        (c3, "Retained",          f"{kpis['retained']:,}",            "✅"),
        (c4, "Churn Rate",        f"{kpis['churn_rate']:.2f}%",       ""),
        (c5, "Active Rate",       f"{kpis['active_pct']:.1f}%",       ""),
        (c6, "High-Value",        f"{kpis['high_value']:,}",          "💎"),
        (c7, "Revenue Risk",      f"€{kpis['revenue_risk']/1e6:.2f}M",""),
    ]
    for col, label, value, delta in pairs:
        with col:
            kpi_card(label, value, delta)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Financial KPIs ─────────────────────────────────
    section_title("Financial KPIs")
    f1, f2, f3, f4 = st.columns(4)
    with f1: kpi_card("Avg Balance",          f"€{kpis['avg_balance']:,.0f}")
    with f2: kpi_card("Avg Credit Score",     f"{kpis['avg_credit']:.0f}")
    with f3: kpi_card("Avg Age",              f"{kpis['avg_age']:.1f} yrs")
    with f4: kpi_card("Active Members",       f"{kpis['active']:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauge charts ──────────────────────────────────────────
    section_title("Gauge Indicators")
    g1, g2, g3 = st.columns(3)

    with g1:
        fig_g1 = _gauge(
            value=kpis["churn_rate"],
            title="Churn Rate %",
            max_val=50,
            threshold=20,
            color=COLORS["danger"],
        )
        st.plotly_chart(fig_g1, use_container_width=True)

    with g2:
        fig_g2 = _gauge(
            value=kpis["active_pct"],
            title="Active Member %",
            max_val=100,
            threshold=60,
            color=COLORS["success"],
            reverse=True,
        )
        st.plotly_chart(fig_g2, use_container_width=True)

    with g3:
        hv_share = kpis["high_value"] / kpis["total"] * 100 if kpis["total"] else 0
        fig_g3 = _gauge(
            value=hv_share,
            title="High-Value Share %",
            max_val=100,
            threshold=20,
            color=COLORS["accent"],
            reverse=True,
        )
        st.plotly_chart(fig_g3, use_container_width=True)

    # ── Comparative charts ────────────────────────────────────
    section_title("Segment Performance Matrix")
    col1, col2 = st.columns(2)

    with col1:
        # Churn rate by geography grouped bar
        geo_data = (
            df.groupby(["Geography", "ChurnLabel"])
            .size()
            .reset_index(name="Count")
        )
        fig_geo = px.bar(
            geo_data, x="Geography", y="Count", color="ChurnLabel",
            barmode="group",
            color_discrete_map={"Retained": COLORS["success"], "Churned": COLORS["danger"]},
            template=PLOTLY_TEMPLATE,
            title="Retained vs Churned by Country",
        )
        fig_geo.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    with col2:
        # Pie
        st.plotly_chart(churn_pie(df), use_container_width=True)

    # ── Tenure trend ──────────────────────────────────────────
    section_title("Churn Trend by Tenure")
    st.plotly_chart(tenure_churn_line(df), use_container_width=True)

    # ── Segment KPI table ─────────────────────────────────────
    section_title("Segment KPI Table")
    seg_kpi = (
        df.groupby("Geography")
        .agg(
            Customers=("Exited", "count"),
            Churned=("Exited", "sum"),
            AvgBalance=("Balance", "mean"),
            AvgCreditScore=("CreditScore", "mean"),
            ActiveMembers=("IsActiveMember", "sum"),
            HighValueCount=("IsHighValue", "sum"),
            RevenueRiskEUR=("RevenueRisk", "sum"),
        )
        .reset_index()
    )
    seg_kpi["ChurnRate%"]   = (seg_kpi["Churned"] / seg_kpi["Customers"] * 100).round(2)
    seg_kpi["ActiveRate%"]  = (seg_kpi["ActiveMembers"] / seg_kpi["Customers"] * 100).round(1)
    seg_kpi["AvgBalance"]   = seg_kpi["AvgBalance"].round(0)
    seg_kpi["AvgCreditScore"]= seg_kpi["AvgCreditScore"].round(0)
    seg_kpi["RevenueRisk€M"]= (seg_kpi["RevenueRiskEUR"] / 1e6).round(3)
    seg_kpi = seg_kpi.drop(columns=["RevenueRiskEUR"])

    st.dataframe(
        seg_kpi.style
            .background_gradient(subset=["ChurnRate%"], cmap="RdYlGn_r")
            .background_gradient(subset=["ActiveRate%"], cmap="RdYlGn")
            .format({"AvgBalance": "€{:,.0f}", "AvgCreditScore": "{:.0f}"}),
        use_container_width=True,
    )

    insight(
        "Use this KPI table to benchmark each country against overall targets. "
        "Flag countries where <strong>ChurnRate%</strong> exceeds 20% or "
        "<strong>ActiveRate%</strong> falls below 50% for immediate intervention."
    )

    # ── Insight summary block ─────────────────────────────────
    section_title("Executive Summary")
    st.markdown(
        f"""
        <div style="background:{COLORS['bg_card']};border-radius:12px;padding:1.4rem 1.8rem;
                    border-left:4px solid {COLORS['accent']};line-height:1.9;font-size:0.9rem;">
            <p>📌 <strong>Overall Churn Rate:</strong> {kpis['churn_rate']:.2f}% across
            {kpis['total']:,} customers. Industry benchmark is 10–15% for European retail banks.</p>
            <p>📌 <strong>Active Membership:</strong> {kpis['active_pct']:.1f}% of customers
            are active members — a strong predictor of retention.</p>
            <p>📌 <strong>High-Value Exposure:</strong> {kpis['high_value']:,} customers
            hold balances above €{100_000:,}, creating concentrated revenue risk of
            €{kpis['revenue_risk']/1e6:.2f}M if they churn.</p>
            <p>📌 <strong>Priority Action:</strong> Deploy personalised retention outreach
            to inactive high-value customers immediately.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Gauge helper ──────────────────────────────────────────────

def _gauge(value, title, max_val, threshold, color, reverse=False):
    """Create a Plotly gauge chart."""
    if reverse:
        bar_color = COLORS["success"] if value >= threshold else COLORS["danger"]
    else:
        bar_color = COLORS["danger"] if value >= threshold else COLORS["success"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        number={"suffix": "%", "font": {"size": 22}},
        gauge=dict(
            axis=dict(range=[0, max_val], tickwidth=1),
            bar=dict(color=bar_color),
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor="rgba(255,255,255,0.1)",
            steps=[
                dict(range=[0, threshold], color="rgba(45,198,83,0.15)"),
                dict(range=[threshold, max_val], color="rgba(230,57,70,0.15)"),
            ],
            threshold=dict(
                line=dict(color="white", width=2),
                thickness=0.75,
                value=threshold,
            ),
        ),
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(t=40, b=10, l=20, r=20),
    )
    return fig
