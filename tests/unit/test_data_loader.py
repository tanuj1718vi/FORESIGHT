"""Unit tests for dataset loader functions and error handling."""

from pathlib import Path
import pandas as pd
import pytest

from foresight.data.loader import (
    load_csv_data,
    load_parquet_data,
    load_processed_sales,
    load_raw_inventory,
    load_raw_products,
    load_raw_sales,
)
from foresight.utils.exceptions import DataProcessingError


@pytest.mark.unit
def test_load_csv_missing_file(tmp_path: Path) -> None:
    """Verify load_csv_data raises DataProcessingError when file does not exist."""
    missing_file = tmp_path / "non_existent.csv"
    with pytest.raises(DataProcessingError) as exc_info:
        load_csv_data(missing_file)
    assert "Data file not found" in str(exc_info.value)


@pytest.mark.unit
def test_load_parquet_missing_file(tmp_path: Path) -> None:
    """Verify load_parquet_data raises DataProcessingError when file does not exist."""
    missing_file = tmp_path / "non_existent.parquet"
    with pytest.raises(DataProcessingError) as exc_info:
        load_parquet_data(missing_file)
    assert "Parquet file not found" in str(exc_info.value)


@pytest.mark.unit
def test_load_raw_files_success(tmp_path: Path) -> None:
    """Verify loading valid raw files returns populated dataframes."""
    # Write mock raw files
    sales_path = tmp_path / "sales_raw.csv"
    products_path = tmp_path / "products_raw.csv"
    inventory_path = tmp_path / "inventory_raw.csv"

    pd.DataFrame({
        "date": ["2024-01-01"],
        "sku_id": ["SKU-1001"],
        "store_id": ["STORE-001"],
        "quantity": [10],
        "price": [20.0],
        "is_promoted": [False],
    }).to_csv(sales_path, index=False)

    pd.DataFrame({
        "sku_id": ["SKU-1001"],
        "category": ["Electronics"],
        "unit_cost": [10.0],
        "lead_time_days": [7],
    }).to_csv(products_path, index=False)

    pd.DataFrame({
        "date": ["2024-01-01"],
        "sku_id": ["SKU-1001"],
        "store_id": ["STORE-001"],
        "inventory_level": [50],
        "units_on_order": [0],
        "backorders": [0],
    }).to_csv(inventory_path, index=False)

    sales = load_raw_sales(tmp_path)
    products = load_raw_products(tmp_path)
    inv = load_raw_inventory(tmp_path)

    assert len(sales) == 1
    assert len(products) == 1
    assert len(inv) == 1
    assert pd.api.types.is_datetime64_any_dtype(sales["date"])
