# FORESIGHT — Enterprise Inventory Risk & Prescriptive Decision Audit

**Audit Timestamp:** `2026-08-29T20:59:39.998773`  
**Portfolio Scope:** `250` SKU-Store replenishment nodes  
**Lateral Rebalances Identified:** `4` multi-store transfers  

---

## 1. Financial Exposure & Capital at Risk

| Financial Risk Category | Exposure Amount ($) | Business Implication |
| :--- | :---: | :--- |
| **Lost Gross Margin Risk** | **$239,964.52** | Unmet customer demand from stockouts |
| **Excess Holding Cost Penalty** | **$133,331.70/yr** | Capital tied up in stagnant/excess stock |
| **Total Financial Exposure** | **$373,296.23** | Combined enterprise inventory vulnerability |

---

## 2. Risk Severity Tier Distribution

| Risk Severity Level | Node Count | Percentage of Portfolio | Management Action |
| :--- | :---: | :---: | :--- |
| `LOW` | **122** | `48.8%` | Active SLA compliance & monitoring |
| `CRITICAL` | **50** | `20.0%` | Active SLA compliance & monitoring |
| `MEDIUM` | **40** | `16.0%` | Active SLA compliance & monitoring |
| `HIGH` | **38** | `15.2%` | Active SLA compliance & monitoring |

### 2.1 Prescriptive Action Work Orders

| Action Type | Order Count | Operational Directive |
| :--- | :---: | :--- |
| **MONITOR** | **102** | Trigger automated ERP/WMS workflow |
| **EXPEDITE** | **59** | Trigger automated ERP/WMS workflow |
| **ORDER** | **56** | Trigger automated ERP/WMS workflow |
| **HOLD** | **25** | Trigger automated ERP/WMS workflow |
| **REDUCE** | **8** | Trigger automated ERP/WMS workflow |
| **REBALANCE** | **4** | Trigger automated ERP/WMS workflow |

---

## 3. Top 10 Critical Financial Risks

| SKU ID | Store ID | Risk Level | Composite Score | Stockout Prob | Lost Margin Risk | Excess Holding Risk | Total Exposure |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `SKU-1022` | `STORE-001` | `CRITICAL` | **100.0** | `91.4%` | $28,445.71 | $0.00 | **$28,445.71** |
| `SKU-1001` | `STORE-001` | `CRITICAL` | **100.0** | `92.2%` | $23,107.47 | $0.00 | **$23,107.47** |
| `SKU-1022` | `STORE-005` | `HIGH` | **70.5** | `70.5%` | $18,279.05 | $0.00 | **$18,279.05** |
| `SKU-1033` | `STORE-005` | `CRITICAL` | **100.0** | `82.7%` | $17,995.49 | $0.00 | **$17,995.49** |
| `SKU-1011` | `STORE-005` | `CRITICAL` | **100.0** | `90.3%` | $17,500.92 | $0.00 | **$17,500.92** |
| `SKU-1036` | `STORE-003` | `CRITICAL` | **91.7** | `73.3%` | $12,336.80 | $0.00 | **$12,336.80** |
| `SKU-1043` | `STORE-001` | `CRITICAL` | **100.0** | `86.0%` | $11,947.51 | $0.00 | **$11,947.51** |
| `SKU-1001` | `STORE-004` | `CRITICAL` | **95.5** | `0.0%` | $0.00 | $11,940.44 | **$11,940.44** |
| `SKU-1026` | `STORE-004` | `MEDIUM` | **41.4** | `0.0%` | $0.00 | $9,792.69 | **$9,792.69** |
| `SKU-1011` | `STORE-004` | `HIGH` | **71.6** | `0.0%` | $0.00 | $9,086.02 | **$9,086.02** |

---

## 4. Priority Prescriptive Action Work Orders (Top Recommendations)

| Rec ID | Action | SKU ID | Store ID | Quantity | Urgency | Expected Impact | Justification |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| `REC-STORE-001-SKU-1022` | **EXPEDITE** | `SKU-1022` | `STORE-001` | **1429** | `CRITICAL` | $28,445.71 | Imminent stockout detected: Net stock (1464 units) covers only 0.2 days of supply against a 23-day lead time. Stockout probability is 91.4%. Expedite emergency PO for 1429 units to protect $28,445.71 in gross margin. |
| `REC-STORE-001-SKU-1001` | **EXPEDITE** | `SKU-1001` | `STORE-001` | **1089** | `CRITICAL` | $23,107.47 | Imminent stockout detected: Net stock (1099 units) covers only 0.0 days of supply against a 19-day lead time. Stockout probability is 92.2%. Expedite emergency PO for 1089 units to protect $23,107.47 in gross margin. |
| `REC-STORE-005-SKU-1022` | **ORDER** | `SKU-1022` | `STORE-005` | **1390** | `HIGH` | $18,279.05 | Inventory breached Reorder Point (1987 <= 2775 units). Place standard replenishment purchase order for 1390 units (EOQ = 602) to restore safety stock buffer (593 units). |
| `REC-STORE-005-SKU-1033` | **EXPEDITE** | `SKU-1033` | `STORE-005` | **874** | `CRITICAL` | $17,995.49 | Imminent stockout detected: Net stock (735 units) covers only 0.0 days of supply against a 12-day lead time. Stockout probability is 82.7%. Expedite emergency PO for 874 units to protect $17,995.49 in gross margin. |
| `REC-STORE-005-SKU-1011` | **EXPEDITE** | `SKU-1011` | `STORE-005` | **947** | `CRITICAL` | $17,500.92 | Imminent stockout detected: Net stock (957 units) covers only 0.0 days of supply against a 19-day lead time. Stockout probability is 90.3%. Expedite emergency PO for 947 units to protect $17,500.92 in gross margin. |
| `REC-STORE-003-SKU-1036` | **EXPEDITE** | `SKU-1036` | `STORE-003` | **687** | `CRITICAL` | $12,336.80 | Imminent stockout detected: Net stock (1089 units) covers only 1.6 days of supply against a 18-day lead time. Stockout probability is 73.3%. Expedite emergency PO for 687 units to protect $12,336.80 in gross margin. |
| `REC-STORE-001-SKU-1043` | **EXPEDITE** | `SKU-1043` | `STORE-001` | **627** | `CRITICAL` | $11,947.51 | Imminent stockout detected: Net stock (375 units) covers only 0.0 days of supply against a 12-day lead time. Stockout probability is 86.0%. Expedite emergency PO for 627 units to protect $11,947.51 in gross margin. |
| `REC-STORE-001-SKU-1026` | **EXPEDITE** | `SKU-1026` | `STORE-001` | **600** | `CRITICAL` | $8,111.33 | Imminent stockout detected: Net stock (839 units) covers only 0.0 days of supply against a 13-day lead time. Stockout probability is 70.5%. Expedite emergency PO for 600 units to protect $8,111.33 in gross margin. |
| `REC-STORE-005-SKU-1046` | **EXPEDITE** | `SKU-1046` | `STORE-005` | **681** | `CRITICAL` | $7,512.13 | Imminent stockout detected: Net stock (339 units) covers only 0.0 days of supply against a 11-day lead time. Stockout probability is 83.1%. Expedite emergency PO for 681 units to protect $7,512.13 in gross margin. |
| `REC-STORE-003-SKU-1041` | **EXPEDITE** | `SKU-1041` | `STORE-003` | **549** | `CRITICAL` | $6,637.64 | Imminent stockout detected: Net stock (507 units) covers only 0.0 days of supply against a 13-day lead time. Stockout probability is 78.8%. Expedite emergency PO for 549 units to protect $6,637.64 in gross margin. |