"""Demand forecasting models, baselines, ensembles, and trainer modules for Project FORESIGHT."""

from foresight.forecasting.base import BaseForecaster, ForecastResult
from foresight.forecasting.baselines import (
    ExponentialSmoothingForecaster,
    MovingAverageForecaster,
    NaiveForecaster,
    SeasonalNaiveForecaster,
)
from foresight.forecasting.ml_models import (
    GradientBoostingForecaster,
    LinearRegressionForecaster,
    QuantileGradientBoostingForecaster,
    RandomForestForecaster,
    XGBoostForecaster,
)
from foresight.forecasting.trainer import train_and_register_champion

__all__ = [
    "BaseForecaster",
    "ForecastResult",
    "NaiveForecaster",
    "SeasonalNaiveForecaster",
    "MovingAverageForecaster",
    "ExponentialSmoothingForecaster",
    "LinearRegressionForecaster",
    "RandomForestForecaster",
    "GradientBoostingForecaster",
    "XGBoostForecaster",
    "QuantileGradientBoostingForecaster",
    "train_and_register_champion",
]
