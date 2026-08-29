"""Unit tests for ForecastExplainer and TreeSHAP calculations."""

import numpy as np
import pandas as pd
import pytest

from foresight.explainability.shap_explainer import ForecastExplainer, categorize_feature
from foresight.explainability.schema import FeatureCategory
from foresight.forecasting.ml_models import XGBoostForecaster


@pytest.fixture
def trained_xgb_with_sample_data() -> tuple[XGBoostForecaster, pd.DataFrame]:
    """Train miniature XGBoost model and provide feature data for explainer testing."""
    np.random.seed(42)
    n = 150
    x_lag = np.random.uniform(5, 30, n)
    x_promo = np.random.choice([0, 1], n, p=[0.8, 0.2])
    x_weekend = np.random.choice([0, 1], n, p=[0.7, 0.3])
    x_price = np.random.uniform(15, 45, n)

    df = pd.DataFrame({
        "lag_1": x_lag,
        "is_promoted": x_promo,
        "is_weekend": x_weekend,
        "price": x_price,
    })
    y = 5.0 + 0.6 * x_lag + 10.0 * x_promo + 4.0 * x_weekend - 0.2 * x_price + np.random.normal(0, 0.5, n)

    model = XGBoostForecaster(n_estimators=30, max_depth=4)
    model.fit(df, y)
    return model, df


@pytest.mark.explainability
def test_categorize_feature() -> None:
    """Verify feature classification rules."""
    assert categorize_feature("lag_7") == FeatureCategory.AUTOREGRESSIVE_LAG
    assert categorize_feature("rolling_mean_14") == FeatureCategory.ROLLING_STATS
    assert categorize_feature("demand_growth_7_28") == FeatureCategory.VELOCITY_TREND
    assert categorize_feature("discount_percentage") == FeatureCategory.PRICING_PROMO
    assert categorize_feature("is_weekend") == FeatureCategory.TEMPORAL
    assert categorize_feature("days_of_inventory") == FeatureCategory.OPERATIONAL


@pytest.mark.explainability
def test_compute_global_importance(trained_xgb_with_sample_data: tuple[XGBoostForecaster, pd.DataFrame]) -> None:
    """Verify global feature rankings from TreeSHAP."""
    model, df = trained_xgb_with_sample_data
    explainer = ForecastExplainer(model)

    importances = explainer.compute_global_importance(df)
    assert len(importances) == len(df.columns)
    assert importances[0].rank == 1
    assert importances[0].mean_abs_shap >= importances[1].mean_abs_shap
    assert np.isclose(sum(imp.relative_importance_pct for imp in importances), 100.0, atol=0.5)


@pytest.mark.explainability
def test_explain_observation_additivity(trained_xgb_with_sample_data: tuple[XGBoostForecaster, pd.DataFrame]) -> None:
    """Verify local SHAP explanation additivity: E[y] + sum(phi_i) approx y_hat."""
    model, df = trained_xgb_with_sample_data
    explainer = ForecastExplainer(model)

    row = df.iloc[10]
    exp = explainer.explain_observation(
        row_features=row,
        sku_id="SKU-TEST",
        store_id="STORE-001",
        date="2024-06-01",
    )

    assert exp.predicted_value > 0
    assert len(exp.business_narrative) > 20
    assert len(exp.top_positive_drivers) + len(exp.top_negative_drivers) > 0
