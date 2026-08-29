# FORESIGHT — Portfolio Inventory Optimization & Working Capital Audit

**Audit Timestamp:** `2026-08-29T20:59:39.541901`  
**Enterprise Portfolio Scope:** `250` SKU-Store replenishment nodes  
**Target Service Level:** `95.0%`  

---

## 1. Executive Financial Summary

| Metric | Portfolio Aggregate Value |
| :--- | :--- |
| **Total Working Capital Committed** | **$3,684,873.94** |
| **Total Units to Order Now** | **56,683 units** |
| **Annual Inventory Holding Cost** | **$736,689.91/yr** |
| **Annual Purchase Ordering Cost** | **$362,048.28/yr** |
| **Total Annual Inventory Carrying Cost** | **$1,098,738.21/yr** |

---

## 2. Portfolio Health Breakdown

| Health Position | Node Count | Percentage of Portfolio | Operational Implication |
| :--- | :---: | :---: | :--- |
| `OPTIMAL` | **127** | `50.8%` | Active monitoring / Action |
| `STOCKOUT_IMMINENT` | **59** | `23.6%` | Active monitoring / Action |
| `UNDERSTOCKED` | **56** | `22.4%` | Active monitoring / Action |
| `CRITICAL_EXCESS` | **4** | `1.6%` | Active monitoring / Action |
| `OVERSTOCKED` | **4** | `1.6%` | Active monitoring / Action |

### 2.1 Prescriptive Action Summary

| Prescriptive Action | Node Count | Operational Workflow |
| :--- | :---: | :--- |
| **HOLD** | **127** | Prescribed replenishment decision |
| **EXPEDITE** | **59** | Prescribed replenishment decision |
| **ORDER** | **56** | Prescribed replenishment decision |
| **REDUCE** | **8** | Prescribed replenishment decision |

---

## 3. Priority Reorder Actions (Top Stockout Risks)

| SKU ID | Store ID | Net Stock Position | Safety Stock | ROP | Rec. Order Qty | Days of Supply | Stockout Risk |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `SKU-1006` | `STORE-001` | 115 | 59.2 | 239.2 | **334** | `3.9d` | **96.5%** |
| `SKU-1001` | `STORE-001` | 1099 | 350.6 | 1751.1 | **1089** | `0.0d` | **92.2%** |
| `SKU-1022` | `STORE-001` | 1464 | 477.4 | 2337.1 | **1429** | `0.2d` | **91.4%** |
| `SKU-1011` | `STORE-005` | 957 | 321.7 | 1532.2 | **947** | `0.0d` | **90.3%** |
| `SKU-1043` | `STORE-001` | 375 | 212.1 | 726.4 | **627** | `0.0d` | **86.0%** |
| `SKU-1008` | `STORE-001` | 360 | 114.0 | 546.0 | **544** | `6.7d` | **85.1%** |
| `SKU-1046` | `STORE-005` | 339 | 227.4 | 698.9 | **681** | `0.0d` | **83.1%** |
| `SKU-1033` | `STORE-005` | 735 | 314.9 | 1230.3 | **874** | `0.0d` | **82.7%** |
| `SKU-1021` | `STORE-004` | 742 | 257.2 | 1144.3 | **866** | `0.0d` | **82.3%** |
| `SKU-1035` | `STORE-005` | 157 | 54.5 | 240.5 | **504** | `5.9d` | **80.9%** |

---

## 4. Priority Capital Optimization (Top Excess Overstocks)

| SKU ID | Store ID | Net Stock Position | Safety Stock | Days of Supply | Committed Capital | Prescribed Action |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `SKU-1006` | `STORE-004` | 152 | 0.0 | `365.0d` | **$1,424.40** | **REDUCE / HOLD** |
| `SKU-1019` | `STORE-003` | 169 | 8.3 | `236.6d` | **$3,258.59** | **REDUCE / HOLD** |
| `SKU-1019` | `STORE-002` | 279 | 29.9 | `108.5d` | **$3,728.82** | **REDUCE / HOLD** |
| `SKU-1025` | `STORE-002` | 54 | 8.4 | `94.5d` | **$682.27** | **REDUCE / HOLD** |
| `SKU-1017` | `STORE-004` | 1007 | 120.4 | `39.0d` | **$10,299.82** | **REDUCE / HOLD** |
| `SKU-1025` | `STORE-001` | 62 | 25.2 | `36.2d` | **$1,317.07** | **REDUCE / HOLD** |
| `SKU-1025` | `STORE-003` | 53 | 23.1 | `33.7d` | **$1,247.93** | **REDUCE / HOLD** |
| `SKU-1019` | `STORE-004` | 157 | 38.3 | `31.4d` | **$3,911.52** | **REDUCE / HOLD** |