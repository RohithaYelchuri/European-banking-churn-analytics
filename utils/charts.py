# utils/charts.py
# ─────────────────────────────────────────────────────────────
# Reusable Plotly chart factory functions
# ─────────────────────────────────────────────────────────────

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from config.settings import COLORS, PLOTLY_TEMPLATE


# ── Colour sequences ──────────────────────────────────────────
CHURN_COLORS  = [COLORS["success"], COLORS["danger"]]
SEGMENT_SEQ   = px.colors.qualitative.Bold
GEOGRAPHY_SEQ = [COLORS["secondary"], COLORS["accent"], COLORS["danger"]]


# ─────────────────────────────────────────────────────────────
# KPI Card (plain text metric, rendered via st.metric)
# ─────────────────────────────────────────────────────────────

def kpi_data(df: pd.DataFrame) -> dict:
    """Return a dict of headline KPIs computed from the filtered DataFrame."""
    total     = len(df)
    churned   = df["Exited"].sum()
    retained  = total - churned
    churn_rt  = churned / total * 100 if total else 0
    avg_bal   = df["Balance"].mean()
    avg_cs    = df["CreditScore"].mean()
    avg_age   = df["Age"].mean()
    hi_val    = df["IsHighValue"].sum()
    rev_risk  = df["RevenueRisk"].sum()
    active    = df["IsActiveMember"].sum()
    active_pct= active / total * 100 if total else 0

    return dict(
        total=total, churned=churned, retained=retained,
        churn_rate=churn_rt, avg_balance=avg_bal,
        avg_credit=avg_cs, avg_age=avg_age,
        high_value=hi_val, revenue_risk=rev_risk,
        active=active, active_pct=active_pct,
    )


# ─────────────────────────────────────────────────────────────
# Churn distribution pie
# ─────────────────────────────────────────────────────────────

def churn_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["ChurnLabel"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    fig = px.pie(
        counts, names="Status", values="Count",
        color="Status",
        color_discrete_map={"Retained": COLORS["success"], "Churned": COLORS["danger"]},
        hole=0.55,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(textinfo="percent+label", pull=[0, 0.07])
    fig.update_layout(
        margin=dict(t=30, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Geography churn bar chart
# ─────────────────────────────────────────────────────────────

def churn_by_geography(df: pd.DataFrame) -> go.Figure:
    grp = (
        df.groupby("Geography")["Exited"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "Churned", "count": "Total"})
        .reset_index()
    )
    grp["ChurnRate"] = grp["Churned"] / grp["Total"] * 100

    fig = go.Figure()
    fig.add_bar(
        x=grp["Geography"], y=grp["Total"],
        name="Total", marker_color=COLORS["secondary"], opacity=0.6,
    )
    fig.add_bar(
        x=grp["Geography"], y=grp["Churned"],
        name="Churned", marker_color=COLORS["danger"],
    )
    fig.update_layout(
        barmode="overlay",
        template=PLOTLY_TEMPLATE,
        xaxis_title="Country",
        yaxis_title="Customers",
        legend=dict(orientation="h", y=1.1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Churn rate heatmap by age group × geography
# ─────────────────────────────────────────────────────────────

def churn_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = (
        df.groupby(["AgeGroup", "Geography"])["Exited"]
        .mean()
        .mul(100)
        .unstack(fill_value=0)
    )
    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="RdYlGn_r",
            colorbar=dict(title="Churn %"),
            text=np.round(pivot.values, 1),
            texttemplate="%{text}%",
        )
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        xaxis_title="Country",
        yaxis_title="Age Group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Correlation matrix
# ─────────────────────────────────────────────────────────────

def correlation_matrix(df: pd.DataFrame) -> go.Figure:
    num_cols = ["CreditScore", "Age", "Tenure", "Balance",
                "NumOfProducts", "HasCrCard", "IsActiveMember",
                "EstimatedSalary", "Exited"]
    cols = [c for c in num_cols if c in df.columns]
    corr = df[cols].corr().round(2)

    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu",
            zmid=0,
            text=corr.values,
            texttemplate="%{text}",
            colorbar=dict(title="r"),
        )
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
        height=500,
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Segment-wise churn rate bars (generic)
# ─────────────────────────────────────────────────────────────

def segment_churn_bar(df: pd.DataFrame, segment_col: str,
                      title: str = "") -> go.Figure:
    grp = (
        df.groupby(segment_col)["Exited"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "ChurnRate", "count": "Count"})
        .reset_index()
    )
    grp["ChurnRate"] = grp["ChurnRate"] * 100

    fig = px.bar(
        grp, x=segment_col, y="ChurnRate",
        color="ChurnRate",
        color_continuous_scale=["#2DC653", "#F6AE2D", "#E63946"],
        text=grp["ChurnRate"].round(1).astype(str) + "%",
        template=PLOTLY_TEMPLATE,
        labels={"ChurnRate": "Churn Rate (%)"},
        title=title,
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Balance distribution by churn status
# ─────────────────────────────────────────────────────────────

def balance_distribution(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for label, color in [("Retained", COLORS["success"]), ("Churned", COLORS["danger"])]:
        sub = df[df["ChurnLabel"] == label]["Balance"]
        fig.add_trace(
            go.Histogram(
                x=sub, name=label, opacity=0.75,
                marker_color=color, nbinsx=40,
            )
        )
    fig.update_layout(
        barmode="overlay",
        template=PLOTLY_TEMPLATE,
        xaxis_title="Balance (EUR)",
        yaxis_title="Count",
        legend=dict(orientation="h", y=1.1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Age distribution by churn
# ─────────────────────────────────────────────────────────────

def age_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="Age", color="ChurnLabel",
        color_discrete_map={"Retained": COLORS["success"], "Churned": COLORS["danger"]},
        barmode="overlay",
        nbins=40,
        opacity=0.78,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Count",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
        legend=dict(orientation="h", y=1.1),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Products vs churn grouped bar
# ─────────────────────────────────────────────────────────────

def products_churn_bar(df: pd.DataFrame) -> go.Figure:
    grp = (
        df.groupby(["NumOfProducts", "ChurnLabel"])
        .size()
        .reset_index(name="Count")
    )
    fig = px.bar(
        grp, x="NumOfProducts", y="Count", color="ChurnLabel",
        barmode="group",
        color_discrete_map={"Retained": COLORS["success"], "Churned": COLORS["danger"]},
        template=PLOTLY_TEMPLATE,
        labels={"NumOfProducts": "Number of Products"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
        legend=dict(orientation="h", y=1.1),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Scatter: credit score vs balance coloured by churn
# ─────────────────────────────────────────────────────────────

def credit_balance_scatter(df: pd.DataFrame) -> go.Figure:
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        sample,
        x="CreditScore", y="Balance",
        color="ChurnLabel",
        color_discrete_map={"Retained": COLORS["success"], "Churned": COLORS["danger"]},
        opacity=0.65,
        size_max=8,
        template=PLOTLY_TEMPLATE,
        hover_data=["Age", "Geography", "NumOfProducts"],
    )
    fig.update_layout(
        xaxis_title="Credit Score",
        yaxis_title="Balance (EUR)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
        legend=dict(orientation="h", y=1.1),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Revenue risk by geography treemap
# ─────────────────────────────────────────────────────────────

def revenue_risk_treemap(df: pd.DataFrame) -> go.Figure:
    grp = (
        df[df["Exited"] == 1]
        .groupby(["Geography", "BalanceSegment"])["RevenueRisk"]
        .sum()
        .reset_index()
    )
    grp["RevenueRiskM"] = grp["RevenueRisk"] / 1e6

    fig = px.treemap(
        grp,
        path=["Geography", "BalanceSegment"],
        values="RevenueRiskM",
        color="RevenueRiskM",
        color_continuous_scale="Reds",
        template=PLOTLY_TEMPLATE,
        labels={"RevenueRiskM": "Risk (€M)"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Gender churn comparison (side-by-side pie)
# ─────────────────────────────────────────────────────────────

def gender_churn_comparison(df: pd.DataFrame) -> go.Figure:
    genders = df["Gender"].unique()
    fig = make_subplots(
        rows=1, cols=len(genders),
        specs=[[{"type": "pie"}] * len(genders)],
        subplot_titles=[f"{g} Customers" for g in genders],
    )
    for i, gender in enumerate(genders, start=1):
        sub = df[df["Gender"] == gender]["ChurnLabel"].value_counts()
        fig.add_trace(
            go.Pie(
                labels=sub.index.tolist(),
                values=sub.values.tolist(),
                marker_colors=[COLORS["success"], COLORS["danger"]],
                hole=0.5,
                name=gender,
            ),
            row=1, col=i,
        )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=10),
        legend=dict(orientation="h", y=-0.1),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Funnel: Active / Inactive / Churned
# ─────────────────────────────────────────────────────────────

def active_churn_funnel(df: pd.DataFrame) -> go.Figure:
    total    = len(df)
    active   = df["IsActiveMember"].sum()
    inactive = total - active
    churned  = df["Exited"].sum()

    fig = go.Figure(go.Funnel(
        y=["Total Customers", "Active Members", "Inactive Members", "Churned"],
        x=[total, active, inactive, churned],
        textinfo="value+percent initial",
        marker=dict(color=[
            COLORS["primary"], COLORS["success"],
            COLORS["neutral"], COLORS["danger"],
        ]),
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# High-value customer profile radar
# ─────────────────────────────────────────────────────────────

def high_value_radar(df: pd.DataFrame) -> go.Figure:
    cats = ["CreditScore", "Age", "Tenure", "NumOfProducts", "IsActiveMember"]
    labels = ["Credit Score", "Age", "Tenure", "Products", "Active"]

    def _norm(df_sub, col):
        mn, mx = df[col].min(), df[col].max()
        return ((df_sub[col].mean() - mn) / (mx - mn) * 100) if mx != mn else 50

    hv  = df[df["IsHighValue"] == 1]
    nhv = df[df["IsHighValue"] == 0]

    fig = go.Figure()
    for subset, name, color in [(hv, "High Value", COLORS["accent"]),
                                 (nhv, "Standard",  COLORS["secondary"])]:
        vals = [_norm(subset, c) for c in cats] + [_norm(subset, cats[0])]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=labels + [labels[0]],
            fill="toself", name=name,
            line_color=color, fillcolor=color,
            opacity=0.4,
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.1),
        margin=dict(t=30, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Tenure vs churn line chart
# ─────────────────────────────────────────────────────────────

def tenure_churn_line(df: pd.DataFrame) -> go.Figure:
    grp = (
        df.groupby("Tenure")["Exited"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "ChurnRate", "count": "Count"})
        .reset_index()
    )
    grp["ChurnRate"] *= 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=grp["Tenure"], y=grp["ChurnRate"],
        mode="lines+markers",
        name="Churn Rate",
        line=dict(color=COLORS["danger"], width=3),
        marker=dict(size=8),
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        xaxis_title="Tenure (years)",
        yaxis_title="Churn Rate (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Balance segment pie
# ─────────────────────────────────────────────────────────────

def balance_segment_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["BalanceSegment"].value_counts().reset_index()
    counts.columns = ["Segment", "Count"]
    fig = px.pie(
        counts, names="Segment", values="Count",
        hole=0.45,
        color_discrete_sequence=SEGMENT_SEQ,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_traces(textinfo="percent+label", pull=[0.03] * len(counts))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# Credit band distribution
# ─────────────────────────────────────────────────────────────

def credit_band_bar(df: pd.DataFrame) -> go.Figure:
    order = ["Very Poor", "Poor", "Fair", "Good", "Very Good", "Exceptional"]
    grp = df["CreditBand"].value_counts().reindex(order).dropna().reset_index()
    grp.columns = ["Band", "Count"]

    fig = px.bar(
        grp, x="Band", y="Count",
        color="Count",
        color_continuous_scale="Blues",
        template=PLOTLY_TEMPLATE,
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        xaxis_title="Credit Band",
        yaxis_title="Customers",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10),
    )
    return fig
