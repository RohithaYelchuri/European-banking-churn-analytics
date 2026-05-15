# pages/segmentation.py
# ─────────────────────────────────────────────────────────────
# Customer Segmentation page
# ─────────────────────────────────────────────────────────────

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.ui_helpers import page_header, section_title, insight, build_sidebar_filters
from utils.data_loader import apply_filters
from utils.charts import (
    balance_segment_pie, credit_band_bar,
    segment_churn_bar, active_churn_funnel,
    high_value_radar,
)
from config.settings import COLORS, PLOTLY_TEMPLATE, SEGMENT_SEQ


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
        "👥 Customer Segmentation",
        "Multi-dimensional customer profiling: geography, age, credit, balance, tenure",
    )

    # ── Quick stats ───────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Countries",      df["Geography"].nunique())
    c2.metric("Age Groups",     df["AgeGroup"].nunique())
    c3.metric("Credit Bands",   df["CreditBand"].nunique())
    c4.metric("Balance Segs",   df["BalanceSegment"].nunique())

    # ── Geography distribution ────────────────────────────────
    section_title("Geography Segmentation")
    geo = df["Geography"].value_counts().reset_index()
    geo.columns = ["Country", "Customers"]

    col1, col2 = st.columns(2)
    with col1:
        fig_geo_bar = px.bar(
            geo, x="Country", y="Customers",
            color="Country",
            color_discrete_sequence=[COLORS["secondary"], COLORS["accent"], COLORS["danger"]],
            text="Customers",
            template=PLOTLY_TEMPLATE,
        )
        fig_geo_bar.update_traces(textposition="outside")
        fig_geo_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.markdown("##### Customers by Country")
        st.plotly_chart(fig_geo_bar, use_container_width=True)

    with col2:
        fig_geo_pie = px.pie(
            geo, names="Country", values="Customers",
            color_discrete_sequence=[COLORS["secondary"], COLORS["accent"], COLORS["danger"]],
            hole=0.5,
            template=PLOTLY_TEMPLATE,
        )
        fig_geo_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=30, b=10),
        )
        st.markdown("##### Market Share by Country")
        st.plotly_chart(fig_geo_pie, use_container_width=True)

    # ── Age group segmentation ────────────────────────────────
    section_title("Age Group Segmentation")
    from config.settings import AGE_LABELS
    age_counts = (
        df["AgeGroup"].value_counts()
        .reindex([a for a in AGE_LABELS if a in df["AgeGroup"].unique()])
        .reset_index()
    )
    age_counts.columns = ["AgeGroup", "Count"]

    col3, col4 = st.columns(2)
    with col3:
        fig_age = px.bar(
            age_counts, x="AgeGroup", y="Count",
            color="Count",
            color_continuous_scale="Viridis",
            text="Count",
            template=PLOTLY_TEMPLATE,
        )
        fig_age.update_traces(textposition="outside")
        fig_age.update_coloraxes(showscale=False)
        fig_age.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.markdown("##### Customers per Age Group")
        st.plotly_chart(fig_age, use_container_width=True)

    with col4:
        st.markdown("##### Churn Rate per Age Group")
        st.plotly_chart(segment_churn_bar(df, "AgeGroup"), use_container_width=True)

    insight(
        "The <strong>45–54</strong> age cohort typically shows the highest churn "
        "propensity — these mid-career customers are often targeted by competing banks "
        "with premium products. Focus retention programs here."
    )

    # ── Credit score bands ────────────────────────────────────
    section_title("Credit Score Segmentation")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("##### Distribution by Credit Band")
        st.plotly_chart(credit_band_bar(df), use_container_width=True)
    with col6:
        st.markdown("##### Churn Rate by Credit Band")
        st.plotly_chart(segment_churn_bar(df, "CreditBand"), use_container_width=True)

    # ── Balance segments ──────────────────────────────────────
    section_title("Balance Segmentation")
    col7, col8 = st.columns(2)
    with col7:
        st.markdown("##### Balance Segment Share")
        st.plotly_chart(balance_segment_pie(df), use_container_width=True)
    with col8:
        st.markdown("##### Churn Rate by Balance Segment")
        st.plotly_chart(segment_churn_bar(df, "BalanceSegment"), use_container_width=True)

    # ── Tenure segments ───────────────────────────────────────
    section_title("Tenure Segmentation")
    col9, col10 = st.columns(2)
    with col9:
        tenure_counts = df["TenureSegment"].value_counts().reset_index()
        tenure_counts.columns = ["Segment", "Count"]
        fig_ten = px.bar(
            tenure_counts, x="Segment", y="Count",
            color_discrete_sequence=[COLORS["secondary"]],
            text="Count",
            template=PLOTLY_TEMPLATE,
        )
        fig_ten.update_traces(textposition="outside")
        fig_ten.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.markdown("##### Customers by Tenure")
        st.plotly_chart(fig_ten, use_container_width=True)

    with col10:
        st.markdown("##### Churn Rate by Tenure Band")
        st.plotly_chart(segment_churn_bar(df, "TenureSegment"), use_container_width=True)

    # ── Active vs inactive funnel ─────────────────────────────
    section_title("Active vs Inactive Members")
    col11, col12 = st.columns([1, 2])
    with col11:
        active_df = df["ActiveStatus"].value_counts().reset_index()
        active_df.columns = ["Status", "Count"]
        fig_act = px.pie(
            active_df, names="Status", values="Count",
            color="Status",
            color_discrete_map={"Active": COLORS["success"], "Inactive": COLORS["neutral"]},
            hole=0.5,
            template=PLOTLY_TEMPLATE,
        )
        fig_act.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=10),
        )
        st.markdown("##### Active vs Inactive Share")
        st.plotly_chart(fig_act, use_container_width=True)

    with col12:
        st.markdown("##### Customer Funnel")
        st.plotly_chart(active_churn_funnel(df), use_container_width=True)

    # ── Wealth tier cross-segment ─────────────────────────────
    section_title("Wealth Tier × Geography Matrix")
    pivot = (
        df.groupby(["WealthTier", "Geography"])
        .size()
        .unstack(fill_value=0)
    )
    fig_wt = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        template=PLOTLY_TEMPLATE,
        text_auto=True,
        labels=dict(color="Customers"),
    )
    fig_wt.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
    )
    st.plotly_chart(fig_wt, use_container_width=True)
