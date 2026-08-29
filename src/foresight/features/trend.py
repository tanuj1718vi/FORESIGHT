"""Trend, velocity, and momentum feature generators for Project FORESIGHT."""

import numpy as np
import pandas as pd


def create_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate velocity, acceleration, and relative momentum features.

    Features generated:
    - demand_growth_7_28: Short-term (7d) vs long-term (28d) rolling mean growth ratio.
    - rolling_trend_7: 7-day rolling mean velocity relative to lag_7.
    - rolling_trend_14: 14-day rolling mean velocity relative to lag_14.
    - momentum_7_1: Single-day step momentum relative to 1 week prior.
    """
    data = df.copy()
    eps = 1e-5

    # 1. Medium-to-Long term growth
    if "rolling_mean_7" in data.columns and "rolling_mean_28" in data.columns:
        data["demand_growth_7_28"] = (
            (data["rolling_mean_7"] - data["rolling_mean_28"]) / (data["rolling_mean_28"] + eps)
        )

    # 2. Rolling Trend relative to seasonal lag
    if "rolling_mean_7" in data.columns and "lag_7" in data.columns:
        data["rolling_trend_7"] = (
            (data["rolling_mean_7"] - data["lag_7"]) / (data["lag_7"] + eps)
        )

    if "rolling_mean_14" in data.columns and "lag_14" in data.columns:
        data["rolling_trend_14"] = (
            (data["rolling_mean_14"] - data["lag_14"]) / (data["lag_14"] + eps)
        )

    # 3. Step Momentum
    if "lag_1" in data.columns and "lag_7" in data.columns:
        data["momentum_7_1"] = (
            (data["lag_1"] - data["lag_7"]) / (data["lag_7"] + eps)
        )

    return data
