"""Unit tests for rolling origin time-series cross-validation."""

import pandas as pd
import pytest

from foresight.evaluation.cross_validation import RollingOriginCV


@pytest.fixture
def multi_year_df() -> pd.DataFrame:
    """Create 365-day dataset for cross validation testing."""
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    return pd.DataFrame({
        "date": dates,
        "quantity": range(365),
    })


@pytest.mark.unit
def test_rolling_origin_cv_split_properties(multi_year_df: pd.DataFrame) -> None:
    """Verify RollingOriginCV generates expanding training sets and disjoint validation windows."""
    cv = RollingOriginCV(n_splits=3, horizon_days=30, step_days=14, min_train_days=100)
    folds = list(cv.split(multi_year_df))

    assert len(folds) == 3

    last_train_size = 0
    for fold in folds:
        assert fold.train_size > 0
        assert fold.val_size == 30

        # Monotonically expanding training sets
        assert fold.train_size >= last_train_size
        last_train_size = fold.train_size

        # Train and validation indices are strictly disjoint
        intersection = set(fold.train_indices).intersection(set(fold.val_indices))
        assert len(intersection) == 0

        # Validation dates are strictly after training dates
        assert fold.val_start_date > fold.train_end_date
