# config/settings.py
# ─────────────────────────────────────────────────────────────
# Central configuration for the Customer Churn Analytics App
# ─────────────────────────────────────────────────────────────

import os

# ── Paths ────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
CHARTS_DIR  = os.path.join(BASE_DIR, "charts")
ASSETS_DIR  = os.path.join(BASE_DIR, "assets")

# Expected dataset filename (user drops their file here)
DATASET_FILENAME = "bank_churn.xlsx"
DATASET_PATH     = os.path.join(DATASET_DIR, DATASET_FILENAME)

# ── App Meta ─────────────────────────────────────────────────
APP_TITLE    = "European Banking – Customer Segmentation & Churn Analytics"
APP_ICON     = "🏦"
APP_VERSION  = "1.0.0"
COMPANY_NAME = "BankIQ Analytics"

# ── Colour Palette ───────────────────────────────────────────
COLORS = {
    "primary"   : "#1A3C5E",   # deep navy
    "secondary" : "#2E86AB",   # steel blue
    "accent"    : "#F6AE2D",   # gold
    "danger"    : "#E63946",   # churn / risk red
    "success"   : "#2DC653",   # retained green
    "neutral"   : "#8D99AE",   # muted grey
    "bg_dark"   : "#0F1B2D",
    "bg_card"   : "#1E2D40",
    "text_light": "#EDF2F4",
    "text_muted": "#8D99AE",
}

PLOTLY_TEMPLATE = "plotly_dark"

# ── Segmentation Thresholds ───────────────────────────────────
AGE_BINS    = [0, 25, 35, 45, 55, 65, 120]
AGE_LABELS  = ["<25", "25-34", "35-44", "45-54", "55-64", "65+"]

CREDIT_BINS   = [0, 500, 580, 670, 740, 800, 900]
CREDIT_LABELS = ["Very Poor", "Poor", "Fair", "Good", "Very Good", "Exceptional"]

BALANCE_BINS   = [0, 1, 50_000, 100_000, 150_000, 200_000, 300_000]
BALANCE_LABELS = ["Zero Balance", "Low", "Mid", "High", "Very High", "Ultra High"]

TENURE_BINS   = [-1, 1, 3, 5, 7, 10]
TENURE_LABELS = ["New (≤1yr)", "Early (2-3yr)", "Mid (4-5yr)", "Loyal (6-7yr)", "Champion (8-10yr)"]

# ── Column Mapping ────────────────────────────────────────────
# Maps possible Excel column names → standard internal names
COLUMN_MAP = {
    "customerid"       : "CustomerID",
    "customer_id"      : "CustomerID",
    "surname"          : "Surname",
    "creditscore"      : "CreditScore",
    "credit_score"     : "CreditScore",
    "geography"        : "Geography",
    "country"          : "Geography",
    "gender"           : "Gender",
    "age"              : "Age",
    "tenure"           : "Tenure",
    "balance"          : "Balance",
    "numofproducts"    : "NumOfProducts",
    "num_of_products"  : "NumOfProducts",
    "hascrcard"        : "HasCrCard",
    "has_cr_card"      : "HasCrCard",
    "isactivemember"   : "IsActiveMember",
    "is_active_member" : "IsActiveMember",
    "estimatedsalary"  : "EstimatedSalary",
    "estimated_salary" : "EstimatedSalary",
    "exited"           : "Exited",
    "churn"            : "Exited",
    "churned"          : "Exited",
    "rowNumber"        : "RowNumber",
    "rownumber"        : "RowNumber",
}

REQUIRED_COLS = [
    "CreditScore", "Geography", "Gender", "Age", "Tenure",
    "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
    "EstimatedSalary", "Exited",
]

# ── High-Value Customer Threshold ─────────────────────────────
HIGH_VALUE_BALANCE_THRESHOLD = 100_000   # EUR
