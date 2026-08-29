# FORESIGHT — Machine Learning Explainability & Driver Decomposition Report

**Audit Timestamp:** `2026-08-29T20:59:41.045237`  
**Forecasting Model:** `XGBoost`  
**Explainability Methodology:** TreeSHAP (Additive Shapley Values)  
**Evaluation Sample Size:** `2,000` observations  

---

## 1. Top 15 Global Demand Drivers (SHAP Value Ranking)

| Rank | Feature Name | Feature Group | Mean |SHAP| (Units) | Relative Share |
| :---: | :--- | :---: | :---: | :---: |
| 1 | `rolling_mean_28` | `rolling_stats` | **8.832** | `35.5%` |
| 2 | `day_of_week` | `temporal` | **2.242** | `9.0%` |
| 3 | `rolling_mean_14` | `rolling_stats` | **2.145** | `8.6%` |
| 4 | `discount_percentage` | `pricing_promo` | **1.205** | `4.8%` |
| 5 | `price_ratio` | `pricing_promo` | **1.196** | `4.8%` |
| 6 | `month` | `temporal` | **0.921** | `3.7%` |
| 7 | `inventory_level` | `operational` | **0.715** | `2.9%` |
| 8 | `is_weekend` | `temporal` | **0.710** | `2.9%` |
| 9 | `lag_56` | `autoregressive_lag` | **0.689** | `2.8%` |
| 10 | `units_on_order` | `categorical_hierarchy` | **0.602** | `2.4%` |
| 11 | `week_of_year` | `temporal` | **0.548** | `2.2%` |
| 12 | `lag_1` | `autoregressive_lag` | **0.542** | `2.2%` |
| 13 | `rolling_mean_7` | `rolling_stats` | **0.453** | `1.8%` |
| 14 | `lag_28` | `autoregressive_lag` | **0.322** | `1.3%` |
| 15 | `inventory_ratio` | `operational` | **0.316** | `1.3%` |

---

## 2. Feature Group Importance Breakdown

| Feature Category | Aggregate Relative Impact (%) |
| :--- | :---: |
| `rolling_stats` | **49.4%** |
| `temporal` | **19.2%** |
| `pricing_promo` | **11.3%** |
| `autoregressive_lag` | **8.3%** |
| `operational` | **5.8%** |
| `categorical_hierarchy` | **4.7%** |
| `velocity_trend` | **1.1%** |

---

## 3. Sample Local Forecast Explanations & Business Narratives

### Explanation #1: SKU `SKU-1001` at Store `STORE-001` (2023-02-27 00:00:00)
- **Baseline Demand \(E[y]\):** `29.0 units`
- **Predicted Demand \(\hat{y}\):** **54.5 units**
- **Executive Narrative:** *Forecast for SKU-1001 is 54.5 units (88.2% above baseline of 29.0 units). Primary upward drivers include: rolling_mean_28 (+12.8 units), favorable price point (+6.4 units), rolling_mean_14 (+3.1 units). Partially dampened by: mid-week low seasonality (-2.2 units), month (-1.3 units).*

| Driver Feature | Actual Value | Impact on Demand |
| :--- | :---: | :---: |
| `rolling_mean_28` (Positive) | `45.29` | **+12.77 units** |
| `price_ratio` (Positive) | `0.85` | **+6.45 units** |
| `rolling_mean_14` (Positive) | `45.71` | **+3.09 units** |
| `discount_percentage` (Positive) | `0.15` | **+2.81 units** |
| `is_promoted_int` (Positive) | `1.0` | **+1.16 units** |
| `day_of_week` (Negative) | `0.0` | **-2.19 units** |
| `month` (Negative) | `2.0` | **-1.33 units** |
| `is_weekend` (Negative) | `0.0` | **-0.82 units** |
| `rolling_std_28` (Negative) | `12.1` | **-0.32 units** |
| `rolling_std_14` (Negative) | `14.91` | **-0.28 units** |

### Explanation #2: SKU `SKU-1001` at Store `STORE-001` (2024-07-10 00:00:00)
- **Baseline Demand \(E[y]\):** `29.0 units`
- **Predicted Demand \(\hat{y}\):** **41.8 units**
- **Executive Narrative:** *Forecast for SKU-1001 is 41.8 units (44.3% above baseline of 29.0 units). Primary upward drivers include: rolling_mean_28 (+10.8 units), rolling_mean_14 (+2.7 units), lag_56 (+1.0 units). Partially dampened by: mid-week low seasonality (-1.7 units), month (-1.3 units).*

| Driver Feature | Actual Value | Impact on Demand |
| :--- | :---: | :---: |
| `rolling_mean_28` (Positive) | `44.93` | **+10.85 units** |
| `rolling_mean_14` (Positive) | `45.43` | **+2.66 units** |
| `lag_56` (Positive) | `50.0` | **+1.02 units** |
| `lag_1` (Positive) | `54.0` | **+0.99 units** |
| `inventory_level` (Positive) | `1386.0` | **+0.88 units** |
| `day_of_week` (Negative) | `2.0` | **-1.74 units** |
| `month` (Negative) | `7.0` | **-1.34 units** |
| `price_ratio` (Negative) | `1.0` | **-1.07 units** |
| `discount_percentage` (Negative) | `0.0` | **-0.67 units** |
| `is_weekend` (Negative) | `0.0` | **-0.56 units** |

### Explanation #3: SKU `SKU-1001` at Store `STORE-003` (2023-07-28 00:00:00)
- **Baseline Demand \(E[y]\):** `29.0 units`
- **Predicted Demand \(\hat{y}\):** **26.0 units**
- **Executive Narrative:** *Forecast for SKU-1001 is 26.0 units (10.2% below baseline of 29.0 units). Primary upward drivers include: rolling_mean_14 (+1.3 units), rolling_mean_28 (+1.1 units), inventory_ratio (+0.6 units). Partially dampened by: units_on_order (-1.5 units), mid-week low seasonality (-1.4 units).*

| Driver Feature | Actual Value | Impact on Demand |
| :--- | :---: | :---: |
| `rolling_mean_14` (Positive) | `34.71` | **+1.32 units** |
| `rolling_mean_28` (Positive) | `30.32` | **+1.09 units** |
| `inventory_ratio` (Positive) | `2.9` | **+0.59 units** |
| `lag_1` (Positive) | `41.0` | **+0.53 units** |
| `days_of_inventory` (Positive) | `2.9` | **+0.45 units** |
| `units_on_order` (Negative) | `726.0` | **-1.54 units** |
| `day_of_week` (Negative) | `4.0` | **-1.43 units** |
| `month` (Negative) | `7.0` | **-0.93 units** |
| `week_of_year` (Negative) | `30.0` | **-0.80 units** |
| `price_ratio` (Negative) | `1.0` | **-0.73 units** |
