"""Data cleaning, transformation, and standardization pipeline for Project FORESIGHT."""

from pathlib import Path
from typing import Any
import pandas as pd

from foresight.config.constants import PROCESSED_DATA_DIR, RAW_DATA_DIR
from foresight.data.loader import load_raw_inventory, load_raw_products, load_raw_sales
from foresight.utils.exceptions import DataProcessingError, DataValidationError
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def validate_raw_frames(
    sales_df: pd.DataFrame,
    products_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
) -> None:
    """Validate core schema and presence of required columns before processing."""
    required_sales = {"date", "sku_id", "store_id", "quantity", "price"}
    required_products = {"sku_id", "category", "unit_cost", "lead_time_days"}
    required_inventory = {"date", "sku_id", "store_id", "inventory_level"}

    if not required_sales.issubset(sales_df.columns):
        missing = required_sales - set(sales_df.columns)
        raise DataValidationError(f"Missing required sales columns: {missing}")

    if not required_products.issubset(products_df.columns):
        missing = required_products - set(products_df.columns)
        raise DataValidationError(f"Missing required product columns: {missing}")

    if not required_inventory.issubset(inventory_df.columns):
        missing = required_inventory - set(inventory_df.columns)
        raise DataValidationError(f"Missing required inventory columns: {missing}")


def align_calendar_grid(
    df: pd.DataFrame,
    date_col: str = "date",
    series_keys: list[str] | None = None,
    fill_values: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Ensure complete continuous daily time-series grid for all (SKU, Store) combinations.

    Imputes zero demand for any unrecorded days to prevent uneven time-step distortion.
    """
    keys = series_keys or ["sku_id", "store_id"]
    fills = fill_values or {"quantity": 0, "is_promoted": False}

    unique_dates = pd.date_range(start=df[date_col].min(), end=df[date_col].max(), freq="D")
    unique_series = df[keys].drop_duplicates()

    # Cartesian product of dates and unique series keys
    grid_index = pd.MultiIndex.from_product(
        [unique_dates, unique_series[keys[0]].unique(), unique_series[keys[1]].unique()],
        names=[date_col, keys[0], keys[1]],
    ).to_frame().reset_index(drop=True)

    # Filter to only existing series pairs
    valid_pairs = set(zip(unique_series[keys[0]], unique_series[keys[1]], strict=False))
    grid = grid_index[
        grid_index.apply(lambda r: (r[keys[0]], r[keys[1]]) in valid_pairs, axis=1)
    ].copy()

    # Merge original observations onto complete grid
    merged = pd.merge(grid, df, on=[date_col] + keys, how="left")

    for col, default_val in fills.items():
        if col in merged.columns:
            if isinstance(default_val, bool):
                merged[col] = merged[col].fillna(default_val).astype(bool)
            else:
                merged[col] = merged[col].fillna(default_val)

    return merged.sort_values(by=keys + [date_col]).reset_index(drop=True)


def process_sales_and_inventory(
    sales_df: pd.DataFrame,
    products_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
) -> pd.DataFrame:
    """Standardize, merge, and clean raw sales, product catalog, and inventory observations."""
    logger.info("Starting data processing and standardization pipeline...")
    validate_raw_frames(sales_df, products_df, inventory_df)

    sales = sales_df.copy()
    sales["date"] = pd.to_datetime(sales["date"])

    inv = inventory_df.copy()
    inv["date"] = pd.to_datetime(inv["date"])

    # 1. Merge Sales and Inventory on (date, sku_id, store_id)
    combined = pd.merge(
        sales,
        inv,
        on=["date", "sku_id", "store_id"],
        how="outer",
    )

    # Fill default quantity and promotions
    combined["quantity"] = combined["quantity"].fillna(0).astype(int)
    combined["is_promoted"] = combined["is_promoted"].fillna(False).astype(bool)
    combined["inventory_level"] = combined["inventory_level"].fillna(0).astype(int)
    combined["units_on_order"] = combined["units_on_order"].fillna(0).astype(int)
    combined["backorders"] = combined["backorders"].fillna(0).astype(int)

    # 2. Merge Product Master Attributes
    merged = pd.merge(
        combined,
        products_df,
        on="sku_id",
        how="left",
    )

    # Fill price if missing from catalog unit_price
    if "unit_price" in merged.columns:
        merged["price"] = merged["price"].fillna(merged["unit_price"])

    # Basic data cleanliness checks
    if merged["sku_id"].isnull().any():
        raise DataProcessingError("Detected null sku_id in processed dataset")

    # Sort deterministically
    merged = merged.sort_values(by=["sku_id", "store_id", "date"]).reset_index(drop=True)
    logger.info(f"Processed dataset ready with {len(merged):,} rows and {len(merged.columns)} columns")
    return merged


def process_and_save_data(
    raw_dir: Path = RAW_DATA_DIR,
    processed_dir: Path = PROCESSED_DATA_DIR,
) -> pd.DataFrame:
    """Load raw data, process, and write to processed storage (Parquet and CSV)."""
    sales_df = load_raw_sales(raw_dir)
    products_df = load_raw_products(raw_dir)
    inventory_df = load_raw_inventory(raw_dir)

    processed_df = process_sales_and_inventory(sales_df, products_df, inventory_df)

    processed_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = processed_dir / "sales_processed.parquet"
    csv_path = processed_dir / "sales_processed.csv"

    processed_df.to_parquet(parquet_path, index=False)
    processed_df.to_csv(csv_path, index=False)

    logger.info(f"Saved processed dataset to {parquet_path} and {csv_path}")
    return processed_df


if __name__ == "__main__":
    process_and_save_data()
