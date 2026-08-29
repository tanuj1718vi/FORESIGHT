"""Automated adversarial leakage and causal integrity tests for Project FORESIGHT."""

import numpy as np
import pandas as pd
import pytest

from foresight.features.pipeline import FeatureEngineeringPipeline


@pytest.fixture
def base_time_series() -> pd.DataFrame:
    """Generate clean 100-day time-series for leakage testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    records = []
    for i, d in enumerate(dates):
        records.append({
            "date": d,
            "sku_id": "SKU-1001",
            "store_id": "STORE-001",
            "quantity": 20 + int(10 * np.sin(i / 5.0)),
            "price": 50.0,
            "unit_price": 50.0,
            "unit_cost": 25.0,
            "is_promoted": False,
            "inventory_level": 200,
            "category": "Electronics",
        })
    return pd.DataFrame(records)


@pytest.mark.unit
def test_adversarial_future_perturbation_leakage_safety(base_time_series: pd.DataFrame) -> None:
    """Adversarial Test: Modifying future targets y(t+1...T) must NOT alter historical features X(<=t).

    Protocol:
    1. Transform unperturbed series -> X_orig.
    2. Choose arbitrary checkpoint cutoff t (e.g. day 40).
    3. Perturb future targets from day 41 to 100 with massive random shocks (+10,000 units).
    4. Transform perturbed series -> X_pert.
    5. Assert all feature values at indices <= 40 are mathematically identical down to machine precision.
    """
    pipeline = FeatureEngineeringPipeline(dropna_warmup=False, lags=[1, 7, 14], windows=[7, 14])

    orig_features = pipeline.fit_transform(base_time_series)
    feature_cols = pipeline.get_feature_names(orig_features)

    cutoff_idx = 40

    perturbed_df = base_time_series.copy()
    # Inject massive future demand surge starting from cutoff + 1
    perturbed_df.loc[cutoff_idx + 1 :, "quantity"] += 10000

    pert_features = pipeline.transform(perturbed_df)

    # Slice historical features up to and including cutoff_idx
    hist_orig = orig_features.loc[:cutoff_idx, feature_cols]
    hist_pert = pert_features.loc[:cutoff_idx, feature_cols]

    # Must be 100% equal with 0.0 variance
    for col in feature_cols:
        orig_vals = hist_orig[col].fillna(-9999).values
        pert_vals = hist_pert[col].fillna(-9999).values
        np.testing.assert_allclose(
            orig_vals,
            pert_vals,
            rtol=1e-5,
            atol=1e-5,
            err_msg=f"Target leakage detected in feature '{col}' at or before cutoff index {cutoff_idx}!",
        )


@pytest.mark.unit
def test_contemporaneous_target_isolation_in_rolling_windows(base_time_series: pd.DataFrame) -> None:
    """Verify modifying contemporaneous target y_t does NOT change rolling features at row t."""
    pipeline = FeatureEngineeringPipeline(dropna_warmup=False, lags=[1, 7], windows=[7, 14])

    orig_features = pipeline.fit_transform(base_time_series)

    test_row = 35
    corrupted_df = base_time_series.copy()
    corrupted_df.loc[test_row, "quantity"] = 999999  # Massive spike at row 35

    corrupted_features = pipeline.transform(corrupted_df)

    # rolling_mean_7 at row 35 MUST NOT reflect the 999999 spike at row 35
    orig_rolling = orig_features.loc[test_row, "rolling_mean_7"]
    corrupted_rolling = corrupted_features.loc[test_row, "rolling_mean_7"]

    assert np.isclose(orig_rolling, corrupted_rolling, atol=1e-5)

    # However, at row 36 (next day), rolling_mean_7 SHOULD reflect row 35's value
    next_day_rolling = corrupted_features.loc[test_row + 1, "rolling_mean_7"]
    assert next_day_rolling > orig_rolling
