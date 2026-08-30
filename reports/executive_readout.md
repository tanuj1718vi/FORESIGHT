# 🔮 Project FORESIGHT — Executive Readout & Strategic Action Memo

**Client:** NorthBay Living (D2C Home & Lifestyle Brand)  
**Target Audience:** Head of Operations & Finance Lead  
**Engagement:** 4-Week Data Science & Analytics Engagement (Zidio Development)  
**Date:** August 2026  
**Document Version:** 1.0 (Executive Delivery)  

---

## Executive Summary (The Bottom Line)

NorthBay Living's current spreadsheet-based inventory planning has created two simultaneous balance-sheet drains: **stockouts on fast movers** (causing unrecoverable lost margin) and **overstocking on slow movers** (locking up working capital and generating carrying costs).

Project **FORESIGHT** replaces guesswork with an **AI-driven probabilistic demand forecasting and automated risk decisioning engine**. Across the active portfolio, FORESIGHT has diagnosed:

* **₹1,99,17,055 (Lost Gross Margin at Risk):** Unfulfilled customer demand across 50 critical SKU-Store nodes due to stock depletion before replenishment arrives.
* **₹1,10,66,531/year (Excess Working Capital & Holding Penalty):** Tied-up cash in stagnant inventory across slow-moving lines.
* **Total Addressable Financial Exposure:** **₹3,09,83,586** across the distribution network.
* **Forecast Accuracy Improvement:** The production **XGBoost Demand Forecaster** achieved a **18.94% WAPE**, outperforming the seasonal-naive baseline (48.65% WAPE) by **61.1%**, eliminating guesswork and preventing bullwhip replenishment.

---

## Slide 1: Engagement Scope & Problem Statement

### The Core Operational Challenge
> *"Every month we stock out of things people want and sit on things they don't. We're guessing how much to order and when."* — Head of Operations, NorthBay Living

```
           TRADITIONAL GUESSWORK                   PROJECT FORESIGHT (AI PLATFORM)
┌─────────────────────────────────────────┐     ┌─────────────────────────────────────────┐
│ • Spreadsheet heuristics & gut feel     │     │ • Multi-lag machine learning forecast   │
│ • Fixed reorder rules ignoring lead-time│ ──> │ • Dynamic Safety Stock & EOQ calculation│
│ • Blind to promo surges & seasonal waves│     │ • 4-Quadrant Stockout vs Overstock Risk │
│ • High stockout rate + trapped cash     │     │ • Clear work orders: Reorder, Markdown  │
└─────────────────────────────────────────┘     └─────────────────────────────────────────┘
```

---

## Slide 2: Financial Impact & Quantified Value at Stake

```
                      ENTERPRISE FINANCIAL EXPOSURE
┌───────────────────────────────────┬───────────────────┬───────────────────────────────┐
│ Financial Metric                  │ Value (₹ INR)     │ Business Implication          │
├───────────────────────────────────┼───────────────────┼───────────────────────────────┤
│ Lost Gross Margin Risk (Stockouts)│ ₹1,99,17,055      │ Revenue lost to competitors   │
│ Excess Holding Cost Penalty       │ ₹1,10,66,531 / yr │ Working capital trapped       │
│ Average Working Inventory Value   │ ₹3,49,35,338      │ Total capital tied in stock   │
│ Combined Addressable Exposure     │ ₹3,09,83,586      │ Direct balance-sheet recovery │
└───────────────────────────────────┴───────────────────┴───────────────────────────────┘
```

### Key Financial Takeaways:
1. **Stockout Prevention Protects Revenue:** 20.0% of SKU replenishment nodes are in imminent danger of stockout within their replenishment lead-time window.
2. **Capital Release from Overstock:** Liquidating and markdown-clearing the top overstocked lines frees up over **₹35,00,000 in immediate cash flow**.

---

## Slide 3: Model Accuracy & Honest Baseline Comparison

In accordance with strict client-grade data science governance, every model was benchmarked using **3-Fold Rolling-Origin Walk-Forward Cross-Validation** (strictly preventing data leakage).

| Rank | Model Candidate | Model Family | WAPE (Primary Metric) | RMSE | R² Score | Decision Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 🥇 | **XGBoost Forecaster** | Gradient Boosted Trees | **18.94%** | **10.36** | **0.863** | **Selected Champion** |
| 🥈 | LightGBM / HistGBM | Histogram Gradient Boosting | 19.12% | 10.43 | 0.862 | Production Contender |
| 🥉 | Quantile Regressor (P10/P50/P90) | Gradient Boosting | 20.23% | 11.47 | 0.833 | Uncertainty Engine |
| 4 | Random Forest | Bagged Ensembles | 20.33% | 11.06 | 0.844 | Benchmark |
| 5 | Ridge Linear Regression | Regularized Linear Model | 30.49% | 16.96 | 0.634 | Linear Benchmark |
| 6 | Simple Moving Average (7-Day) | Statistical Baseline | 36.93% | 20.51 | 0.465 | Baseline |
| 7 | **Seasonal-Naive Baseline** | Persistence ($y_{t-7}$) | **48.65%** | **27.42** | **0.042** | **Reference Baseline** |

### Accuracy Finding:
* **The Champion Model beats the Seasonal-Naive baseline by 29.71 percentage points (a 61.1% relative reduction in forecast error)**.
* **Uncertainty Bounds:** The Quantile Forecaster produces calibrated 10th and 90th percentile demand intervals to ensure safety stock is sized for 95% service level during promotional spikes.

---

## Slide 4: The 4-Quadrant Risk Decisioning Framework

The FORESIGHT Risk Layer categorizes all SKUs across an intuitive $2 \times 2$ grid:

```
 STOCKOUT RISK (Lead-time demand vs Net Stock)
    ▲
1.0 ┼──────────────────────────────┬──────────────────────────────┐
    │     🚨 REORDER / EXPEDITE    │     ⚠️ WATCH / VOLATILE     │
    │  • Stockout Prob > 70%       │  • Erratic demand spikes     │
    │  • Action: Emergency PO /    │  • Action: Manual review &   │
    │    supplier expediting       │    lead-time re-negotiation  │
0.5 ┼──────────────────────────────┼──────────────────────────────┤
    │     ✅ HEALTHY BUFFER        │     🏷️ MARKDOWN / CLEAR      │
    │  • Days of Supply aligned    │  • Days of Supply > 45 days  │
    │  • Action: Routine auto-ROP  │  • Action: Promotional promo │
    │    monitoring                │    to release tied-up cash   │
0.0 ┴──────────────────────────────┴──────────────────────────────►
   0.0                            0.5                            1.0
                 OVERSTOCK RISK (On-hand vs Forward Demand)
```

### Action Distribution Across 250 Inventory Nodes:
* **MONITOR (Healthy):** 102 Nodes (40.8%) — Maintain standard automated reordering.
* **EXPEDITE / ORDER (Critical Stockout):** 115 Nodes (46.0%) — Trigger immediate purchase orders.
* **HOLD / REDUCE (Overstocked):** 33 Nodes (13.2%) — Halt inbound purchase orders and initiate markdowns.
* **REBALANCE (Lateral Multi-Store Transfers):** 4 Cross-store transfers identified to eliminate stockouts without purchasing new inventory.

---

## Slide 5: Immediate Action Plan for Operations & Merchandising

### Top Immediate Actions for Operations (Next 48 Hours)

1. **Expedite Critical Orders for High-Velocity Movers:**
   * `SKU-1022`: 0.2 Days of Supply remaining (Lead time: 23 days). Raise emergency PO for 1,429 units (Protects ₹23,61,000 gross margin).
   * `SKU-1001`: 0.0 Days of Supply remaining (Lead time: 19 days). Raise PO for 1,089 units (Protects ₹19,18,000 gross margin).
   * `SKU-1033`: Raise PO for 874 units (Protects ₹14,93,000 gross margin).

2. **Execute Lateral Stock Transfers:**
   * Transfer surplus units of `SKU-1001` and `SKU-1011` from Store 4 (overstocked) to Store 1 and Store 5 (stockout danger), saving ₹18,00,000 without supplier lead-time lag.

3. **Initiate Promotional Clearance on Stagnant Lines:**
   * Implement a 20% discount on `SKU-1026` and `SKU-1040` (Class CZ lines) in Store 4 to liberate ₹15,00,000 in working capital before carrying costs compound.

---

## Slide 6: Productized Delivery & Handover

The operations and leadership teams do not need to read Python notebooks. Project FORESIGHT is delivered as a turnkey software suite:

1. **Interactive Streamlit Planning Dashboard (`http://localhost:8501`)**:
   * **Executive Overview:** Real-time KPI scorecard, portfolio revenue, and risk tier distribution.
   * **Forecast Explorer:** Interactive historical demand vs. XGBoost forecast with 80% confidence ribbons.
   * **Inventory & ROP Engine:** Live safety stock, continuous review reorder points, and EOQ calculators.
   * **Financial Risk Grid:** Interactive $2 \times 2$ stockout vs overstock bubble chart sized by revenue at risk.
   * **Prescriptive Work Orders:** Downloadable CSV procurement sheets with one-click filtering.
   * **What-If Scenario Simulator:** Live slider to test supplier lead-time delays and promotional spikes.

2. **FastAPI REST Microservice (`http://localhost:8000/docs`)**:
   * Production-grade REST API endpoints for real-time predictions (`/api/v1/forecast/predict`), batch scoring, risk assessment, and explainability narratives.

3. **Automated End-to-End Pipeline (`python run_pipeline.py`)**:
   * Reproducible single-command pipeline performing ingestion, 11-point data validation, feature engineering, model training, risk evaluation, and drift monitoring.

---

## Slide 7: Governance, Limitations & Roadmap

### Honest Limitations:
* **Cold-Start SKUs:** Products with less than 28 days of transaction history rely on category-level median demand priors until individual velocity stabilizes.
* **Supplier Lead-Time Volatility:** Unannounced supplier delays beyond recorded lead times require buffer adjustments via the What-If stress tool.

### Next Steps & MLOps Monitoring:
* Automated monthly retraining triggered whenever the **Kolmogorov-Smirnov (KS) drift test** or **Population Stability Index (PSI > 0.25)** flags distributional shifts.
* Bi-weekly inventory rebalance audits to optimize cross-facility stock movements.
