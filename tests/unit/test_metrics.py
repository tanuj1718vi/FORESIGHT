"""Unit tests for forecasting evaluation metrics and zero-safe scoring formulas."""

import numpy as np
import pytest

from foresight.evaluation.metrics import (
    evaluate_predictions,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_absolute_scaled_error,
    pinball_loss,
    root_mean_squared_error,
    symmetric_mean_absolute_percentage_error,
    weighted_absolute_percentage_error,
)


@pytest.mark.unit
def test_standard_metrics_calculation() -> None:
    """Verify MAE, RMSE, WAPE on known synthetic vectors."""
    y_true = np.array([10.0, 20.0, 30.0, 40.0])
    y_pred = np.array([12.0, 18.0, 33.0, 37.0])

    # Absolute errors: [2, 2, 3, 3] -> sum = 10, mean = 2.5
    # Squared errors: [4, 4, 9, 9] -> sum = 26, mean = 6.5, sqrt = 2.5495
    # Actual sum: 100 -> WAPE = 10 / 100 = 0.10

    assert np.isclose(mean_absolute_error(y_true, y_pred), 2.5)
    assert np.isclose(root_mean_squared_error(y_true, y_pred), np.sqrt(6.5))
    assert np.isclose(weighted_absolute_percentage_error(y_true, y_pred), 0.10)


@pytest.mark.unit
def test_zero_demand_handling_in_wape_and_smape() -> None:
    """Verify metrics handle zero-demand periods without division by zero or errors."""
    y_true = np.array([0.0, 0.0, 0.0, 0.0])
    y_pred = np.array([0.0, 0.0, 0.0, 0.0])

    assert weighted_absolute_percentage_error(y_true, y_pred) == 0.0
    assert symmetric_mean_absolute_percentage_error(y_true, y_pred) == 0.0
    assert mean_absolute_percentage_error(y_true, y_pred) == 0.0


@pytest.mark.unit
def test_mase_calculation() -> None:
    """Verify MASE relative to seasonal naive in-sample scaling."""
    y_train = np.array([10.0, 12.0, 15.0, 11.0, 13.0, 16.0, 10.5, 12.5, 15.5])
    y_true = np.array([11.0, 13.0])
    y_pred = np.array([10.5, 12.5])

    mase_val = mean_absolute_scaled_error(y_true, y_pred, y_train, seasonality=3)
    assert mase_val is not None
    assert mase_val > 0.0


@pytest.mark.unit
def test_pinball_loss_symmetry() -> None:
    """Verify Pinball / Quantile Loss behaves as expected for median (q=0.50)."""
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([12.0, 18.0, 32.0])

    # At q=0.50, pinball loss equals 0.5 * MAE
    loss_50 = pinball_loss(y_true, y_pred, quantile=0.50)
    mae_val = mean_absolute_error(y_true, y_pred)
    assert np.isclose(loss_50, 0.5 * mae_val)


@pytest.mark.unit
def test_evaluate_predictions_returns_full_score_set() -> None:
    """Verify evaluate_predictions outputs strongly typed MetricScoreSet."""
    y_true = [10.0, 20.0, 30.0, 40.0]
    y_pred = [10.0, 20.0, 30.0, 40.0]  # Perfect forecast

    scores = evaluate_predictions(y_true, y_pred)
    assert scores.mae == 0.0
    assert scores.rmse == 0.0
    assert scores.wape == 0.0
    assert scores.r2 == 1.0
    assert scores.sample_size == 4
