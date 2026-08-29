"""Temporal and calendar feature transformations for Project FORESIGHT."""

import numpy as np
import pandas as pd


def create_calendar_features(
    df: pd.DataFrame,
    date_col: str = "date",
) -> pd.DataFrame:
    """Generate calendar, seasonal, and cyclical trigonometric features from date column.

    Features generated:
    - day_of_week (0 = Monday, 6 = Sunday)
    - day_of_month (1 - 31)
    - week_of_year (1 - 53)
    - month (1 - 12)
    - quarter (1 - 4)
    - year
    - is_weekend (0 or 1)
    - sin_day_of_week, cos_day_of_week
    - sin_month, cos_month
    """
    data = df.copy()
    dt = pd.to_datetime(data[date_col])

    data["day_of_week"] = dt.dt.dayofweek
    data["day_of_month"] = dt.dt.day
    data["week_of_year"] = dt.dt.isocalendar().week.astype(int)
    data["month"] = dt.dt.month
    data["quarter"] = dt.dt.quarter
    data["year"] = dt.dt.year
    data["is_weekend"] = data["day_of_week"].isin([5, 6]).astype(int)

    # Cyclical trigonometric encodings
    data["sin_day_of_week"] = np.sin(2.0 * np.pi * data["day_of_week"] / 7.0).round(5)
    data["cos_day_of_week"] = np.cos(2.0 * np.pi * data["day_of_week"] / 7.0).round(5)
    data["sin_month"] = np.sin(2.0 * np.pi * (data["month"] - 1) / 12.0).round(5)
    data["cos_month"] = np.cos(2.0 * np.pi * (data["month"] - 1) / 12.0).round(5)

    return data
