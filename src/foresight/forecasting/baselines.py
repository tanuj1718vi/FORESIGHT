"""Baseline and classical statistical forecasting models for Project FORESIGHT."""

from typing import Any
import numpy as np
import pandas as pd

from foresight.forecasting.base import BaseForecaster


class NaiveForecaster(BaseForecaster):
    """Persistence baseline model predicting most recent observed lag (y_hat = lag_1)."""

    def __init__(self) -> None:
        super().__init__(name="Naive (Persistence)", model_type="baseline")
        self.last_observed_mean_: float = 0.0

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "NaiveForecaster":
        self.last_observed_mean_ = float(np.mean(y[-7:])) if len(y) > 0 else 0.0
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        if "lag_1" in X.columns:
            preds = X["lag_1"].fillna(self.last_observed_mean_).values
        else:
            preds = np.full(len(X), self.last_observed_mean_)
        return np.maximum(0.0, preds)


class SeasonalNaiveForecaster(BaseForecaster):
    """Weekly seasonal persistence model (y_hat = lag_7)."""

    def __init__(self, season_length: int = 7) -> None:
        super().__init__(name=f"Seasonal Naive (s={season_length})", model_type="baseline")
        self.season_length = season_length
        self.last_observed_mean_: float = 0.0

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "SeasonalNaiveForecaster":
        self.last_observed_mean_ = float(np.mean(y[-self.season_length:])) if len(y) > 0 else 0.0
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        lag_col = f"lag_{self.season_length}"
        if lag_col in X.columns:
            preds = X[lag_col].fillna(self.last_observed_mean_).values
        elif "lag_1" in X.columns:
            preds = X["lag_1"].fillna(self.last_observed_mean_).values
        else:
            preds = np.full(len(X), self.last_observed_mean_)
        return np.maximum(0.0, preds)


class MovingAverageForecaster(BaseForecaster):
    """Rolling moving average baseline forecaster."""

    def __init__(self, window: int = 7) -> None:
        super().__init__(name=f"Moving Average ({window}d)", model_type="baseline")
        self.window = window
        self.mean_demand_: float = 0.0

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "MovingAverageForecaster":
        self.mean_demand_ = float(np.mean(y[-self.window:])) if len(y) > 0 else 0.0
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        roll_col = f"rolling_mean_{self.window}"
        if roll_col in X.columns:
            preds = X[roll_col].fillna(self.mean_demand_).values
        else:
            preds = np.full(len(X), self.mean_demand_)
        return np.maximum(0.0, preds)


class ExponentialSmoothingForecaster(BaseForecaster):
    """Holt-Winters Exponential Smoothing forecaster with trend and seasonal weighting."""

    def __init__(self, alpha: float = 0.3, beta: float = 0.1, gamma: float = 0.2, season_length: int = 7) -> None:
        super().__init__(name="Exponential Smoothing (Holt-Winters)", model_type="classical")
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.season_length = season_length
        self.level_: float = 0.0
        self.trend_: float = 0.0
        self.seasonals_: np.ndarray = np.ones(season_length)

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "ExponentialSmoothingForecaster":
        if len(y) < self.season_length * 2:
            self.level_ = float(np.mean(y)) if len(y) > 0 else 0.0
            self.is_fitted = True
            return self

        # Initialize components
        self.seasonals_ = np.array([
            float(np.mean(y[i :: self.season_length])) / (np.mean(y) + 1e-5)
            for i in range(self.season_length)
        ])
        self.level_ = float(y[0] / (self.seasonals_[0] + 1e-5))
        self.trend_ = float((np.mean(y[self.season_length : self.season_length * 2]) - np.mean(y[:self.season_length])) / self.season_length)

        # Smooth over training series
        for t in range(len(y)):
            val = y[t]
            s_idx = t % self.season_length
            last_level = self.level_
            self.level_ = self.alpha * (val / (self.seasonals_[s_idx] + 1e-5)) + (1.0 - self.alpha) * (self.level_ + self.trend_)
            self.trend_ = self.beta * (self.level_ - last_level) + (1.0 - self.beta) * self.trend_
            self.seasonals_[s_idx] = self.gamma * (val / (self.level_ + 1e-5)) + (1.0 - self.gamma) * self.seasonals_[s_idx]

        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        n = len(X)
        preds = np.zeros(n)
        for h in range(n):
            s_idx = h % self.season_length
            pred = (self.level_ + (h + 1) * self.trend_) * self.seasonals_[s_idx]
            preds[h] = pred
        return np.maximum(0.0, preds)
