# FORESIGHT — Enterprise MLOps & Drift Monitoring Report

**Audit Timestamp:** `2026-08-29T20:59:43.535515`  
**Production Champion Model:** `XGBoost`  
**Reference Baseline Window:** `134,800` samples  
**Production Evaluation Window:** `33,700` samples  

---

## 1. Executive Concept Drift & Retraining Decision

| Metric | Value | Operational Status |
| :--- | :---: | :--- |
| **Baseline Validation WAPE** | `18.94%` | Reference benchmark |
| **Current Production Rolling WAPE** | **`17.21%`** | Live performance |
| **Performance Degradation Delta** | `-9.1%` | Threshold: +25% |
| **Prescriptive Retraining Directive** | **`NO_ACTION`** | Automated governance rule |

> **Audit Justification:** *Model performance remains stable: Current WAPE (17.21%) meets benchmark (18.94%).*

---

## 2. Feature Distribution Shift (KS Test & Population Stability Index)

- **Total Monitored Predictors:** `48`
- **Drifted Features Detected:** **`33`** / `48`

| Feature Name | KS Statistic (D) | KS p-value | PSI Score | Drift Severity | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `price` | `0.0020` | `0.9999` | `0.0001` | `NO_DRIFT` | **🟢 STABLE** |
| `inventory_level` | `0.0560` | `0.0000` | `0.0265` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `units_on_order` | `0.0498` | `0.0000` | `0.0078` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `unit_price` | `0.0002` | `1.0000` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |
| `unit_cost` | `0.0002` | `1.0000` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |
| `lead_time_days` | `0.0003` | `1.0000` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |
| `min_order_qty` | `0.0001` | `1.0000` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |
| `day_of_week` | `0.0056` | `0.3729` | `0.0003` | `NO_DRIFT` | **🟢 STABLE** |
| `day_of_month` | `0.0631` | `0.0000` | `0.0150` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `week_of_year` | `0.7400` | `0.0000` | `5.1214` | `SIGNIFICANT_DRIFT` | **🔴 DRIFT** |
| `month` | `0.6843` | `0.0000` | `5.6578` | `SIGNIFICANT_DRIFT` | **🔴 DRIFT** |
| `quarter` | `0.5694` | `0.0000` | `5.0165` | `SIGNIFICANT_DRIFT` | **🔴 DRIFT** |
| `year` | `0.5731` | `0.0000` | `0.0000` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `is_weekend` | `0.0019` | `1.0000` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |
| `sin_day_of_week` | `0.0056` | `0.3729` | `0.0004` | `NO_DRIFT` | **🟢 STABLE** |
| `cos_day_of_week` | `0.0074` | `0.1024` | `0.0002` | `NO_DRIFT` | **🟢 STABLE** |
| `sin_month` | `0.6843` | `0.0000` | `6.1719` | `SIGNIFICANT_DRIFT` | **🔴 DRIFT** |
| `cos_month` | `0.2133` | `0.0000` | `0.9341` | `SIGNIFICANT_DRIFT` | **🔴 DRIFT** |
| `lag_1` | `0.0589` | `0.0000` | `0.0323` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `lag_7` | `0.0512` | `0.0000` | `0.0251` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `lag_14` | `0.0437` | `0.0000` | `0.0187` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `lag_21` | `0.0357` | `0.0000` | `0.0129` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `lag_28` | `0.0309` | `0.0000` | `0.0082` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `lag_56` | `0.0124` | `0.0005` | `0.0013` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_mean_7` | `0.0599` | `0.0000` | `0.0278` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_std_7` | `0.0849` | `0.0000` | `0.0478` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_min_7` | `0.0565` | `0.0000` | `0.0278` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_max_7` | `0.0672` | `0.0000` | `0.0359` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_mean_14` | `0.0568` | `0.0000` | `0.0270` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_std_14` | `0.0850` | `0.0000` | `0.0563` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_min_14` | `0.0936` | `0.0000` | `0.0577` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_max_14` | `0.0701` | `0.0000` | `0.0331` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_mean_28` | `0.0503` | `0.0000` | `0.0235` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_std_28` | `0.0854` | `0.0000` | `0.0526` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_min_28` | `0.1223` | `0.0000` | `0.0811` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_max_28` | `0.0634` | `0.0000` | `0.0221` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `demand_growth_7_28` | `0.0776` | `0.0000` | `0.0346` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_trend_7` | `0.0209` | `0.0000` | `0.0047` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `rolling_trend_14` | `0.0209` | `0.0000` | `0.0028` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `momentum_7_1` | `0.0200` | `0.0000` | `0.0056` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `discount_percentage` | `0.0067` | `0.1818` | `0.0003` | `NO_DRIFT` | **🟢 STABLE** |
| `price_ratio` | `0.0067` | `0.1818` | `0.0003` | `NO_DRIFT` | **🟢 STABLE** |
| `is_promoted_int` | `0.0066` | `0.1937` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |
| `inventory_ratio` | `0.1037` | `0.0000` | `0.0698` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `days_of_inventory` | `0.1037` | `0.0000` | `0.0698` | `MODERATE_DRIFT` | **🟡 SHIFT** |
| `category_code` | `0.0003` | `1.0000` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |
| `store_code` | `0.0001` | `1.0000` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |
| `sku_code` | `0.0001` | `1.0000` | `0.0000` | `NO_DRIFT` | **🟢 STABLE** |