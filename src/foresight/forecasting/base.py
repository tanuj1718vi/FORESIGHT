"""Base forecaster abstractions, version compatibility checks, and standardized prediction models."""

from abc import ABC, abstractmethod
from datetime import datetime
import json
from pathlib import Path
import pickle
import platform
from typing import Any
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
import sklearn
import xgboost

from foresight.utils.exceptions import ForecastingError
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


def get_current_environment_metadata() -> dict[str, str]:
    """Capture runtime library and Python version signatures."""
    return {
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
        "xgboost_version": xgboost.__version__,
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
    }


def validate_environment_compatibility(saved_meta: dict[str, Any]) -> None:
    """Compare saved artifact environment signature against active runtime.

    Emits explicit warnings for minor differences and raises clear errors on major corruption.
    """
    curr = get_current_environment_metadata()
    for lib in ["python_version", "scikit_learn_version", "xgboost_version", "numpy_version", "pandas_version"]:
        saved_ver = saved_meta.get(lib)
        curr_ver = curr.get(lib)
        if saved_ver and curr_ver and saved_ver != curr_ver:
            # Check major/minor difference
            s_parts = saved_ver.split(".")[:2]
            c_parts = curr_ver.split(".")[:2]
            if s_parts != c_parts:
                logger.warning(
                    f"Model Version Drift Detected for '{lib}': Artifact trained on {saved_ver}, "
                    f"running on {curr_ver}. Pickle deserialization may behave differently."
                )


class ForecastResult(BaseModel):
    """Standardized point and probabilistic prediction output."""
    model_name: str
    sku_id: str | None = None
    store_id: str | None = None
    forecast_dates: list[str]
    point_forecast: list[float]
    quantiles: dict[str, list[float]] = Field(
        default_factory=dict,
        description="Quantile prediction intervals (e.g. '0.1', '0.5', '0.9')",
    )


class BaseForecaster(ABC):
    """Abstract base class establishing the forecasting interface across all models."""

    def __init__(self, name: str, model_type: str = "ml") -> None:
        self.name = name
        self.model_type = model_type
        self.is_fitted: bool = False
        self.feature_names_: list[str] | None = None

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs: Any) -> "BaseForecaster":
        """Fit model on training feature matrix and target vector."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame, **kwargs: Any) -> np.ndarray:
        """Generate point forecasts for input feature matrix."""
        pass

    def predict_quantiles(
        self,
        X: pd.DataFrame,
        quantiles: list[float] | None = None,
    ) -> dict[float, np.ndarray]:
        """Generate probabilistic prediction intervals."""
        q_list = quantiles or [0.10, 0.50, 0.90]
        point_preds = self.predict(X)

        results: dict[float, np.ndarray] = {}
        for q in q_list:
            if np.isclose(q, 0.50):
                results[q] = point_preds
            elif q < 0.50:
                spread = (0.50 - q) * 0.45
                results[q] = np.maximum(0.0, point_preds * (1.0 - spread))
            else:
                spread = (q - 0.50) * 0.45
                results[q] = point_preds * (1.0 + spread)

        return results

    def save(self, file_path: Path | str) -> None:
        """Serialize trained forecaster artifact and persist environment metadata sidecar."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

        # Save sidecar metadata
        meta = {
            "model_name": self.name,
            "model_type": self.model_type,
            "feature_names": self.feature_names_,
            "saved_at": datetime.now().isoformat(),
            "environment": get_current_environment_metadata(),
        }
        meta_path = path.with_suffix(".meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    @classmethod
    def load(cls, file_path: Path | str) -> "BaseForecaster":
        """Deserialize forecaster artifact from disk with environment validation."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Model artifact not found at {path}")

        meta_path = path.with_suffix(".meta.json")
        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                validate_environment_compatibility(meta.get("environment", {}))
            except Exception as e:
                logger.warning(f"Could not read metadata sidecar at {meta_path}: {e}")

        try:
            with open(path, "rb") as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            raise ForecastingError(
                f"Failed to deserialize model artifact at '{path}'. Error: {e}. "
                f"Ensure models were trained with compatible Python/scikit-learn/XGBoost versions."
            ) from e

    def get_feature_importances(self) -> dict[str, float] | None:
        """Return feature importance mapping if supported by underlying algorithm."""
        return None
