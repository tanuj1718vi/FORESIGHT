# Project FORESIGHT — Data Dictionary & Entity Catalog

This document defines the data models, column specifications, physical data types, data origins, and business semantics for the datasets in Project FORESIGHT.

---

## 1. Physical Dataset Artifacts

| Dataset File | File Format | Storage Path | Row Count | Primary Key / Granularity |
| :--- | :--- | :--- | :--- | :--- |
| **Raw Sales** | CSV | `data/raw/sales_raw.csv` | 182,500 | `(date, sku_id, store_id)` |
| **Raw Products** | CSV | `data/raw/products_raw.csv` | 50 | `sku_id` |
| **Raw Inventory** | CSV | `data/raw/inventory_raw.csv` | 182,500 | `(date, sku_id, store_id)` |
| **Processed Unified Sales** | Parquet & CSV | `data/processed/sales_processed.parquet` | 182,500 | `(date, sku_id, store_id)` |

---

## 2. Processed Dataset Schema (`sales_processed`)

| Field Name | Type | Nullable | Origin | Description & Constraints | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | `datetime64[ns]` | No | Primary | Observation calendar date (2023-01-01 to 2024-12-31, 730 days) | `2023-01-01` |
| `sku_id` | `object` / `str` | No | Primary | Unique identifier for the Stock Keeping Unit (`SKU-1001` to `SKU-1050`) | `SKU-1042` |
| `store_id` | `object` / `str` | No | Primary | Location/Store identifier (`STORE-001` to `STORE-005`) | `STORE-001` |
| `quantity` | `int64` | No | Realized | Units sold on the specific day ($\ge 0$). Fulfills demand up to available inventory | `18` |
| `price` | `float64` | No | Transactional | Selling price per unit on that date after applicable promotional discounts ($> 0$) | `29.99` |
| `is_promoted` | `bool` | No | Operational | Boolean flag indicating whether marketing promotion/discount was active | `True` |
| `inventory_level` | `int64` | No | Operational | On-hand physical inventory count at the end of the trading day ($\ge 0$) | `124` |
| `units_on_order` | `int64` | No | Operational | Inventory units currently in transit from supplier awaiting arrival | `50` |
| `backorders` | `int64` | No | Operational | Unfulfilled consumer demand on that day due to stockout ($\ge 0$) | `0` |
| `product_name` | `object` / `str` | No | Catalog | Merchandising display title of the product | `Electronics Audio Item 42` |
| `category` | `object` / `str` | No | Catalog | Primary merchandise category (5 distinct categories) | `Electronics` |
| `subcategory` | `object` / `str` | No | Catalog | Granular product subcategory | `Audio` |
| `unit_price` | `float64` | No | Catalog | Standard retail catalog base price ($> 0$) | `34.99` |
| `unit_cost` | `float64` | No | Catalog | Wholesale supplier procurement unit cost ($> 0$) | `18.50` |
| `lead_time_days` | `int64` | No | Catalog | Supplier replenishment lead time in days ($\ge 1$, typical range 3–28 days) | `14` |
| `min_order_qty` | `int64` | No | Catalog | Supplier Minimum Order Quantity (MOQ) ($\ge 1$) | `50` |
| `demand_pattern` | `object` / `str` | No | Archetype | Demand classification: `regular`, `seasonal`, `volatile`, `intermittent` | `regular` |
| `base_demand_rate` | `float64` | No | Model Baseline | Mean intrinsic daily demand rate for the SKU prior to seasonality/store scaling | `22.50` |
| `holding_cost_annual_rate` | `float64` | No | Financial | Annualized inventory carrying cost fraction (default: 0.20 = 20%) | `0.20` |

---

## 3. Product Categories & Parameter Ranges

| Category | Typical Price Range | Target Margin | Typical Lead Time | MOQ Range | Seasonality Profile |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Electronics** | \$25 – \$299 | 30% – 55% | 10 – 21 days | 20 – 100 | Q4 Holiday surge (+60%), Weekend boost (+25%) |
| **Apparel** | \$19 – \$149 | 45% – 65% | 14 – 28 days | 50 – 200 | Q4 Holiday surge (+40%), Weekend boost (+40%) |
| **Home & Kitchen**| \$15 – \$189 | 35% – 50% | 7 – 18 days | 25 – 150 | Q4 Holiday surge (+30%), Weekend boost (+30%) |
| **Grocery** | \$4.5 – \$34 | 20% – 35% | 3 – 7 days | 100 – 500 | Steady baseline, Heavy weekend boost (+50%) |
| **Health & Beauty**| \$9 – \$79 | 50% – 70% | 7 – 14 days | 30 – 120 | Moderate year-round, Q4 gift surge (+25%) |

---

## 4. Location Nodes & Scaling

| Store ID | Location Name | Facility Type | Volume Multiplier |
| :--- | :--- | :--- | :--- |
| `STORE-001` | Metro Flagship - North | High-Volume Retail | $1.35\times$ |
| `STORE-002` | Suburban Center - West | Standard Retail | $1.05\times$ |
| `STORE-003` | Downtown Express - Central | Compact Retail | $0.85\times$ |
| `STORE-004` | Regional Hub - South | Large Format Retail | $1.20\times$ |
| `STORE-005` | E-Commerce Fulfillment Center | Central Distribution | $1.55\times$ |

---

## 5. Demand Archetypes & Distribution Formulations

1. **Regular Demand (55% of catalog):**
   $$\text{Demand}_t \sim \text{Poisson}(\lambda_t)$$
   where $\lambda_t = \text{base\_rate} \times \text{store\_scale} \times \text{day\_factor} \times \text{season\_factor} \times \text{promo\_lift} \times \text{trend}_t$.

2. **Seasonal Demand (20% of catalog):**
   Higher responsiveness to holiday quarter spikes and annual cyclical variations.

3. **Volatile Demand (15% of catalog):**
   $$\text{Demand}_t \sim \lfloor \lambda_t \times \text{Lognormal}(0, \sigma=0.45) \rceil$$

4. **Intermittent Demand (10% of catalog):**
   Zero-inflated Poisson with $65\%$ probability of zero daily demand, punctuated by non-zero discrete batches ($1-8$ units).

---

## 6. Real vs. Generated Field Attribution

- **Deterministic Real-World Equivalent Entities:**
  - Date index, Store IDs, SKU IDs, Merchandising Categories, Subcategories, Unit Price, Unit Cost, Promo Flags, Sales Quantities.
- **Operational Supply Chain Fields (Simulated with Stochastic Consistency):**
  - `inventory_level`, `units_on_order`, `backorders`, `lead_time_days`, `min_order_qty`.
  - All simulated fields preserve inventory balance conservation:
    $$\text{Inventory}_{t} = \max\left(0, \text{Inventory}_{t-1} + \text{Receipts}_t - \text{Demand}_t\right)$$
