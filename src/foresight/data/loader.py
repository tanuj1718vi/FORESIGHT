"""Dataset loading, ingestion, and validation utilities for Project FORESIGHT."""

from pathlib import Path
import pandas as pd

from foresight.config.constants import PROCESSED_DATA_DIR, RAW_DATA_DIR
from foresight.utils.exceptions import DataProcessingError
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def load_csv_data(
    file_path: Path | str,
    date_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame with validation."""
    path = Path(file_path)
    if not path.is_file():
        raise DataProcessingError(f"Data file not found at path: {path}")

    try:
        df = pd.read_csv(path, parse_dates=date_columns or [])
        logger.info(f"Loaded {len(df):,} rows from {path.name}")
        return df
    except Exception as e:
        raise DataProcessingError(f"Failed to read CSV at {path}: {e}") from e


def load_parquet_data(file_path: Path | str) -> pd.DataFrame:
    """Load a Parquet file into a pandas DataFrame."""
    path = Path(file_path)
    if not path.is_file():
        raise DataProcessingError(f"Parquet file not found at path: {path}")

    try:
        df = pd.read_parquet(path)
        logger.info(f"Loaded {len(df):,} rows from {path.name}")
        return df
    except Exception as e:
        raise DataProcessingError(f"Failed to read Parquet at {path}: {e}") from e


def load_raw_sales(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load raw sales transactions from disk."""
    file_path = raw_dir / "sales_raw.csv"
    df = load_csv_data(file_path, date_columns=["date"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_raw_products(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load product master catalog from disk."""
    file_path = raw_dir / "products_raw.csv"
    return load_csv_data(file_path)


def load_raw_inventory(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load raw inventory positions from disk."""
    file_path = raw_dir / "inventory_raw.csv"
    df = load_csv_data(file_path, date_columns=["date"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_processed_sales(processed_dir: Path = PROCESSED_DATA_DIR) -> pd.DataFrame:
    """Load standardized processed sales dataset."""
    parquet_path = processed_dir / "sales_processed.parquet"
    if parquet_path.is_file():
        df = load_parquet_data(parquet_path)
        df["date"] = pd.to_datetime(df["date"])
        return df

    csv_path = processed_dir / "sales_processed.csv"
    if csv_path.is_file():
        df = load_csv_data(csv_path, date_columns=["date"])
        df["date"] = pd.to_datetime(df["date"])
        return df

    raise DataProcessingError(f"Processed dataset not found in {processed_dir}")
