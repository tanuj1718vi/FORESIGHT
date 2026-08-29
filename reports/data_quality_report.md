# FORESIGHT — Data Quality Audit Report

**Dataset:** `sales_processed`  
**Audit Timestamp:** `2026-08-25T22:14:51.542795`  
**Total Records:** `182,500` | **Total Columns:** `19`  
**Overall Health Status:** ✅ **PASS**  
**Data Quality Score:** **100.0%**

---

## Quality Check Summary

| Check Name | Status | Severity | Violated Rows | Violated % | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `null_values_check` | ✅ PASS | `INFO` | 0 | 0.00% | No null or NaN values detected in any column. |
| `duplicate_rows_check` | ✅ PASS | `INFO` | 0 | 0.00% | Zero duplicate rows detected. |
| `duplicate_series_keys_check` | ✅ PASS | `INFO` | 0 | 0.00% | Primary keys ['date', 'sku_id', 'store_id'] are strictly unique. |
| `date_validity_check` | ✅ PASS | `INFO` | 0 | 0.00% | All dates valid across range 2023-01-01 to 2024-12-30. |
| `non_negative_sales_check` | ✅ PASS | `INFO` | 0 | 0.00% | All sales quantities are non-negative. |
| `inventory_validity_check` | ✅ PASS | `INFO` | 0 | 0.00% | All inventory counts are valid and non-negative. |
| `sku_identifier_format_check` | ✅ PASS | `INFO` | 0 | 0.00% | All 50 distinct SKU identifiers follow standard formatting. |
| `category_consistency_check` | ✅ PASS | `INFO` | 0 | 0.00% | All SKUs maintain 100% consistent category mappings. |
| `time_continuity_check` | ✅ PASS | `INFO` | 0 | 0.00% | All 250 time-series possess complete 730 continuous daily steps. |
| `extreme_outliers_check` | ✅ PASS | `INFO` | 569 | 0.31% | Detected 569 extreme demand observations (0.31%) above threshold 111.0 units. |
| `data_leakage_check` | ✅ PASS | `INFO` | 0 | 0.00% | No future lookahead or target leakage columns identified. |

---

## Detailed Findings & Diagnostic Context

### `null_values_check` (PASS)
- **Description:** Verify zero missing or NaN values across all columns.
- **Finding:** No null or NaN values detected in any column.
- **Diagnostics:**
```json
{
  "null_counts_by_column": {}
}
```

### `duplicate_rows_check` (PASS)
- **Description:** Verify absence of completely duplicate rows.
- **Finding:** Zero duplicate rows detected.

### `duplicate_series_keys_check` (PASS)
- **Description:** Verify uniqueness of primary (date, sku_id, store_id) keys.
- **Finding:** Primary keys ['date', 'sku_id', 'store_id'] are strictly unique.
- **Diagnostics:**
```json
{
  "key_columns": [
    "date",
    "sku_id",
    "store_id"
  ]
}
```

### `date_validity_check` (PASS)
- **Description:** Verify all date values can be successfully parsed into valid timestamps.
- **Finding:** All dates valid across range 2023-01-01 to 2024-12-30.
- **Diagnostics:**
```json
{
  "min_date": "2023-01-01",
  "max_date": "2024-12-30",
  "total_days": 730
}
```

### `non_negative_sales_check` (PASS)
- **Description:** Verify sales quantities are non-negative (quantity >= 0).
- **Finding:** All sales quantities are non-negative.

### `inventory_validity_check` (PASS)
- **Description:** Verify inventory counts are non-negative (inventory_level >= 0).
- **Finding:** All inventory counts are valid and non-negative.

### `sku_identifier_format_check` (PASS)
- **Description:** Verify all SKU IDs match standard pattern 'SKU-XXXX'.
- **Finding:** All 50 distinct SKU identifiers follow standard formatting.
- **Diagnostics:**
```json
{
  "unique_skus": 50
}
```

### `category_consistency_check` (PASS)
- **Description:** Verify each SKU belongs to exactly 1 category hierarchy.
- **Finding:** All SKUs maintain 100% consistent category mappings.
- **Diagnostics:**
```json
{
  "categories_count": 5
}
```

### `time_continuity_check` (PASS)
- **Description:** Verify every time-series has complete 730 daily steps without gaps.
- **Finding:** All 250 time-series possess complete 730 continuous daily steps.
- **Diagnostics:**
```json
{
  "total_series": 250,
  "expected_days_per_series": 730
}
```

### `extreme_outliers_check` (PASS)
- **Description:** Audit extreme sales spikes exceeding 3.0x IQR above Q3.
- **Finding:** Detected 569 extreme demand observations (0.31%) above threshold 111.0 units.
- **Diagnostics:**
```json
{
  "q25": 15.0,
  "q75": 39.0,
  "iqr": 24.0,
  "upper_bound_3iqr": 111.0,
  "max_value": 221.0
}
```

### `data_leakage_check` (PASS)
- **Description:** Verify absence of lookahead or future target leak columns.
- **Finding:** No future lookahead or target leakage columns identified.
