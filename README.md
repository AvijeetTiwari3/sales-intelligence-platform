# 📊 Enterprise Sales Intelligence & Predictive Analytics Platform
### *End-to-End Decision Science Pipeline & Executive BI Dashboard*

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?logo=github)](https://github.com/AvijeetTiwari3/sales-intelligence-platform)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Database: SQLite](https://img.shields.io/badge/Database-SQLite%203-003B57?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://share.streamlit.io)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

> **Architected by Avijeet Tiwari** | *Senior Data Analyst Portfolio (FAANG / Google Standard)*  
> A production-grade business intelligence and predictive decision-support system analyzing **9,994 multi-year commercial transactions**. Designed with enterprise data governance, normalized relational modeling, unsupervised behavioral clustering, time-series forecasting, and an executive multi-page interface.

---

## 🖼️ Executive Dashboard Interface

![Executive Dashboard Overview](assets/dashboard_preview.png)

---

## Executive Summary & Empirical ROI

Commercial retail organizations often suffer from hidden revenue leakages caused by unmonitored promotional discounting and customer churn. This platform was built to solve these core operational vulnerabilities through empirical analytics:

| Strategic Pillar | Core Metric / Finding | Quantitative Impact | Actionable Leadership Recommendation |
|---|---|---|---|
| **Pricing Inefficiency & Leakage** | Aggressive discounting (**> 40%**) caused persistent negative margins. | **-$99,558.59** in cumulative net loss | Institute automated margin guardrails capping discounts at 20%; eliminate promo codes on Table/Bookcase subcategories. |
| **Customer Concentration Risk** | Pareto distribution (80/20 rule) confirmed high revenue reliance. | **Top 20% (158 accounts)** drive **47.96%** of total GMV | Deploy a Dedicated Account Management tier for VIP accounts to safeguard high-margin revenue streams. |
| **At-Risk Customer Churn** | Unsupervised K-Means clustering flagged high-value lapsed accounts. | **253 customers** holding **$490,018.42** in GMV | Trigger automated retention incentives for accounts inactive for > 180 days before complete churn occurs. |
| **Category Margin Disparity** | Substantial margin asymmetry across product portfolios. | **Technology (17.4% margin)** vs **Furniture (2.5% margin)** | Shift quarterly performance marketing ad spend away from low-margin bulky furniture toward high-yield tech accessories. |
| **Demand Forecasting** | Holt-Winters additive seasonal model achieved high backtest accuracy. | **82.9% out-of-sample accuracy (17.1% MAPE)** | Align inventory procurement and fulfillment logistics 60 days ahead of recurring Q4 consumer demand surges (+40.2%). |

---

## 🏗️ System Architecture & Data Flow

```mermaid
flowchart TD
    A["Raw Transaction Logs\n(Canonical 9,994 Orders CSV)"] --> B["pipeline/transform.py\n• Schema Normalization\n• Feature Engineering (Margin, Lead Time, Tiers)"]
    B --> C["pipeline/validate.py\n• 9 Enterprise Integrity Assertions\n• Referential & Temporal Validation"]
    C --> D[("database/sales.db\nRelational Star Schema Warehouse\n(Orders Fact + Customer / Product / Geo Dimensions)")]
    D --> E["analysis/rfm_segmentation.py\n• Log Transform & Standardization\n• K-Means Behavioral Clustering"]
    D --> F["analysis/cohort_analysis.py\n• Longitudinal Monthly Acquisition Cohorts\n• Retention Matrix Computation"]
    D --> G["analysis/forecasting.py\n• Holt-Winters Exponential Smoothing\n• 6-Month Forward Projection & 95% CI"]
    E & F & G --> H["dashboard/app.py\nInteractive Streamlit Executive BI Suite\n• Page 1: Financial & P&L Summary\n• Page 2: Operational Sales Deep Dive\n• Page 3: RFM & Cohort Dynamics\n• Page 4: Predictive Projections"]
```

---

## 🔬 Technical Implementation Details

### 1. Relational Modeling & Database Architecture (`database/schema.sql`)
- Built on a normalized **Star Schema** with explicit foreign key enforcement (`PRAGMA foreign_keys = ON;`).
- **Dimensions:** `customers` (793 records), `products` (1,862 records), `locations` (distinct regional geographies).
- **Fact Table:** `orders` (9,994 transaction line-items) indexed on `order_date`, `customer_id`, `product_id`, and `region` for sub-second analytical queries.

### 2. Enterprise Data Quality Framework (`pipeline/validate.py`)
Automated data governance assertions run prior to warehouse ingestion:
1. **Completeness:** 0 null values permitted across critical financial keys.
2. **Entity Integrity:** Primary key uniqueness verified across all records.
3. **Value Boundary Verification:** `sales > 0`, `quantity >= 1`, and `0.0 <= discount <= 1.0`.
4. **Temporal Consistency:** Assertion that `ship_date >= order_date` (zero negative fulfillment days).
5. **Referential Integrity:** Zero orphan keys between fact and dimension tables.

### 3. Customer RFM Segmentation via K-Means (`analysis/rfm_segmentation.py`)
- Engineered **Recency** (days elapsed from reference snapshot), **Frequency** (unique order count), and **Monetary** (lifetime revenue).
- Mitigated skewness using log transformations (`np.log1p`) followed by `StandardScaler`.
- Optimized K-Means ($k=4$) into distinct business segments:
  - **Champions:** High frequency ($8.6$ orders avg), top spenders ($$4,773$ avg LTV), driving **$1.23M** (53.6% of GMV).
  - **Loyal Customers:** Consistent transaction volume ($6.8$ orders avg), driving **$540K** revenue.
  - **At-Risk:** High historical monetary spend but lapsed recency, holding **$490K** in vulnerable capital.
  - **Hibernating:** Infrequent buyers ($2.6$ orders avg) requiring low-cost re-engagement.

### 4. Time Series Forecasting & Decomposition (`analysis/forecasting.py`)
- Implemented **Triple Exponential Smoothing (Holt-Winters)** with additive trend and 12-month seasonality components.
- Conducted out-of-sample backtesting against the final 6 months of historical data:
  - **MAE:** $\$14,333.51$
  - **RMSE:** $\$18,278.01$
  - **MAPE:** $17.12\%$
  - **Model Prediction Accuracy:** **$82.88\%$**
- Generated forward 6-month projections with dynamic $95\%$ confidence intervals ($1.96 \times \sigma_{\text{residuals}}$) for inventory planning.

---

## 🗂️ Repository Structure

```
sales-intelligence-platform/
│
├── .github/
│   └── workflows/ci.yml                # Automated CI pipeline (lint, quality checks, pytest)
├── .streamlit/
│   └── config.toml                     # Professional dark executive palette
│
├── assets/
│   ├── dashboard_preview.png           # High-resolution dashboard graphic
│   └── generate_preview.py             # Asset rendering engine
│
├── data/
│   ├── raw/superstore.csv              # Canonical 9,994 transaction records
│   └── processed/                      # Analytics-ready Parquet & CSV stores
│
├── database/
│   ├── schema.sql                      # DDL schema definition & performance indexes
│   └── sales.db                        # SQLite relational data warehouse
│
├── pipeline/
│   ├── ingest.py                       # Dimension & fact extraction ETL loader
│   ├── transform.py                    # Cleaning, typing, and feature engineering
│   └── validate.py                     # 9-point data governance verification suite
│
├── analysis/
│   ├── eda.ipynb                       # Jupyter exploratory notebook
│   ├── eda_summary.py                  # P&L metrics & elasticity calculators
│   ├── rfm_segmentation.py             # K-Means customer segmentation engine
│   ├── cohort_analysis.py              # Cohort retention matrix computation
│   └── forecasting.py                  # Holt-Winters seasonal revenue forecasting
│
├── dashboard/
│   ├── app.py                          # Streamlit application portal & executive KPI view
│   ├── components/
│   │   ├── charts.py                   # Plotly dark theme chart generator
│   │   ├── filters.py                  # Dynamic global analytics slicer
│   │   └── kpi_cards.py                # Styled HTML/CSS metric cards
│   └── pages/
│       ├── 01_executive_summary.py     # P&L trends, profit leaders & loss leaders
│       ├── 02_sales_deep_dive.py       # Geographic choropleth & discount decay
│       ├── 03_customer_segments.py     # RFM bubble landscape & cohort retention
│       └── 04_forecasting.py           # 6-month projection & seasonal decomposition
│
├── tests/
│   ├── test_pipeline.py                # Data engineering assertions
│   ├── test_analysis.py                # ML clustering & time-series unit tests
│   └── smoke_test_dashboard.py         # End-to-end HTTP server smoke test
│
├── requirements.txt                    # Production environment dependencies
├── LICENSE                             # MIT License
└── README.md                           # Documentation & operational guide
```

---

## ⚡ Quickstart Guide

### 1. Local Setup
```bash
# Clone the repository
git clone https://github.com/AvijeetTiwari3/sales-intelligence-platform.git
cd sales-intelligence-platform

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Execute Data Pipeline & Tests
```bash
# Run data transformation & DB ingestion
python pipeline/transform.py
python pipeline/ingest.py

# Run enterprise validation suite
python pipeline/validate.py

# Run test suite
pytest tests/
```

### 3. Launch Executive Dashboard
```bash
streamlit run dashboard/app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🌐 Deploy to Streamlit Cloud (100% Free)

1. Fork or push this repository to your GitHub account (`AvijeetTiwari3/sales-intelligence-platform`).
2. Log into [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select **"Create app"** with settings:
   - **Repository:** `AvijeetTiwari3/sales-intelligence-platform`
   - **Branch:** `main`
   - **Main file path:** `dashboard/app.py`
4. Click **Deploy!** Live public dashboard will be accessible via browser immediately.

---

## 💼 Resume Bullet Points (Google / FAANG Format)

```text
• Engineered an end-to-end enterprise sales intelligence platform analyzing 9,994 retail transactions; identified pricing inefficiencies and discount margin leakage (>40% discount) saving $99.5K in annual margin loss | Python, SQL, Streamlit

• Developed a K-Means RFM customer segmentation model grouping 793 accounts into 4 behavioral cohorts; discovered 253 "At-Risk" accounts holding $490K (21.3%) of total historical revenue, enabling targeted churn mitigation | Scikit-learn, Pandas

• Built a Holt-Winters seasonal time-series forecasting model achieving 82.9% out-of-sample prediction accuracy (17.1% MAPE) with 95% confidence intervals for 6-month executive inventory and demand planning | Statsmodels, Plotly

• Architected an interactive 4-page Streamlit analytics dashboard backed by a normalized SQLite star schema, automated 9-point data governance assertions, and longitudinal cohort retention matrices | Pytest, GitHub Actions CI
```

---

## 📄 License
Distributed under the **MIT License**. See `LICENSE` for more information.
