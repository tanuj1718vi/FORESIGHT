"""Autoregressive lag feature generation for Project FORESIGHT."""

import pandas as pd


def create_lag_features(
    df: pd.DataFrame,
    target_col: str = "quantity",
    group_cols: list[str] | None = None,
    date_col: str = "date",
    lags: list[int] | None = None,
) -> pd.DataFrame:
    """Generate strictly backward-shifted autoregressive lag features for each time-series group.

    Args:
        df: Input DataFrame.
        target_col: Target variable column name (e.g. quantity).
        group_cols: Primary time-series grouping keys (default: ['sku_id', 'store_id']).
        date_col: Timestamp column name.
        lags: List of integer retrospective lag offsets (default: [1, 7, 14, 21, 28, 56]).

    Returns:
        DataFrame with new columns: lag_1, lag_7, lag_14, lag_21, lag_28, lag_56.
    """
    data = df.copy()
    groups = group_cols or ["sku_id", "store_id"]
    lag_offsets = lags or [1, 7, 14, 21, 28, 56]

    # Ensure deterministic sort order
    data = data.sort_values(by=groups + [date_col]).reset_index(drop=True)

    grouped = data.groupby(groups)[target_col]

    for lag in lag_offsets:
        col_name = f"lag_{lag}"
        data[col_name] = grouped.shift(lag)

    return data
