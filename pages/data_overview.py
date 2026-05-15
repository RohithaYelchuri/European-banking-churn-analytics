# pages/data_overview.py
# ─────────────────────────────────────────────────────────────
# Data Overview – raw data, stats, quality report
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.ui_helpers import page_header, section_title, insight, build_sidebar_filters
from utils.data_loader import apply_filters
from utils.charts import correlation_matrix, credit_band_bar
from config.settings import COLORS, PLOTLY_TEMPLATE


def render():
    if "df_raw" not in st.session_state:
        st.info("📂 Please upload your dataset via the sidebar to begin.")
        return

    df_raw = st.session_state["df_raw"]
    filters = build_sidebar_filters(df_raw)
    df = apply_filters(df_raw, **filters)

    page_header(
        "📋 Data Overview",
        "Raw data inspection, descriptive statistics, and data quality assessment",
    )

    # ── Dataset shape ─────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rows", f"{len(df):,}")
    c2.metric("Columns", str(df.shape[1]))
    c3.metric("Missing Values", str(df.isnull().sum().sum()))

    # ── Raw data preview ──────────────────────────────────────
    section_title("Raw Data Preview")
    show_n = st.slider("Rows to display", 5, 100, 20, step=5)
    st.dataframe(
        df.head(show_n).style.background_gradient(
            subset=["Balance", "CreditScore", "EstimatedSalary"],
            cmap="Blues",
        ),
        use_container_width=True,
        height=320,
    )

    # ── Descriptive statistics ────────────────────────────────
    section_title("Descriptive Statistics")
    num_cols = df.select_dtypes(include="number").columns.tolist()
    desc = df[num_cols].describe().T.round(2)
    desc["skew"]     = df[num_cols].skew().round(3)
    desc["kurtosis"] = df[num_cols].kurtosis().round(3)
    st.dataframe(desc.style.background_gradient(subset=["mean", "std"], cmap="coolwarm"),
                 use_container_width=True)

    # ── Column data types ─────────────────────────────────────
    section_title("Column Info")
    col_info = pd.DataFrame({
        "Column"    : df.columns,
        "Dtype"     : df.dtypes.astype(str).values,
        "Non-Null"  : df.notnull().sum().values,
        "Nulls"     : df.isnull().sum().values,
        "Unique"    : df.nunique().values,
        "Sample"    : [str(df[c].dropna().iloc[0]) if not df[c].dropna().empty else "" for c in df.columns],
    })
    st.dataframe(col_info, use_container_width=True, height=320)

    # ── Correlation matrix ────────────────────────────────────
    section_title("Correlation Matrix")
    st.plotly_chart(correlation_matrix(df), use_container_width=True)

    insight(
        "The correlation matrix reveals that <strong>Age</strong> and "
        "<strong>Balance</strong> have the highest positive correlation with "
        "<strong>Exited</strong>. <strong>NumOfProducts</strong> and "
        "<strong>IsActiveMember</strong> show negative correlation — customers "
        "with more products and active status are less likely to churn."
    )

    # ── Distribution of numeric features ─────────────────────
    section_title("Feature Distributions")
    dist_col = st.selectbox(
        "Select feature to inspect",
        options=["CreditScore", "Age", "Tenure", "Balance", "EstimatedSalary"],
    )
    fig = px.histogram(
        df, x=dist_col, color="ChurnLabel",
        color_discrete_map={"Retained": COLORS["success"], "Churned": COLORS["danger"]},
        barmode="overlay", nbins=50, opacity=0.75,
        template=PLOTLY_TEMPLATE,
        marginal="box",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Categorical distribution ──────────────────────────────
    section_title("Categorical Distributions")
    cat_col = st.selectbox(
        "Select category",
        options=["Geography", "Gender", "AgeGroup", "CreditBand", "BalanceSegment", "TenureSegment"],
    )
    cat_counts = df[cat_col].value_counts().reset_index()
    cat_counts.columns = [cat_col, "Count"]
    fig2 = px.bar(
        cat_counts, x=cat_col, y="Count",
        color="Count",
        color_continuous_scale="Blues",
        template=PLOTLY_TEMPLATE,
        text="Count",
    )
    fig2.update_traces(textposition="outside")
    fig2.update_coloraxes(showscale=False)
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Download ──────────────────────────────────────────────
    section_title("Export")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered Dataset (CSV)",
        data=csv,
        file_name="filtered_churn_data.csv",
        mime="text/csv",
    )
