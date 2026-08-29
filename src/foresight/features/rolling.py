"""Leakage-safe rolling window statistical transformations for Project FORESIGHT."""

import pandas as pd


def create_rolling_features(
    df: pd.DataFrame,
    target_col: str = "quantity",
    group_cols: list[str] | None = None,
    date_col: str = "date",
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """Generate strictly causal rolling statistics over past observations (shift=1).

    CRITICAL LEAKAGE SAFETY:
    Rolling aggregations at time step t are computed exclusively over observations
    from t-1 backward to t-w. The contemporaneous target value y_t is NEVER included.

    Args:
        df: Input DataFrame.
        target_col: Target variable column name.
        group_cols: Primary grouping keys (default: ['sku_id', 'store_id']).
        date_col: Date column name.
        windows: Rolling window day spans (default: [7, 14, 28]).

    Returns:
        DataFrame with rolling mean, std, min, max features.
    """
    data = df.copy()
    groups = group_cols or ["sku_id", "store_id"]
    window_sizes = windows or [7, 14, 28]

    # Ensure deterministic sort order
    data = data.sort_values(by=groups + [date_col]).reset_index(drop=True)

    # Shift by 1 first to strictly exclude the current observation y_t
    shifted_target = data.groupby(groups)[target_col].shift(1)

    for w in window_sizes:
        # Grouped rolling on shifted series
        rolling_obj = shifted_target.groupby([data[col] for col in groups]).rolling(
            window=w, min_periods=w
        )

        data[f"rolling_mean_{w}"] = rolling_obj.mean().reset_index(drop=True)
        data[f"rolling_std_{w}"] = rolling_obj.std().reset_index(drop=True)
        data[f"rolling_min_{w}"] = rolling_obj.min().reset_index(drop=True)
        data[f"rolling_max_{w}"] = rolling_obj.max().reset_index(drop=True)

    return data
