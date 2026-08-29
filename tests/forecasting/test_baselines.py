"""Unit tests for baseline and classical statistical forecasting models."""

import numpy as np
import pandas as pd
import pytest

from foresight.forecasting.baselines import (
    ExponentialSmoothingForecaster,
    MovingAverageForecaster,
    NaiveForecaster,
    SeasonalNaiveForecaster,
)


@pytest.fixture
def baseline_test_df() -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    """Provide feature data and targets for baseline testing."""
    X_train = pd.DataFrame({
        "lag_1": [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0],
        "lag_7": [8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
        "rolling_mean_7": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0],
    })
    y_train = np.array([12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0])

    X_test = pd.DataFrame({
        "lag_1": [26.0, 28.0],
        "lag_7": [16.0, 17.0],
        "rolling_mean_7": [18.0, 19.0],
    })
    return X_train, y_train, X_test


@pytest.mark.forecasting
def test_naive_forecaster(baseline_test_df: tuple[pd.DataFrame, np.ndarray, pd.DataFrame]) -> None:
    """Verify NaiveForecaster predicts lag_1 values."""
    X_train, y_train, X_test = baseline_test_df
    model = NaiveForecaster()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    assert len(preds) == 2
    assert preds[0] == 26.0
    assert preds[1] == 28.0


@pytest.mark.forecasting
def test_seasonal_naive_forecaster(baseline_test_df: tuple[pd.DataFrame, np.ndarray, pd.DataFrame]) -> None:
    """Verify SeasonalNaiveForecaster predicts lag_7 values."""
    X_train, y_train, X_test = baseline_test_df
    model = SeasonalNaiveForecaster(season_length=7)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    assert len(preds) == 2
    assert preds[0] == 16.0
    assert preds[1] == 17.0


@pytest.mark.forecasting
def test_moving_average_forecaster(baseline_test_df: tuple[pd.DataFrame, np.ndarray, pd.DataFrame]) -> None:
    """Verify MovingAverageForecaster predicts rolling mean."""
    X_train, y_train, X_test = baseline_test_df
    model = MovingAverageForecaster(window=7)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    assert len(preds) == 2
    assert preds[0] == 18.0
    assert preds[1] == 19.0


@pytest.mark.forecasting
def test_exponential_smoothing_forecaster(baseline_test_df: tuple[pd.DataFrame, np.ndarray, pd.DataFrame]) -> None:
    """Verify ExponentialSmoothingForecaster fits and generates non-negative predictions."""
    X_train, y_train, X_test = baseline_test_df
    model = ExponentialSmoothingForecaster(season_length=7)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    assert len(preds) == 2
    assert (preds >= 0.0).all()
