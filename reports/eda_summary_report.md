# FORESIGHT — Exploratory Data Analysis & Business Intelligence

**Dataset:** `sales_processed`  
**Observation Period:** `2023-01-01` to `2024-12-30` (730 days)  
**Total Records:** `182,500` | **Generated:** `2026-08-25T22:23:38.390315`

---

## 1. Executive Key Performance Indicators

| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **Total Sales Volume** | `5,244,260 units` | Total fulfilled retail demand |
| **Total Gross Revenue** | `$420,307,822.51` | Cumulative sales proceeds |
| **Mean Daily Demand** | `7183.9 units/day` | Aggregate network daily velocity |
| **Promotional Lift** | `1.50x` | Average demand surge during active markdown/promo |
| **Annual Market Trend** | `+10.2%/yr` | Underling structural market growth rate |
| **Average Working Inventory Value** | `$4,209,076.93` | Tied-up working capital in physical stock |
| **Stockout Rate** | `1.81%` | Percentage of SKU-store days experiencing stock depletion |
| **Total Backorders** | `110,772 units` | Unfulfilled customer demand lost/backordered |
| **Inventory Turnover Ratio** | `28.78x / yr` | Velocity of inventory replenishment cycle |
| **Average Days of Supply (DOS)** | `12.7 days` | Projected coverage buffer at current demand rate |

---

## 2. Demand Seasonality & Cyclicality

### Day-of-Week Seasonality Index (1.0 = Average Day)

| Monday | Tuesday | Wednesday | Thursday | Friday | Saturday | Sunday |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0.91 | 0.91 | 0.92 | 0.92 | 0.92 | **1.22** | **1.21** |

---

## 3. ABC / XYZ Portfolio Segmentation Matrix

The catalog of **50 SKUs** is segmented by revenue contribution (ABC) and demand variability (XYZ):

| Segment Breakdown | Count | SKU Share | Strategy Profile |
| :--- | :--- | :--- | :--- |
| **AX** | `1` | `2.0%` | High Value, Low Volatility (Automated Replenish) |
| **AY** | `18` | `36.0%` | Standard Dynamic ROP |
| **BX** | `3` | `6.0%` | Standard Dynamic ROP |
| **BY** | `12` | `24.0%` | Standard Dynamic ROP |
| **CX** | `1` | `2.0%` | Standard Dynamic ROP |
| **CY** | `10` | `20.0%` | Standard Dynamic ROP |
| **CZ** | `5` | `10.0%` | Low Value, Intermittent (Order-on-demand / Low Stock) |

### Top Revenue Driving SKUs (Pareto Class A)
- SKU-1036, SKU-1026, SKU-1033, SKU-1041, SKU-1001

### High Volatility / Intermittent SKUs (Class Z)
- SKU-1031, SKU-1019, SKU-1006, SKU-1040, SKU-1025
