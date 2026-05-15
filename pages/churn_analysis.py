# pages/churn_analysis.py
# ─────────────────────────────────────────────────────────────
# Churn Analysis – deep-dive churn metrics across all dimensions
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ui_helpers import (
    page_header, section_title, insight, warning_box, build_sidebar_filters,
)
from utils.data_loader import apply_filters
from utils.charts import (
    churn_pie, churn_by_geography, churn_heatmap,
    segment_churn_bar, gender_churn_comparison,
    products_churn_bar, age_distribution,
    balance_distribution, tenure_churn_line,
    revenue_risk_treemap, active_churn_funnel,
)
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
        "📉 Churn Analysis",
        "Comprehensive churn pattern investigation: who churns, where, and why",
    )

    # ── Top metrics row ───────────────────────────────────────
    total   = len(df)
    churned = df["Exited"].sum()
    retained= total - churned
    cr      = churned / total * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Churn Rate", f"{cr:.2f}%")
    c2.metric("Churned Customers",  f"{churned:,}")
    c3.metric("Retained Customers", f"{retained:,}")
    c4.metric("Revenue Risk",       f"€{df['RevenueRisk'].sum()/1e6:.2f}M")

    # ── Overall churn split ───────────────────────────────────
    section_title("Overall Churn Distribution")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(churn_pie(df), use_container_width=True)
    with col2:
        st.plotly_chart(churn_by_geography(df), use_container_width=True)

    # ── Heatmap: age × geography ──────────────────────────────
    section_title("Churn Rate Heatmap — Age Group × Country")
    st.plotly_chart(churn_heatmap(df), use_container_width=True)
    insight(
        "Germany consistently shows elevated churn rates across age groups, "
        "especially in the 45–54 bracket. France retains customers best in younger cohorts."
    )

    # ── Gender analysis ───────────────────────────────────────
    section_title("Gender-wise Churn Analysis")
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(gender_churn_comparison(df), use_container_width=True)
    with col4:
        st.plotly_chart(segment_churn_bar(df, "Gender", "Churn Rate by Gender"),
                        use_container_width=True)

    gender_churn = (
        df.groupby("Gender")["Exited"].mean() * 100
    ).reset_index()
    gender_churn.columns = ["Gender", "ChurnRate"]
    top_gender = gender_churn.loc[gender_churn["ChurnRate"].idxmax()]
    insight(
        f"<strong>{top_gender['Gender']}</strong> customers churn at "
        f"<strong>{top_gender['ChurnRate']:.1f}%</strong> — noticeably higher than the other "
        f"gender segment. Tailored products and communication could address this gap."
    )

    # ── Age group churn ───────────────────────────────────────
    section_title("Age Group Churn Analysis")
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(age_distribution(df), use_container_width=True)
    with col6:
        st.plotly_chart(segment_churn_bar(df, "AgeGroup", "Churn Rate by Age Group"),
                        use_container_width=True)

    # ── Products churn ────────────────────────────────────────
    section_title("Products Held vs Churn")
    st.plotly_chart(products_churn_bar(df), use_container_width=True)
    warning_box(
        "Customers with <strong>3–4 products</strong> show dramatically higher churn "
        "despite higher product penetration. This counter-intuitive pattern may signal "
        "product complexity or poor cross-sell fit — needs further investigation."
    )

    # ── Balance segment churn ─────────────────────────────────
    section_title("Balance Segment Churn")
    col7, col8 = st.columns(2)
    with col7:
        st.plotly_chart(balance_distribution(df), use_container_width=True)
    with col8:
        st.plotly_chart(segment_churn_bar(df, "BalanceSegment", "Churn by Balance Tier"),
                        use_container_width=True)

    # ── Tenure churn line ─────────────────────────────────────
    section_title("Tenure vs Churn Rate")
    st.plotly_chart(tenure_churn_line(df), use_container_width=True)

    # ── Active vs inactive ────────────────────────────────────
    section_title("Active vs Inactive Member Churn")
    col9, col10 = st.columns(2)
    with col9:
        st.plotly_chart(active_churn_funnel(df), use_container_width=True)
    with col10:
        active_churn = (
            df.groupby("ActiveStatus")["Exited"]
            .agg(["mean", "count"])
            .rename(columns={"mean": "ChurnRate", "count": "Count"})
            .reset_index()
        )
        active_churn["ChurnRate"] *= 100
        fig_ac = px.bar(
            active_churn, x="ActiveStatus", y="ChurnRate",
            color="ActiveStatus",
            color_discrete_map={"Active": COLORS["success"], "Inactive": COLORS["danger"]},
            text=active_churn["ChurnRate"].round(1).astype(str) + "%",
            template=PLOTLY_TEMPLATE,
        )
        fig_ac.update_traces(textposition="outside")
        fig_ac.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(fig_ac, use_container_width=True)

    insight(
        "Inactive members churn at a rate <strong>2–3× higher</strong> than active "
        "members. Re-engagement campaigns (push notifications, loyalty points, "
        "personalised offers) can deliver fast ROI."
    )

    # ── Revenue risk treemap ──────────────────────────────────
    section_title("Revenue Risk Map (Churned Customers)")
    if df["Exited"].sum() > 0:
        st.plotly_chart(revenue_risk_treemap(df), use_container_width=True)
    else:
        st.info("No churned customers in the filtered set.")

    # ── Credit band churn ─────────────────────────────────────
    section_title("Credit Score Band vs Churn")
    st.plotly_chart(
        segment_churn_bar(df, "CreditBand", "Churn Rate by Credit Band"),
        use_container_width=True,
    )

    # ── Country-level churn table ─────────────────────────────
    section_title("Country-Level Churn Summary")
    geo_summary = (
        df.groupby("Geography")
        .agg(
            Total=("Exited", "count"),
            Churned=("Exited", "sum"),
            AvgBalance=("Balance", "mean"),
            AvgCredit=("CreditScore", "mean"),
            RevenueRisk=("RevenueRisk", "sum"),
        )
        .reset_index()
    )
    geo_summary["ChurnRate%"]    = (geo_summary["Churned"] / geo_summary["Total"] * 100).round(2)
    geo_summary["AvgBalance"]    = geo_summary["AvgBalance"].round(0)
    geo_summary["AvgCredit"]     = geo_summary["AvgCredit"].round(0)
    geo_summary["RevenueRisk€M"] = (geo_summary["RevenueRisk"] / 1e6).round(3)
    geo_summary = geo_summary.drop(columns=["RevenueRisk"])

    st.dataframe(
        geo_summary.style.background_gradient(subset=["ChurnRate%"], cmap="RdYlGn_r"),
        use_container_width=True,
    )
