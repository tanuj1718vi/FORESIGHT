"""Unit tests for individual feature transformers and unified FeatureEngineeringPipeline."""

from datetime import date
import numpy as np
import pandas as pd
import pytest

from foresight.features.business import create_business_features
from foresight.features.lags import create_lag_features
from foresight.features.pipeline import FeatureEngineeringPipeline
from foresight.features.rolling import create_rolling_features
from foresight.features.temporal import create_calendar_features
from foresight.features.trend import create_trend_features


@pytest.fixture
def sample_feature_df() -> pd.DataFrame:
    """Provide structured multi-day dataset for feature verification."""
    dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")  # 91 days
    records = []
    for i, d in enumerate(dates):
        records.append({
            "date": d,
            "sku_id": "SKU-1001",
            "store_id": "STORE-001",
            "quantity": 10 + (i % 5),  # 10, 11, 12, 13, 14 ...
            "price": 25.0 if i % 10 != 0 else 20.0,
            "unit_price": 25.0,
            "unit_cost": 15.0,
            "is_promoted": (i % 10 == 0),
            "inventory_level": 150 - (i % 20),
            "category": "Electronics",
        })
    return pd.DataFrame(records)


@pytest.mark.unit
def test_create_calendar_features(sample_feature_df: pd.DataFrame) -> None:
    """Verify calendar feature generator creates cyclical encodings and date parts."""
    res = create_calendar_features(sample_feature_df)

    expected_cols = [
        "day_of_week", "day_of_month", "week_of_year", "month", "quarter",
        "year", "is_weekend", "sin_day_of_week", "cos_day_of_week",
        "sin_month", "cos_month"
    ]
    for c in expected_cols:
        assert c in res.columns

    # 2024-01-01 was a Monday (day_of_week = 0, is_weekend = 0)
    assert res.loc[0, "day_of_week"] == 0
    assert res.loc[0, "is_weekend"] == 0
    assert np.isclose(res.loc[0, "sin_day_of_week"], 0.0)
    assert np.isclose(res.loc[0, "cos_day_of_week"], 1.0)


@pytest.mark.unit
def test_create_lag_features(sample_feature_df: pd.DataFrame) -> None:
    """Verify lag features match exact historical retrospective target values."""
    res = create_lag_features(sample_feature_df, lags=[1, 7, 14])

    assert "lag_1" in res.columns
    assert "lag_7" in res.columns
    assert "lag_14" in res.columns

    # Row 0 has no lag_1 (NaN)
    assert pd.isna(res.loc[0, "lag_1"])

    # Row 1 lag_1 should equal Row 0 quantity
    assert res.loc[1, "lag_1"] == sample_feature_df.loc[0, "quantity"]

    # Row 7 lag_7 should equal Row 0 quantity
    assert res.loc[7, "lag_7"] == sample_feature_df.loc[0, "quantity"]


@pytest.mark.unit
def test_create_rolling_features_shift_exclusion(sample_feature_df: pd.DataFrame) -> None:
    """Verify rolling mean at step t equals exact average over [t-w, t-1] (excludes y_t)."""
    res = create_rolling_features(sample_feature_df, windows=[7])

    assert "rolling_mean_7" in res.columns
    assert "rolling_std_7" in res.columns

    # Row 7 rolling_mean_7 should equal mean of quantities from Row 0 through Row 6
    expected_mean = sample_feature_df.loc[0:6, "quantity"].mean()
    actual_mean = res.loc[7, "rolling_mean_7"]
    assert np.isclose(actual_mean, expected_mean)


@pytest.mark.unit
def test_create_trend_and_business_features(sample_feature_df: pd.DataFrame) -> None:
    """Verify trend ratios and commercial business signals."""
    lagged = create_lag_features(sample_feature_df, lags=[1, 7, 14, 28])
    rolled = create_rolling_features(lagged, windows=[7, 28])
    trended = create_trend_features(rolled)
    business = create_business_features(trended)

    assert "demand_growth_7_28" in business.columns
    assert "rolling_trend_7" in business.columns
    assert "discount_percentage" in business.columns
    assert "price_ratio" in business.columns
    assert "is_promoted_int" in business.columns

    # When price is 20 and unit_price is 25 -> discount is (25-20)/25 = 0.20
    promo_row = business[business["price"] == 20.0].iloc[0]
    assert np.isclose(promo_row["discount_percentage"], 0.20)
    assert promo_row["is_promoted_int"] == 1


@pytest.mark.unit
def test_feature_engineering_pipeline_end_to_end(sample_feature_df: pd.DataFrame) -> None:
    """Verify FeatureEngineeringPipeline end-to-end fit_transform and metadata tracking."""
    pipeline = FeatureEngineeringPipeline(dropna_warmup=True, lags=[1, 7, 14])
    transformed = pipeline.fit_transform(sample_feature_df)

    assert len(transformed) > 0
    # No NaNs in lag_14 column
    assert not transformed["lag_14"].isnull().any()

    meta = pipeline.get_feature_metadata(transformed)
    assert meta.total_features > 10
    assert "lag_1" in meta.lag_features
    assert "rolling_mean_7" in meta.rolling_features
    assert "sin_day_of_week" in meta.temporal_features
