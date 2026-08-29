# FORESIGHT — Time-Series Forecasting Model Benchmark Leaderboard

**Audit Timestamp:** `2026-08-29T20:59:31.291585`  
**Validation Protocol:** Rolling Origin Cross-Validation (`3 folds`, `30-day horizon`)  
**Primary Selection Metric:** `WAPE` (Lower is Better)  
**🏆 Champion Model Selected:** **XGBoost** (Mean WAPE: **0.1894**)  

---

## Model Performance Leaderboard

| Rank | Model Name | Type | Mean WAPE | Mean RMSE | Mean MAE | Mean sMAPE | Mean R² | Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `XGBoost` | `ml` | **0.1894** | `10.36` | `6.90` | `42.45%` | `0.863` | 🏆 **CHAMPION** |
| 2 | `Gradient Boosting (HistGBM)` | `ml` | **0.1912** | `10.43` | `6.97` | `41.62%` | `0.862` | 🥈 CONTENDER |
| 3 | `Quantile Gradient Boosting (P10/P50/P90)` | `ml` | **0.2023** | `11.47` | `7.38` | `44.28%` | `0.833` | BASELINE |
| 4 | `Random Forest` | `ml` | **0.2033** | `11.06` | `7.42` | `46.46%` | `0.844` | BASELINE |
| 5 | `Ridge Linear Regression` | `ml` | **0.3049** | `16.96` | `11.12` | `48.88%` | `0.634` | BASELINE |
| 6 | `Naive (Persistence)` | `baseline` | **0.3565** | `20.58` | `13.00` | `45.79%` | `0.461` | BASELINE |
| 7 | `Moving Average (7d)` | `baseline` | **0.3693** | `20.51` | `13.48` | `54.71%` | `0.465` | BASELINE |
| 8 | `Seasonal Naive (s=7)` | `baseline` | **0.4865** | `27.42` | `17.75` | `61.96%` | `0.042` | BASELINE |

---

## Key Architectural Observations
- **WAPE Robustness:** Zero-demand periods and intermittent spikes are cleanly handled without division anomalies.
- **ML Superiority:** Gradient boosting models leverage multi-lag autoregression and calendar signals to outperform naive and persistence baselines.
- **Quantile Intervals:** Probabilistic gradient boosting produces calibrated P10, P50, and P90 intervals feeding downstream inventory safety stock engines.