# 🏦 Customer Segmentation & Churn Pattern Analytics
### European Banking — BankIQ Analytics Platform

---

## 📌 Project Overview

A **production-ready, multi-page Streamlit application** that delivers end-to-end customer
segmentation and churn analysis for a European retail banking dataset. Built with Python,
Pandas, Plotly, and Streamlit.

---

## 🗂️ Folder Structure

```
customer_churn_analytics/
│
├── app.py                      ← Main entry point (run this)
│
├── pages/                      ← One file per Streamlit page
│   ├── home.py                 ← Home Dashboard
│   ├── data_overview.py        ← Data Overview & EDA
│   ├── segmentation.py         ← Customer Segmentation
│   ├── churn_analysis.py       ← Churn Deep-Dive
│   ├── high_value.py           ← High-Value Customer Analysis
│   ├── kpi_dashboard.py        ← KPI Scorecard with Gauges
│   └── recommendations.py      ← Business Recommendations
│
├── utils/                      ← Shared utility modules
│   ├── data_loader.py          ← Data ingestion, cleaning, feature engineering
│   ├── charts.py               ← Plotly chart factory functions
│   └── ui_helpers.py           ← CSS, sidebar filters, KPI cards
│
├── config/
│   └── settings.py             ← Central configuration & constants
│
├── dataset/
│   └── bank_churn.xlsx         ← Place your Excel dataset here
│
├── .streamlit/
│   └── config.toml             ← Streamlit theme configuration
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone / download the project

```bash
git clone https://github.com/yourname/customer_churn_analytics.git
cd customer_churn_analytics
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your dataset

Place your Excel file at:
```
dataset/bank_churn.xlsx
```

Expected columns (any capitalisation):
`CreditScore, Geography, Gender, Age, Tenure, Balance,
NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Exited`

Optional columns auto-dropped: `RowNumber, CustomerID, Surname`

---

## 🚀 Running the App

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

Alternatively, upload your Excel file directly via the sidebar file uploader — no need to
place it in the dataset folder.

---

## 📄 Pages

| Page | Description |
|------|-------------|
| 🏠 Home Dashboard | Executive overview, top KPIs, country & churn charts |
| 📋 Data Overview | Raw data, stats, correlation matrix, feature distributions |
| 👥 Customer Segmentation | Geography, age, credit, balance, tenure, active segmentation |
| 📉 Churn Analysis | Deep-dive churn by every dimension + revenue risk treemap |
| 💎 High-Value Customers | €100K+ balance analysis, radar chart, top churners table |
| 📊 KPI Dashboard | Gauge indicators, segment matrix, executive scorecard table |
| 💡 Recommendations | 5 priority actions, ROI projection, business conclusions |

---

## 🔎 Sidebar Filters (apply across all pages)

- 🌍 Country (Geography)
- 👤 Gender
- 🎂 Age Group
- 💶 Balance Range (EUR)
- 💳 Credit Band

---

## ☁️ Deployment on Streamlit Cloud

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourname/customer_churn_analytics.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repo
4. Set **Main file path** to `app.py`
5. Click **Deploy**

> **Note**: Upload your dataset via the sidebar file uploader when using the cloud version
> (do not commit sensitive data to GitHub).

### 3. Optional: Add dataset as Streamlit Secret

For persistent cloud datasets, use Streamlit Secrets or connect to a cloud storage bucket
(S3, GCS) and modify `utils/data_loader.py` accordingly.

---

## 🛠️ Tech Stack

| Library | Purpose |
|---------|---------|
| Streamlit 1.35 | Web application framework |
| Pandas 2.2 | Data manipulation |
| NumPy 1.26 | Numerical operations |
| Plotly 5.22 | Interactive visualisations |
| Seaborn / Matplotlib | Static charts (EDA) |
| Scikit-learn | Feature engineering support |
| OpenPyXL | Excel file reading |

---

## 📊 Key Insights Generated

1. **Churn rate** typically 15–25% in European retail banking datasets
2. **Age 45–54** is the highest-risk cohort
3. **Inactive members** churn 2–3× more than active members
4. **High-balance customers** are not inherently loyal
5. **Germany** shows disproportionately high churn in multi-country datasets
6. **Multi-product holders** (3–4 products) show a counter-intuitive churn spike

---

## 👤 Author

**BankIQ Analytics**
Built with Python + Streamlit | European Banking Intelligence
