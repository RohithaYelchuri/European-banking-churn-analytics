# utils/data_loader.py
# ─────────────────────────────────────────────────────────────
# Handles all data ingestion, cleaning, and feature engineering
# ─────────────────────────────────────────────────────────────

import os
import pandas as pd
import numpy as np
import streamlit as st
from config.settings import (
    DATASET_PATH, COLUMN_MAP, REQUIRED_COLS,
    AGE_BINS, AGE_LABELS,
    CREDIT_BINS, CREDIT_LABELS,
    BALANCE_BINS, BALANCE_LABELS,
    TENURE_BINS, TENURE_LABELS,
    HIGH_VALUE_BALANCE_THRESHOLD,
)


# ── Public entry-point ────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_data(uploaded_file=None) -> pd.DataFrame:
    """
    Load data from an uploaded Streamlit file object OR the default
    path in dataset/.  Returns a fully cleaned & enriched DataFrame.
    """
    raw = _read_source(uploaded_file)
    df  = _clean(raw)
    df  = _engineer_features(df)
    return df


def dataset_exists() -> bool:
    return os.path.isfile(DATASET_PATH)


# ── Internal helpers ──────────────────────────────────────────

def _read_source(uploaded_file) -> pd.DataFrame:
    """Read Excel from uploaded file object or disk path."""
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file, engine="openpyxl")
    if dataset_exists():
        return pd.read_excel(DATASET_PATH, engine="openpyxl")
    raise FileNotFoundError(
        f"No dataset found. Place your Excel file at:\n  {DATASET_PATH}\n"
        "or upload it via the sidebar."
    )


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize columns, handle missing values, drop noise."""
    # ── Normalize column names ─────────────────────────────
    df.columns = df.columns.str.strip()
    rename_map = {
        col: COLUMN_MAP[col.lower()]
        for col in df.columns
        if col.lower() in COLUMN_MAP
    }
    df = df.rename(columns=rename_map)

    # ── Drop utility columns ───────────────────────────────
    drop_cols = [c for c in ["RowNumber", "CustomerID", "Surname"] if c in df.columns]
    df = df.drop(columns=drop_cols)

    # ── Validate required columns ──────────────────────────
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    # ── Handle missing values ──────────────────────────────
    numeric_cols  = df.select_dtypes(include="number").columns.tolist()
    category_cols = df.select_dtypes(include="object").columns.tolist()

    df[numeric_cols]  = df[numeric_cols].fillna(df[numeric_cols].median())
    df[category_cols] = df[category_cols].fillna(df[category_cols].mode().iloc[0])

    # ── Remove duplicates ──────────────────────────────────
    df = df.drop_duplicates().reset_index(drop=True)

    # ── Coerce types ───────────────────────────────────────
    for col in ["CreditScore", "Age", "Tenure", "NumOfProducts",
                "HasCrCard", "IsActiveMember", "Exited"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["Balance"]         = pd.to_numeric(df["Balance"],         errors="coerce").fillna(0)
    df["EstimatedSalary"] = pd.to_numeric(df["EstimatedSalary"], errors="coerce").fillna(0)

    # ── Normalise string categoricals ─────────────────────
    for col in ["Geography", "Gender"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    return df


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived segmentation fields."""

    # Age group
    df["AgeGroup"] = pd.cut(
        df["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=True
    ).astype(str)

    # Credit score band
    df["CreditBand"] = pd.cut(
        df["CreditScore"], bins=CREDIT_BINS, labels=CREDIT_LABELS, right=True
    ).astype(str)

    # Balance segment
    df["BalanceSegment"] = pd.cut(
        df["Balance"], bins=BALANCE_BINS, labels=BALANCE_LABELS, right=True
    ).astype(str)

    # Tenure segment
    df["TenureSegment"] = pd.cut(
        df["Tenure"], bins=TENURE_BINS, labels=TENURE_LABELS, right=True
    ).astype(str)

    # Active status label
    df["ActiveStatus"] = df["IsActiveMember"].map({1: "Active", 0: "Inactive"})

    # Churn label
    df["ChurnLabel"] = df["Exited"].map({1: "Churned", 0: "Retained"})

    # High-value customer flag
    df["IsHighValue"] = (df["Balance"] >= HIGH_VALUE_BALANCE_THRESHOLD).astype(int)

    # Products label
    df["ProductsLabel"] = "Products: " + df["NumOfProducts"].astype(str)

    # Wealth tier (composite)
    df["WealthTier"] = pd.qcut(
        df["EstimatedSalary"],
        q=4,
        labels=["Budget", "Middle", "Affluent", "Premium"],
        duplicates="drop"
    ).astype(str)

    # Revenue risk: estimated annual fee exposure (simplified proxy)
    df["RevenueRisk"] = df["Balance"] * df["Exited"] * 0.015   # 1.5% fee proxy

    return df


# ── Filter helper (used by every page) ────────────────────────

def apply_filters(
    df: pd.DataFrame,
    geographies: list,
    genders: list,
    age_groups: list,
    balance_range: tuple,
    credit_bands: list,
) -> pd.DataFrame:
    """Apply sidebar filters and return the filtered DataFrame."""
    mask = pd.Series(True, index=df.index)

    if geographies:
        mask &= df["Geography"].isin(geographies)
    if genders:
        mask &= df["Gender"].isin(genders)
    if age_groups:
        mask &= df["AgeGroup"].isin(age_groups)
    if credit_bands:
        mask &= df["CreditBand"].isin(credit_bands)

    bal_min, bal_max = balance_range
    mask &= (df["Balance"] >= bal_min) & (df["Balance"] <= bal_max)

    return df[mask].copy()
