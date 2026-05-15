# pages/high_value.py
# ─────────────────────────────────────────────────────────────
# High-Value Customer Analysis
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ui_helpers import (
    page_header, section_title, insight, warning_box, success_box,
    kpi_card, build_sidebar_filters,
)
from utils.data_loader import apply_filters
from utils.charts import (
    high_value_radar, credit_balance_scatter, revenue_risk_treemap,
    segment_churn_bar,
)
from config.settings import COLORS, PLOTLY_TEMPLATE, HIGH_VALUE_BALANCE_THRESHOLD


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
        "💎 High-Value Customer Analysis",
        f"Deep-dive into customers with balance ≥ €{HIGH_VALUE_BALANCE_THRESHOLD:,}",
    )

    hv  = df[df["IsHighValue"] == 1]
    nhv = df[df["IsHighValue"] == 0]

    if hv.empty:
        st.warning(f"No high-value customers (Balance ≥ €{HIGH_VALUE_BALANCE_THRESHOLD:,}) in filtered set.")
        return

    # ── Summary KPIs ──────────────────────────────────────────
    hv_total   = len(hv)
    hv_churned = hv["Exited"].sum()
    hv_cr      = hv_churned / hv_total * 100 if hv_total else 0
    hv_avg_bal = hv["Balance"].mean()
    hv_rev_risk= hv["RevenueRisk"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("High-Value Count",   f"{hv_total:,}")
    with c2: kpi_card("HV Churn Rate",      f"{hv_cr:.1f}%")
    with c3: kpi_card("HV Churned",         f"{hv_churned:,}")
    with c4: kpi_card("Avg Balance",        f"€{hv_avg_bal:,.0f}")
    with c5: kpi_card("Revenue at Risk",    f"€{hv_rev_risk/1e6:.2f}M")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── HV vs Standard comparison ─────────────────────────────
    section_title("High-Value vs Standard Customer Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Customer Radar: High-Value vs Standard")
        st.plotly_chart(high_value_radar(df), use_container_width=True)

    with col2:
        # Side-by-side bar comparison of key metrics
        metrics = ["CreditScore", "Age", "Tenure", "NumOfProducts"]
        labels  = ["Credit Score", "Age (yrs)", "Tenure (yrs)", "# Products"]
        hv_vals = [hv[m].mean() for m in metrics]
        nhv_vals= [nhv[m].mean() for m in metrics]

        fig_cmp = go.Figure(data=[
            go.Bar(name="High-Value",  x=labels, y=hv_vals,
                   marker_color=COLORS["accent"]),
            go.Bar(name="Standard",   x=labels, y=nhv_vals,
                   marker_color=COLORS["secondary"]),
        ])
        fig_cmp.update_layout(
            barmode="group",
            template=PLOTLY_TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.1),
        )
        st.markdown("##### Avg Metrics: HV vs Standard")
        st.plotly_chart(fig_cmp, use_container_width=True)

    # ── Credit score vs balance scatter ───────────────────────
    section_title("Credit Score × Balance Landscape")
    st.plotly_chart(credit_balance_scatter(df), use_container_width=True)

    # ── HV churn by geography ─────────────────────────────────
    section_title("High-Value Churn by Country")
    hv_geo = (
        hv.groupby("Geography")["Exited"]
        .agg(["sum", "count", "mean"])
        .rename(columns={"sum": "Churned", "count": "Total", "mean": "ChurnRate"})
        .reset_index()
    )
    hv_geo["ChurnRate"] *= 100

    col3, col4 = st.columns(2)
    with col3:
        fig_hv_geo = px.bar(
            hv_geo, x="Geography", y="ChurnRate",
            color="ChurnRate",
            color_continuous_scale=["#2DC653", "#F6AE2D", "#E63946"],
            text=hv_geo["ChurnRate"].round(1).astype(str) + "%",
            template=PLOTLY_TEMPLATE,
            title="HV Churn Rate by Country",
        )
        fig_hv_geo.update_traces(textposition="outside")
        fig_hv_geo.update_coloraxes(showscale=False)
        fig_hv_geo.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_hv_geo, use_container_width=True)

    with col4:
        fig_hv_cnt = px.bar(
            hv_geo, x="Geography", y=["Total", "Churned"],
            barmode="overlay", opacity=0.8,
            color_discrete_map={"Total": COLORS["secondary"], "Churned": COLORS["danger"]},
            template=PLOTLY_TEMPLATE,
            title="HV Counts by Country",
        )
        fig_hv_cnt.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_hv_cnt, use_container_width=True)

    # ── HV churn by age group ─────────────────────────────────
    section_title("High-Value Churn by Age Group & Gender")
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(
            segment_churn_bar(hv, "AgeGroup", "HV Churn Rate by Age"),
            use_container_width=True,
        )
    with col6:
        st.plotly_chart(
            segment_churn_bar(hv, "Gender", "HV Churn Rate by Gender"),
            use_container_width=True,
        )

    # ── Revenue risk treemap ──────────────────────────────────
    section_title("Revenue Risk from High-Value Churners")
    if hv["Exited"].sum() > 0:
        st.plotly_chart(revenue_risk_treemap(hv), use_container_width=True)

    # ── Active member breakdown ───────────────────────────────
    section_title("Activity Status — High-Value Customers")
    hv_act = hv["ActiveStatus"].value_counts().reset_index()
    hv_act.columns = ["Status", "Count"]
    fig_act = px.pie(
        hv_act, names="Status", values="Count",
        color="Status",
        color_discrete_map={"Active": COLORS["success"], "Inactive": COLORS["danger"]},
        hole=0.5,
        template=PLOTLY_TEMPLATE,
    )
    fig_act.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=10),
    )
    col7, col8 = st.columns([1, 2])
    with col7:
        st.plotly_chart(fig_act, use_container_width=True)
    with col8:
        st.markdown("<br><br>", unsafe_allow_html=True)
        warning_box(
            f"<strong>{hv_cr:.1f}%</strong> of high-value customers have churned. "
            f"Each lost customer represents an average balance of <strong>€{hv_avg_bal:,.0f}</strong>. "
            f"Total estimated revenue at risk: <strong>€{hv_rev_risk/1e6:.2f}M</strong>."
        )
        success_box(
            "Recommend assigning a dedicated <strong>Relationship Manager</strong> to the "
            "top 10% of high-value customers. Personalised touchpoints can reduce HV churn by up to 30%."
        )

    # ── Top 20 churned HV customers ───────────────────────────
    section_title("Top 20 High-Value Churned Customers (by Balance)")
    top20 = (
        hv[hv["Exited"] == 1]
        .sort_values("Balance", ascending=False)
        .head(20)
        [["Geography", "Gender", "Age", "CreditScore", "Balance",
          "Tenure", "NumOfProducts", "IsActiveMember", "EstimatedSalary"]]
        .reset_index(drop=True)
    )
    top20.index += 1
    st.dataframe(
        top20.style.background_gradient(subset=["Balance"], cmap="Reds"),
        use_container_width=True,
    )
