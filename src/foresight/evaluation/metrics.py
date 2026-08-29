"""Time-series forecasting evaluation metrics and zero-safe scoring formulas."""

from typing import Any
import numpy as np
from pydantic import BaseModel, Field


class MetricScoreSet(BaseModel):
    """Container for comprehensive forecast evaluation metrics."""
    mae: float = Field(..., description="Mean Absolute Error")
    rmse: float = Field(..., description="Root Mean Squared Error")
    wape: float = Field(..., description="Weighted Absolute Percentage Error")
    smape: float = Field(..., description="Symmetric Mean Absolute Percentage Error (Percentage)")
    mape: float = Field(..., description="Mean Absolute Percentage Error (Zero-Safe Percentage)")
    mase: float | None = Field(default=None, description="Mean Absolute Scaled Error")
    r2: float = Field(..., description="Coefficient of Determination")
    total_actual_volume: float = Field(..., description="Sum of true actual units")
    total_forecast_volume: float = Field(..., description="Sum of predicted units")
    sample_size: int = Field(..., description="Number of evaluated observations")


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Mean Absolute Error (MAE)."""
    return float(np.mean(np.abs(y_true - y_pred)))


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Root Mean Squared Error (RMSE)."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def weighted_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Weighted Absolute Percentage Error (WAPE).

    Formula: WAPE = sum(|y_true - y_pred|) / sum(y_true)
    Industry gold-standard for retail demand forecasting; handles zero-demand days gracefully.
    """
    total_actual = np.sum(y_true)
    if total_actual == 0:
        return 0.0 if np.sum(np.abs(y_pred)) == 0 else 1.0
    return float(np.sum(np.abs(y_true - y_pred)) / total_actual)


calculate_wape = weighted_absolute_percentage_error


def symmetric_mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Symmetric Mean Absolute Percentage Error (sMAPE) in percentage (0 to 200%)."""
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    # Avoid zero division when both true and pred are zero
    zero_mask = denominator == 0
    smape_elements = np.zeros_like(y_true, dtype=float)
    smape_elements[~zero_mask] = np.abs(y_pred[~zero_mask] - y_true[~zero_mask]) / denominator[~zero_mask]
    return float(np.mean(smape_elements) * 100.0)


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute Zero-Safe Mean Absolute Percentage Error (MAPE)."""
    non_zero_mask = y_true != 0
    if not np.any(non_zero_mask):
        return 0.0
    return float(np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100.0)


def mean_absolute_scaled_error(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_train: np.ndarray | None = None,
    seasonality: int = 7,
) -> float | None:
    """Compute Mean Absolute Scaled Error (MASE) against in-sample seasonal naive baseline."""
    if y_train is None or len(y_train) <= seasonality:
        return None
    scale = np.mean(np.abs(y_train[seasonality:] - y_train[:-seasonality]))
    if scale == 0:
        # Fallback to non-seasonal lag-1 scale or epsilon
        scale = np.mean(np.abs(np.diff(y_train)))
        if scale == 0:
            scale = 1e-5
    mae_val = mean_absolute_error(y_true, y_pred)
    return float(mae_val / scale)


def pinball_loss(y_true: np.ndarray, y_pred_q: np.ndarray, quantile: float) -> float:
    """Compute Pinball / Quantile Loss for probabilistic forecast verification."""
    residual = y_true - y_pred_q
    loss = np.maximum(quantile * residual, (quantile - 1.0) * residual)
    return float(np.mean(loss))


def evaluate_predictions(
    y_true: np.ndarray | list[float],
    y_pred: np.ndarray | list[float],
    y_train: np.ndarray | list[float] | None = None,
    seasonality: int = 7,
) -> MetricScoreSet:
    """Evaluate predictions across the full standard suite of forecasting metrics."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    y_tr = np.asarray(y_train, dtype=float) if y_train is not None else None

    mae_val = mean_absolute_error(y_t, y_p)
    rmse_val = root_mean_squared_error(y_t, y_p)
    wape_val = weighted_absolute_percentage_error(y_t, y_p)
    smape_val = symmetric_mean_absolute_percentage_error(y_t, y_p)
    mape_val = mean_absolute_percentage_error(y_t, y_p)
    mase_val = mean_absolute_scaled_error(y_t, y_p, y_tr, seasonality=seasonality)

    # R2 Calculation
    ss_res = np.sum((y_t - y_p) ** 2)
    ss_tot = np.sum((y_t - np.mean(y_t)) ** 2)
    r2_val = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

    return MetricScoreSet(
        mae=round(mae_val, 3),
        rmse=round(rmse_val, 3),
        wape=round(wape_val, 4),
        smape=round(smape_val, 2),
        mape=round(mape_val, 2),
        mase=round(mase_val, 3) if mase_val is not None else None,
        r2=round(r2_val, 4),
        total_actual_volume=float(np.sum(y_t)),
        total_forecast_volume=round(float(np.sum(y_p)), 2),
        sample_size=len(y_t),
    )
