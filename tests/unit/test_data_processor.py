"""Unit tests for data validation, grid alignment, and processing pipelines."""

from datetime import date
import pandas as pd
import pytest

from foresight.data.processor import (
    align_calendar_grid,
    process_sales_and_inventory,
    validate_raw_frames,
)
from foresight.utils.exceptions import DataValidationError


@pytest.mark.unit
def test_validate_raw_frames_missing_columns() -> None:
    """Verify validate_raw_frames raises DataValidationError when required column is missing."""
    sales_bad = pd.DataFrame({"date": ["2024-01-01"], "sku_id": ["SKU-1"]})
    products = pd.DataFrame({"sku_id": ["SKU-1"], "category": ["Cat"], "unit_cost": [10.0], "lead_time_days": [5]})
    inv = pd.DataFrame({"date": ["2024-01-01"], "sku_id": ["SKU-1"], "store_id": ["S1"], "inventory_level": [10]})

    with pytest.raises(DataValidationError):
        validate_raw_frames(sales_bad, products, inv)


@pytest.mark.unit
def test_align_calendar_grid_imputation() -> None:
    """Verify align_calendar_grid fills missing time-steps with zero demand."""
    sparse_data = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-03"]),
        "sku_id": ["SKU-1", "SKU-1"],
        "store_id": ["STORE-1", "STORE-1"],
        "quantity": [10, 20],
        "is_promoted": [False, True],
    })

    aligned = align_calendar_grid(sparse_data, date_col="date")

    # Should contain 2024-01-01, 2024-01-02, 2024-01-03 (3 rows)
    assert len(aligned) == 3
    # Check that missing middle day (2024-01-02) was imputed with 0
    day2 = aligned[aligned["date"] == "2024-01-02"].iloc[0]
    assert day2["quantity"] == 0
    assert bool(day2["is_promoted"]) is False
    assert day2["is_promoted"] == False


@pytest.mark.unit
def test_process_sales_and_inventory_pipeline() -> None:
    """Verify process_sales_and_inventory combines and standardizes disparate tables."""
    sales = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "sku_id": ["SKU-1", "SKU-1"],
        "store_id": ["STORE-1", "STORE-1"],
        "quantity": [5, 12],
        "price": [25.0, 22.0],
        "is_promoted": [False, True],
    })
    products = pd.DataFrame({
        "sku_id": ["SKU-1"],
        "product_name": ["Test Item"],
        "category": ["Electronics"],
        "subcategory": ["Audio"],
        "unit_cost": [12.0],
        "unit_price": [25.0],
        "lead_time_days": [7],
        "min_order_qty": [10],
        "demand_pattern": ["regular"],
    })
    inv = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "sku_id": ["SKU-1", "SKU-1"],
        "store_id": ["STORE-1", "STORE-1"],
        "inventory_level": [100, 88],
        "units_on_order": [0, 50],
        "backorders": [0, 0],
    })

    processed = process_sales_and_inventory(sales, products, inv)

    assert len(processed) == 2
    assert "category" in processed.columns
    assert "inventory_level" in processed.columns
    assert processed["category"].iloc[0] == "Electronics"
    assert processed["lead_time_days"].iloc[0] == 7
