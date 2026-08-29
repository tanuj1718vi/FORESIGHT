"""Rolling-origin walk-forward time-series cross-validation for Project FORESIGHT."""

from collections.abc import Generator
from datetime import datetime
from typing import NamedTuple
import numpy as np
import pandas as pd
from pydantic import BaseModel

from foresight.utils.exceptions import ConfigurationError
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


class TimeSeriesCVFold(NamedTuple):
    """Metadata and row indices for a single temporal cross-validation fold."""
    fold_idx: int
    train_indices: np.ndarray
    val_indices: np.ndarray
    train_start_date: str
    train_end_date: str
    val_start_date: str
    val_end_date: str
    train_size: int
    val_size: int


class RollingOriginCV:
    """Rolling Origin / Walk-Forward cross-validation generator.

    Produces expanding historical training sets with strictly forward, non-overlapping
    validation horizons to evaluate time-series forecasting models without lookahead leakage.
    """

    def __init__(
        self,
        n_splits: int = 4,
        horizon_days: int = 30,
        step_days: int = 14,
        min_train_days: int = 180,
        date_col: str = "date",
    ) -> None:
        self.n_splits = n_splits
        self.horizon_days = horizon_days
        self.step_days = step_days
        self.min_train_days = min_train_days
        self.date_col = date_col

    def split(self, df: pd.DataFrame) -> Generator[TimeSeriesCVFold, None, None]:
        """Generate rolling origin training and validation index splits.

        Args:
            df: Input DataFrame containing the date column.

        Yields:
            TimeSeriesCVFold tuples with train/val indices and date bounds.
        """
        if self.date_col not in df.columns:
            raise ConfigurationError(f"Date column '{self.date_col}' not found in DataFrame.")

        dates = pd.to_datetime(df[self.date_col])
        unique_dates = np.sort(dates.unique())
        total_days = len(unique_dates)

        required_days = self.min_train_days + self.horizon_days + (self.n_splits - 1) * self.step_days
        if total_days < required_days:
            # Fallback scaling if dataset is shorter
            step = max(7, (total_days - self.min_train_days - self.horizon_days) // max(1, self.n_splits))
        else:
            step = self.step_days

        # Determine cutoff dates starting from the most recent window working backward
        last_val_end_idx = total_days - 1

        for fold in range(self.n_splits):
            val_end_idx = last_val_end_idx - (self.n_splits - 1 - fold) * step
            val_start_idx = val_end_idx - self.horizon_days + 1
            train_end_idx = val_start_idx - 1

            if train_end_idx < 0:
                continue

            train_start_date = unique_dates[0]
            train_end_date = unique_dates[train_end_idx]
            val_start_date = unique_dates[val_start_idx]
            val_end_date = unique_dates[val_end_idx]

            train_mask = (dates >= train_start_date) & (dates <= train_end_date)
            val_mask = (dates >= val_start_date) & (dates <= val_end_date)

            train_indices = np.where(train_mask)[0]
            val_indices = np.where(val_mask)[0]

            yield TimeSeriesCVFold(
                fold_idx=fold + 1,
                train_indices=train_indices,
                val_indices=val_indices,
                train_start_date=pd.Timestamp(train_start_date).strftime("%Y-%m-%d"),
                train_end_date=pd.Timestamp(train_end_date).strftime("%Y-%m-%d"),
                val_start_date=pd.Timestamp(val_start_date).strftime("%Y-%m-%d"),
                val_end_date=pd.Timestamp(val_end_date).strftime("%Y-%m-%d"),
                train_size=len(train_indices),
                val_size=len(val_indices),
            )
