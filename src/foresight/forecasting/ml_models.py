"""Machine learning and probabilistic quantile forecasters for Project FORESIGHT."""

from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from foresight.forecasting.base import BaseForecaster
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


class LinearRegressionForecaster(BaseForecaster):
    """Ridge regularized linear regression forecaster with feature scaling."""

    def __init__(self, alpha: float = 1.0) -> None:
        super().__init__(name="Ridge Linear Regression", model_type="ml")
        self.alpha = alpha
        self.pipeline: Pipeline | None = None

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "LinearRegressionForecaster":
        self.feature_names_ = list(X.columns)
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", Ridge(alpha=self.alpha)),
        ])
        # Replace infs and fillna
        clean_X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        self.pipeline.fit(clean_X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        if not self.is_fitted or self.pipeline is None:
            raise RuntimeError("Model is not fitted.")
        clean_X = X[self.feature_names_].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        preds = self.pipeline.predict(clean_X)
        return np.maximum(0.0, preds)

    def get_feature_importances(self) -> dict[str, float] | None:
        if not self.is_fitted or self.pipeline is None or self.feature_names_ is None:
            return None
        coefs = self.pipeline.named_steps["regressor"].coef_
        return {feat: round(float(abs(c)), 4) for feat, c in zip(self.feature_names_, coefs, strict=False)}


class RandomForestForecaster(BaseForecaster):
    """Random Forest bagging ensemble forecaster."""

    def __init__(self, n_estimators: int = 100, max_depth: int = 12, random_state: int = 42) -> None:
        super().__init__(name="Random Forest", model_type="ml")
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "RandomForestForecaster":
        self.feature_names_ = list(X.columns)
        clean_X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        self.model.fit(clean_X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted.")
        clean_X = X[self.feature_names_].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        preds = self.model.predict(clean_X)
        return np.maximum(0.0, preds)

    def get_feature_importances(self) -> dict[str, float] | None:
        if not self.is_fitted or self.feature_names_ is None:
            return None
        importances = self.model.feature_importances_
        return {feat: round(float(imp), 4) for feat, imp in zip(self.feature_names_, importances, strict=False)}


class GradientBoostingForecaster(BaseForecaster):
    """Histogram-based Gradient Boosted Trees forecaster."""

    def __init__(self, max_iter: int = 120, max_depth: int = 8, random_state: int = 42) -> None:
        super().__init__(name="Gradient Boosting (HistGBM)", model_type="ml")
        self.model = HistGradientBoostingRegressor(
            max_iter=max_iter,
            max_depth=max_depth,
            random_state=random_state,
        )

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "GradientBoostingForecaster":
        self.feature_names_ = list(X.columns)
        clean_X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        self.model.fit(clean_X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted.")
        clean_X = X[self.feature_names_].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        preds = self.model.predict(clean_X)
        return np.maximum(0.0, preds)


class XGBoostForecaster(BaseForecaster):
    """Extreme Gradient Boosting (XGBoost) high-performance forecaster."""

    def __init__(
        self,
        n_estimators: int = 150,
        max_depth: int = 6,
        learning_rate: float = 0.08,
        subsample: float = 0.85,
        colsample_bytree: float = 0.85,
        random_state: int = 42,
    ) -> None:
        super().__init__(name="XGBoost", model_type="ml")
        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=random_state,
            n_jobs=-1,
        )

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "XGBoostForecaster":
        self.feature_names_ = list(X.columns)
        clean_X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        self.model.fit(clean_X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted.")
        clean_X = X[self.feature_names_].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        preds = self.model.predict(clean_X)
        return np.maximum(0.0, preds)

    def get_feature_importances(self) -> dict[str, float] | None:
        if not self.is_fitted or self.feature_names_ is None:
            return None
        importances = self.model.feature_importances_
        return {feat: round(float(imp), 4) for feat, imp in zip(self.feature_names_, importances, strict=False)}


class QuantileGradientBoostingForecaster(BaseForecaster):
    """Probabilistic forecaster training pinball quantile regressors (P10, P50, P90)."""

    def __init__(
        self,
        quantiles: list[float] | None = None,
        max_iter: int = 100,
        max_depth: int = 6,
        random_state: int = 42,
    ) -> None:
        super().__init__(name="Quantile Gradient Boosting (P10/P50/P90)", model_type="ml")
        self.quantiles = quantiles or [0.10, 0.50, 0.90]
        self.max_iter = max_iter
        self.max_depth = max_depth
        self.random_state = random_state
        self.models: dict[float, HistGradientBoostingRegressor] = {}

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "QuantileGradientBoostingForecaster":
        self.feature_names_ = list(X.columns)
        clean_X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)

        for q in self.quantiles:
            logger.info(f"Fitting quantile model for alpha={q:.2f}...")
            q_model = HistGradientBoostingRegressor(
                loss="quantile",
                quantile=q,
                max_iter=self.max_iter,
                max_depth=self.max_depth,
                random_state=self.random_state,
            )
            q_model.fit(clean_X, y)
            self.models[q] = q_model

        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        """Point forecast returns median (P50) prediction."""
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted.")
        median_q = 0.50 if 0.50 in self.models else self.quantiles[len(self.quantiles) // 2]
        clean_X = X[self.feature_names_].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        preds = self.models[median_q].predict(clean_X)
        return np.maximum(0.0, preds)

    def predict_quantiles(
        self,
        X: pd.DataFrame,
        quantiles: list[float] | None = None,
    ) -> dict[float, np.ndarray]:
        """Generate calibrated probabilistic quantile intervals."""
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted.")
        clean_X = X[self.feature_names_].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        results: dict[float, np.ndarray] = {}

        target_quantiles = quantiles or self.quantiles
        for q in target_quantiles:
            if q in self.models:
                preds = self.models[q].predict(clean_X)
            else:
                # Find closest quantile or fallback
                closest_q = min(self.models.keys(), key=lambda k: abs(k - q))
                preds = self.models[closest_q].predict(clean_X)
            results[q] = np.maximum(0.0, preds)

        # Enforce quantile monotonicity: P10 <= P50 <= P90
        sorted_qs = sorted(results.keys())
        for i in range(1, len(sorted_qs)):
            prev_q = sorted_qs[i - 1]
            curr_q = sorted_qs[i]
            results[curr_q] = np.maximum(results[curr_q], results[prev_q])

        return results
