"""
=============================================================================
 Late Delivery Risk Prediction — Training Pipeline  (Windows-Fixed)
=============================================================================
 HOW TO RUN — open Command Prompt in your project root folder:

   cd C:/Users/Rohitha/Downloads/late_delivery_risk
   python src/train_pipeline.py

 After it finishes run the dashboard:
   python -m streamlit run streamlit_app/app.py
   Then open: http://localhost:8501
=============================================================================
"""
import warnings; warnings.filterwarnings('ignore')
import os, sys, pickle
import numpy as np
import pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, roc_curve
)

# Try XGBoost — silently fall back to GradientBoosting if not installed
try:
    from xgboost import XGBClassifier
    USE_XGB = True
    print("  XGBoost found and will be used.")
except ImportError:
    USE_XGB = False
    print("  XGBoost not installed — using GradientBoostingClassifier instead.")

sns.set_theme(style='whitegrid', palette='Set2')

# ─────────────────────────────────────────────────────────────────────────────
# PATHS — built from THIS file's location so they work on any machine/OS
# This script = <project_root>/src/train_pipeline.py
# BASE         = <project_root>/
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE        = os.path.dirname(SCRIPT_DIR)

DATA_PATH   = os.path.join(BASE, 'data',    'APL_Logistics.csv')
CHARTS_DIR  = os.path.join(BASE, 'charts')
MODELS_DIR  = os.path.join(BASE, 'models')
REPORTS_DIR = os.path.join(BASE, 'reports')

for d in (CHARTS_DIR, MODELS_DIR, REPORTS_DIR):
    os.makedirs(d, exist_ok=True)

def save_chart(filename):
    plt.savefig(os.path.join(CHARTS_DIR, filename), dpi=150, bbox_inches='tight')
    plt.close()

print("=" * 62)
print("  LATE DELIVERY RISK — ML TRAINING PIPELINE")
print("=" * 62)
print(f"  Project root : {BASE}")
print(f"  Data file    : {DATA_PATH}")

# ── 1. Load ───────────────────────────────────────────────────────────────────
print("\n[1/10] Loading dataset...")
if not os.path.exists(DATA_PATH):
    print(f"\n  ERROR: Dataset not found at:\n  {DATA_PATH}")
    print("\n  FIX: Copy APL_Logistics.csv into the 'data' sub-folder.")
    input("\nPress Enter to exit...")
    sys.exit(1)

df = pd.read_csv(DATA_PATH, encoding='latin1')
print(f"  Loaded {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"  Late rate: {df['Late_delivery_risk'].mean()*100:.1f}%")

# ── 2. Feature Engineering ────────────────────────────────────────────────────
print("\n[2/10] Feature engineering...")
df['shipping_delay']  = df['Days for shipping (real)'] - df['Days for shipment (scheduled)']
df['is_delayed']      = (df['shipping_delay'] > 0).astype(int)
df['discount_amount'] = df['Order Item Product Price'] - df['Order Item Total']
df['profit_margin']   = df['Order Profit Per Order'] / (df['Sales'] + 1e-9)
df['schedule_ratio']  = df['Days for shipping (real)'] / (df['Days for shipment (scheduled)'] + 1e-9)
print("  5 new features created.")

# ── 3. EDA Charts 01-05 ───────────────────────────────────────────────────────
print("\n[3/10] Generating EDA charts...")

# 01 Target distribution
counts = df['Late_delivery_risk'].value_counts()
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].bar(['On Time (0)', 'Late (1)'], counts.values,
            color=['#2ecc71', '#e74c3c'], edgecolor='white', linewidth=1.5)
axes[0].set_title('Late Delivery Risk Distribution', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Count')
for i, v in enumerate(counts.values):
    axes[0].text(i, v + 500, f'{v:,}\n({v/len(df)*100:.1f}%)', ha='center', fontweight='bold')
axes[1].pie(counts.values, labels=['On Time', 'Late Delivery'],
            colors=['#2ecc71', '#e74c3c'], autopct='%1.1f%%', startangle=90)
axes[1].set_title('Target Pie Chart', fontsize=14, fontweight='bold')
plt.tight_layout(); save_chart('01_target_distribution.png')

# 02 Shipping mode
ship_late = df.groupby('Shipping Mode')['Late_delivery_risk'].mean().sort_values(ascending=False)
ship_vol  = df.groupby('Shipping Mode')['Late_delivery_risk'].count()
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
bars = axes[0].barh(ship_late.index, ship_late.values * 100,
                    color=['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71'])
axes[0].set_xlabel('Late Delivery Rate (%)'); axes[0].set_title('Late Rate by Shipping Mode', fontweight='bold')
for bar, val in zip(bars, ship_late.values):
    axes[0].text(val * 100 + 0.3, bar.get_y() + bar.get_height() / 2,
                 f'{val*100:.1f}%', va='center', fontweight='bold')
axes[1].bar(ship_vol.index, ship_vol.values, color=sns.color_palette('Set2', 4))
axes[1].set_title('Volume by Shipping Mode', fontweight='bold')
axes[1].tick_params(axis='x', rotation=15)
plt.tight_layout(); save_chart('02_shipping_mode_analysis.png')

# 03 Market & Segment
mkt_late = df.groupby('Market')['Late_delivery_risk'].mean().sort_values(ascending=False)
seg_late = df.groupby('Customer Segment')['Late_delivery_risk'].mean().sort_values(ascending=False)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(mkt_late.index, mkt_late.values * 100, color=sns.color_palette('Set1', len(mkt_late)))
axes[0].set_title('Late Rate by Market', fontweight='bold'); axes[0].tick_params(axis='x', rotation=15)
for i, v in enumerate(mkt_late.values):
    axes[0].text(i, v * 100 + 0.3, f'{v*100:.1f}%', ha='center', fontweight='bold', fontsize=10)
axes[1].bar(seg_late.index, seg_late.values * 100, color=sns.color_palette('Set2', 3))
axes[1].set_title('Late Rate by Customer Segment', fontweight='bold')
for i, v in enumerate(seg_late.values):
    axes[1].text(i, v * 100 + 0.3, f'{v*100:.1f}%', ha='center', fontweight='bold', fontsize=10)
plt.tight_layout(); save_chart('03_market_segment_analysis.png')

# 04 Shipping days
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for lbl, col, nm in [(0, '#2ecc71', 'On Time'), (1, '#e74c3c', 'Late')]:
    sub = df[df['Late_delivery_risk'] == lbl]
    axes[0].hist(sub['Days for shipping (real)'], bins=20, alpha=0.6, color=col, label=nm, edgecolor='white')
    axes[1].hist(sub['shipping_delay'], bins=20, alpha=0.6, color=col, label=nm, edgecolor='white')
axes[0].set_title('Real Shipping Days', fontweight='bold'); axes[0].legend()
axes[1].axvline(0, color='black', linestyle='--')
axes[1].set_title('Shipping Delay (Real - Scheduled)', fontweight='bold'); axes[1].legend()
plt.tight_layout(); save_chart('04_shipping_days_distribution.png')

# 05 Correlation heatmap
num_cols = df.select_dtypes(include='number').columns.tolist()
corr = df[num_cols].corr()
fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(corr, mask=np.triu(np.ones_like(corr, dtype=bool)), annot=True, fmt='.2f',
            cmap='RdYlGn', center=0, linewidths=0.5, ax=ax, annot_kws={'size': 7})
ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
plt.tight_layout(); save_chart('05_correlation_heatmap.png')
print("  Charts 01-05 saved.")

# ── 4. Preprocessing ──────────────────────────────────────────────────────────
print("\n[4/10] Preprocessing...")
drop_cols = ['Customer Fname', 'Customer Lname', 'Customer Street', 'Customer Zipcode',
             'Customer Id', 'Order Customer Id', 'Latitude', 'Longitude',
             'Delivery Status',   # data leakage — directly reveals the target
             'Order City', 'Order Country', 'Order State',
             'Category Id', 'Department Id',
             'Customer City', 'Customer State', 'Customer Country']
drop_cols = [c for c in drop_cols if c in df.columns]
df_model  = df.drop(columns=drop_cols).dropna()
print(f"  After preprocessing: {df_model.shape[0]:,} rows x {df_model.shape[1]} columns")

cat_cols = df_model.select_dtypes(include='object').columns.tolist()
label_encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col].astype(str))
    label_encoders[col] = le
print(f"  Encoded {len(cat_cols)} categorical columns.")

# ── 5. Split & Scale ──────────────────────────────────────────────────────────
print("\n[5/10] Splitting and scaling...")
TARGET = 'Late_delivery_risk'
X = df_model.drop(columns=[TARGET])
y = df_model[TARGET]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

pickle.dump(scaler,               open(os.path.join(MODELS_DIR, 'scaler.pkl'),          'wb'))
pickle.dump(label_encoders,       open(os.path.join(MODELS_DIR, 'label_encoders.pkl'),  'wb'))
pickle.dump(X.columns.tolist(),   open(os.path.join(MODELS_DIR, 'feature_names.pkl'),   'wb'))
print(f"  Train: {X_train.shape} | Test: {X_test.shape}")

# ── 6. Train Models ───────────────────────────────────────────────────────────
print("\n[6/10] Training models (takes 2-5 minutes)...")

print("  [1/3] Logistic Regression...")
lr = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
lr.fit(X_train_sc, y_train)
print("        done ✓")

print("  [2/3] Random Forest (200 trees)...")
rf = RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_split=10,
                            class_weight='balanced', random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
print("        done ✓")

if USE_XGB:
    print("  [3/3] XGBoost...")
    boost = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1,
                          subsample=0.8, colsample_bytree=0.8,
                          scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
                          eval_metric='logloss', random_state=42, n_jobs=-1)
    boost_name = 'XGBoost'
else:
    print("  [3/3] Gradient Boosting...")
    boost = GradientBoostingClassifier(n_estimators=200, max_depth=5,
                                       learning_rate=0.1, subsample=0.8, random_state=42)
    boost_name = 'Gradient Boosting'
boost.fit(X_train, y_train)
print("        done ✓")

# ── 7. Evaluate & Charts 06-08 ────────────────────────────────────────────────
print("\n[7/10] Evaluating models...")

def evaluate(name, model, Xu, yt):
    yp  = model.predict(Xu)
    ypr = model.predict_proba(Xu)[:, 1]
    return {'Model': name,
            'Accuracy':  round(accuracy_score(yt, yp),  4),
            'Precision': round(precision_score(yt, yp), 4),
            'Recall':    round(recall_score(yt, yp),    4),
            'F1 Score':  round(f1_score(yt, yp),        4),
            'ROC-AUC':   round(roc_auc_score(yt, ypr),  4)}

models_info = [('Logistic Regression', lr, X_test_sc),
               ('Random Forest',       rf, X_test),
               (boost_name,            boost, X_test)]

results_df = pd.DataFrame([evaluate(n, m, Xu, y_test) for n, m, Xu in models_info]).set_index('Model')
print("\n" + "─" * 62)
print(results_df.to_string())
print("─" * 62)
results_df.to_csv(os.path.join(REPORTS_DIR, 'model_results.csv'))

# Chart 06 model comparison
fig, ax = plt.subplots(figsize=(13, 6))
metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC-AUC']
x = np.arange(len(metrics)); w = 0.25
for i, (idx, row) in enumerate(results_df.iterrows()):
    bars = ax.bar(x + i * w, [row[m] for m in metrics], w,
                  label=idx, color=['#3498db', '#2ecc71', '#e74c3c'][i],
                  alpha=0.85, edgecolor='white')
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                f'{bar.get_height():.3f}', ha='center', fontsize=8)
ax.set_xticks(x + w); ax.set_xticklabels(metrics); ax.set_ylim(0.4, 1.08)
ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold'); ax.legend()
plt.tight_layout(); save_chart('06_model_comparison.png')

# Chart 07 ROC curves
fig, ax = plt.subplots(figsize=(9, 7))
for (name, model, Xu), lc in zip(models_info, ['#3498db', '#2ecc71', '#e74c3c']):
    ypr = model.predict_proba(Xu)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, ypr)
    ax.plot(fpr, tpr, lw=2.5, color=lc,
            label=f'{name} (AUC={roc_auc_score(y_test, ypr):.4f})')
ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random Baseline')
ax.set_xlabel('False Positive Rate', fontsize=12); ax.set_ylabel('True Positive Rate', fontsize=12)
ax.set_title('ROC Curves', fontsize=14, fontweight='bold'); ax.legend(loc='lower right'); ax.grid(alpha=0.3)
plt.tight_layout(); save_chart('07_roc_curves.png')

# Chart 08 Confusion matrices
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for ax, (name, model, Xu) in zip(axes, models_info):
    yp = model.predict(Xu); cm = confusion_matrix(y_test, yp)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['On Time', 'Late'], yticklabels=['On Time', 'Late'])
    ax.set_title(f'{name}\nAcc: {accuracy_score(y_test,yp):.3f}', fontweight='bold')
    ax.set_xlabel('Predicted'); ax.set_ylabel('Actual')
plt.tight_layout(); save_chart('08_confusion_matrices.png')
print("  Charts 06-08 saved.")

# ── 8. Feature Importance Charts 09-10 ───────────────────────────────────────
print("\n[8/10] Feature importance charts...")
gb_fi = pd.Series(boost.feature_importances_, index=X.columns).sort_values(ascending=False).head(20)
fig, ax = plt.subplots(figsize=(10, 8))
fi_colors = ['#e74c3c' if i < 3 else '#3498db' for i in range(len(gb_fi))]
ax.barh(gb_fi.index[::-1], gb_fi.values[::-1], color=fi_colors[::-1], edgecolor='white')
ax.set_title(f'{boost_name} — Top 20 Feature Importances', fontsize=14, fontweight='bold')
ax.set_xlabel('Importance Score')
plt.tight_layout(); save_chart('09_feature_importance.png')

rf_fi = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(20)
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
for ax_i, (name, fi, color) in zip(axes, [(boost_name, gb_fi, '#e74c3c'), ('Random Forest', rf_fi, '#2ecc71')]):
    ax_i.barh(fi.index[::-1], fi.values[::-1], color=color, alpha=0.82, edgecolor='white')
    ax_i.set_title(f'{name}\nTop 20 Feature Importances', fontweight='bold')
    ax_i.set_xlabel('Importance Score')
plt.tight_layout(); save_chart('10_feature_importance_comparison.png')
print("  Charts 09-10 saved.")

# ── 9. Risk Categories Chart 11 ───────────────────────────────────────────────
print("\n[9/10] Risk categorisation...")
best_name  = results_df['ROC-AUC'].idxmax()
best_model = {'Logistic Regression': lr, 'Random Forest': rf, boost_name: boost}[best_name]
X_best     = X_test_sc if best_name == 'Logistic Regression' else X_test
probs      = best_model.predict_proba(X_best)[:, 1]
risk_cats  = ['Low' if p < 0.35 else ('Medium' if p < 0.65 else 'High') for p in probs]
risk_cts   = pd.Series(risk_cats).value_counts().reindex(['Low', 'Medium', 'High']).fillna(0)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(risk_cts.index, risk_cts.values,
            color=['#2ecc71', '#f39c12', '#e74c3c'], edgecolor='white', linewidth=1.5)
axes[0].set_title('Risk Category Distribution (Test Set)', fontweight='bold')
axes[0].set_ylabel('Number of Shipments')
for i, v in enumerate(risk_cts.values):
    axes[0].text(i, v + 100, f'{int(v):,}', ha='center', fontweight='bold')
axes[1].hist(probs, bins=50, color='#3498db', edgecolor='white', alpha=0.8)
axes[1].axvline(0.35, color='#f39c12', linestyle='--', lw=2, label='Low→Medium (0.35)')
axes[1].axvline(0.65, color='#e74c3c', linestyle='--', lw=2, label='Medium→High (0.65)')
axes[1].set_title('Late Delivery Probability Distribution', fontweight='bold')
axes[1].set_xlabel('P(Late Delivery)'); axes[1].set_ylabel('Count'); axes[1].legend()
plt.tight_layout(); save_chart('11_risk_categories.png')
print(f"  Best model: {best_name}")

# ── 10. Save Models ───────────────────────────────────────────────────────────
print("\n[10/10] Saving all model artifacts...")
pickle.dump(best_model, open(os.path.join(MODELS_DIR, 'best_model.pkl'), 'wb'))
pickle.dump({'Logistic Regression': lr, 'Random Forest': rf, boost_name: boost},
            open(os.path.join(MODELS_DIR, 'all_models.pkl'), 'wb'))
pickle.dump(boost_name, open(os.path.join(MODELS_DIR, 'boost_name.pkl'), 'wb'))

print("  best_model.pkl   saved")
print("  all_models.pkl   saved")
print("  scaler.pkl       saved")
print("  label_encoders.pkl  saved")
print("  feature_names.pkl   saved")
print("  boost_name.pkl   saved")

print("\n" + "=" * 62)
print("  PIPELINE COMPLETE!")
print("=" * 62)
print(f"\n  charts/  -> {CHARTS_DIR}")
print(f"  models/  -> {MODELS_DIR}")
print(f"  reports/ -> {REPORTS_DIR}")
print()
print("  LAUNCH THE DASHBOARD (copy this command):")
print()
print("  python -m streamlit run streamlit_app\\app.py")
print()
print("  Then open: http://localhost:8501")
print("=" * 62)
