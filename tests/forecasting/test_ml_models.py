"""Unit tests for machine learning, gradient boosting, and probabilistic forecasters."""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from foresight.forecasting.ml_models import (
    GradientBoostingForecaster,
    LinearRegressionForecaster,
    QuantileGradientBoostingForecaster,
    RandomForestForecaster,
    XGBoostForecaster,
)


@pytest.fixture
def ml_train_test_data() -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]:
    """Generate synthetic linear + seasonal dataset for ML testing."""
    np.random.seed(42)
    n = 200
    x1 = np.arange(n, dtype=float)
    x2 = np.sin(x1 / 3.5)
    x3 = (x1 % 7).astype(float)

    X = pd.DataFrame({
        "time_idx": x1,
        "sin_feat": x2,
        "day_of_week": x3,
        "lag_1": np.roll(x1, 1),
    })
    y = 15.0 + 0.2 * x1 + 4.0 * x2 + np.random.normal(0, 1.0, n)

    X_train, y_train = X.iloc[:160], y[:160]
    X_test, y_test = X.iloc[160:], y[160:]
    return X_train, y_train, X_test, y_test


@pytest.mark.forecasting
def test_linear_regression_forecaster(ml_train_test_data: tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]) -> None:
    """Verify Ridge Linear Regression fits, predicts, and produces feature importances."""
    X_train, y_train, X_test, y_test = ml_train_test_data
    model = LinearRegressionForecaster(alpha=1.0)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    assert len(preds) == len(X_test)
    assert (preds >= 0.0).all()

    importances = model.get_feature_importances()
    assert importances is not None
    assert "time_idx" in importances


@pytest.mark.forecasting
def test_random_forest_forecaster(ml_train_test_data: tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]) -> None:
    """Verify RandomForestForecaster fits and generates predictions."""
    X_train, y_train, X_test, y_test = ml_train_test_data
    model = RandomForestForecaster(n_estimators=30, max_depth=6)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    assert len(preds) == len(X_test)
    assert model.get_feature_importances() is not None


@pytest.mark.forecasting
def test_gradient_boosting_forecaster(ml_train_test_data: tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]) -> None:
    """Verify GradientBoostingForecaster fits and predicts."""
    X_train, y_train, X_test, y_test = ml_train_test_data
    model = GradientBoostingForecaster(max_iter=40, max_depth=5)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    assert len(preds) == len(X_test)


@pytest.mark.forecasting
def test_xgboost_forecaster_and_serialization(
    ml_train_test_data: tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray],
    tmp_path: Path,
) -> None:
    """Verify XGBoostForecaster fits, predicts, serializes, and deserializes without loss."""
    X_train, y_train, X_test, y_test = ml_train_test_data
    model = XGBoostForecaster(n_estimators=50, max_depth=5)
    model.fit(X_train, y_train)

    preds1 = model.predict(X_test)

    # Serialize & reload
    save_file = tmp_path / "xgb_test.pkl"
    model.save(save_file)
    reloaded = XGBoostForecaster.load(save_file)

    preds2 = reloaded.predict(X_test)
    np.testing.assert_allclose(preds1, preds2)


@pytest.mark.forecasting
def test_quantile_gradient_boosting_monotonicity(
    ml_train_test_data: tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray],
) -> None:
    """Verify QuantileGradientBoosting produces strictly monotonic intervals (P10 <= P50 <= P90)."""
    X_train, y_train, X_test, y_test = ml_train_test_data
    q_model = QuantileGradientBoostingForecaster(quantiles=[0.10, 0.50, 0.90], max_iter=30)
    q_model.fit(X_train, y_train)

    quantiles = q_model.predict_quantiles(X_test)
    assert set(quantiles.keys()) == {0.10, 0.50, 0.90}

    p10 = quantiles[0.10]
    p50 = quantiles[0.50]
    p90 = quantiles[0.90]

    # Monotonicity check: P10 <= P50 <= P90 across all test rows
    assert (p10 <= p50).all()
    assert (p50 <= p90).all()
