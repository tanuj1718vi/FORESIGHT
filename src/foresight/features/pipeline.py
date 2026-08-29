"""Unified Leakage-Safe Feature Engineering Pipeline for Project FORESIGHT."""

from typing import Any
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from foresight.features.business import create_business_features
from foresight.features.lags import create_lag_features
from foresight.features.rolling import create_rolling_features
from foresight.features.temporal import create_calendar_features
from foresight.features.trend import create_trend_features
from foresight.utils.logger import get_logger

logger = get_logger(__name__)


class FeatureMetadata(BaseModel):
    """Metadata schema documenting generated feature sets."""
    total_features: int
    feature_names: list[str]
    temporal_features: list[str]
    lag_features: list[str]
    rolling_features: list[str]
    trend_features: list[str]
    business_features: list[str]
    categorical_features: list[str]
    target_column: str = "quantity"
    warmup_days_required: int = 56


class FeatureEngineeringPipeline:
    """End-to-end transformer generating ML-ready feature matrices from processed sales."""

    def __init__(
        self,
        target_col: str = "quantity",
        date_col: str = "date",
        group_cols: list[str] | None = None,
        lags: list[int] | None = None,
        windows: list[int] | None = None,
        dropna_warmup: bool = True,
    ) -> None:
        self.target_col = target_col
        self.date_col = date_col
        self.group_cols = group_cols or ["sku_id", "store_id"]
        self.lags = lags or [1, 7, 14, 21, 28, 56]
        self.windows = windows or [7, 14, 28]
        self.dropna_warmup = dropna_warmup

        # Learned encodings for categoricals
        self._category_mapping: dict[str, int] = {}
        self._store_mapping: dict[str, int] = {}
        self._sku_mapping: dict[str, int] = {}
        self._is_fitted: bool = False

    def fit(self, df: pd.DataFrame) -> "FeatureEngineeringPipeline":
        """Learn categorical encodings from historical training dataset."""
        if "category" in df.columns:
            cats = sorted(df["category"].astype(str).unique())
            self._category_mapping = {c: i for i, c in enumerate(cats)}

        if "store_id" in df.columns:
            stores = sorted(df["store_id"].astype(str).unique())
            self._store_mapping = {s: i for i, s in enumerate(stores)}

        if "sku_id" in df.columns:
            skus = sorted(df["sku_id"].astype(str).unique())
            self._sku_mapping = {sku: i for i, sku in enumerate(skus)}

        self._is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature transformations with strict temporal causality."""
        logger.info(f"Transforming feature matrix for {len(df):,} records...")

        # 1. Temporal & Calendar Features
        data = create_calendar_features(df, date_col=self.date_col)

        # 2. Autoregressive Lags
        data = create_lag_features(
            data,
            target_col=self.target_col,
            group_cols=self.group_cols,
            date_col=self.date_col,
            lags=self.lags,
        )

        # 3. Leakage-Safe Rolling Statistics (shift=1)
        data = create_rolling_features(
            data,
            target_col=self.target_col,
            group_cols=self.group_cols,
            date_col=self.date_col,
            windows=self.windows,
        )

        # 4. Trend & Velocity Features
        data = create_trend_features(data)

        # 5. Commercial & Inventory Features
        data = create_business_features(
            data,
            unit_price_col="unit_price",
            price_col="price",
            promo_col="is_promoted",
            inventory_col="inventory_level",
            rolling_demand_col="rolling_mean_7",
        )

        # 6. Categorical Integer Encodings
        if self._is_fitted:
            if "category" in data.columns:
                data["category_code"] = data["category"].astype(str).map(self._category_mapping).fillna(-1).astype(int)
            if "store_id" in data.columns:
                data["store_code"] = data["store_id"].astype(str).map(self._store_mapping).fillna(-1).astype(int)
            if "sku_id" in data.columns:
                data["sku_code"] = data["sku_id"].astype(str).map(self._sku_mapping).fillna(-1).astype(int)

        # 7. Warmup Truncation (Optional)
        if self.dropna_warmup:
            max_lag = max(self.lags) if self.lags else 0
            # Drop records where max_lag is NaN to yield complete matrices for ML training
            before_len = len(data)
            data = data.dropna(subset=[f"lag_{max_lag}"]).reset_index(drop=True)
            logger.info(
                f"Dropped {before_len - len(data):,} initial warmup records (max lag = {max_lag} days). Remaining: {len(data):,}"
            )

        return data

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit categorical mappings and transform input DataFrame."""
        return self.fit(df).transform(df)

    def get_feature_names(self, df: pd.DataFrame) -> list[str]:
        """Return list of generated predictive feature columns (excluding identifiers and target)."""
        exclude = {
            self.target_col,
            self.date_col,
            "product_name",
            "category",
            "subcategory",
            "sku_id",
            "store_id",
            "demand_pattern",
            "is_promoted",
            "backorders",
            "base_demand_rate",
            "holding_cost_annual_rate",
        }
        return [c for c in df.columns if c not in exclude]

    def get_feature_metadata(self, df: pd.DataFrame) -> FeatureMetadata:
        """Generate structured metadata summarizing the engineered feature space."""
        all_features = self.get_feature_names(df)

        temporal = [c for c in all_features if any(k in c for k in ["day", "week", "month", "quarter", "year", "sin", "cos"])]
        lag = [c for c in all_features if c.startswith("lag_")]
        rolling = [c for c in all_features if c.startswith("rolling_")]
        trend = [c for c in all_features if any(k in c for k in ["trend", "growth", "momentum"])]
        business = [c for c in all_features if any(k in c for k in ["discount", "price", "promo", "inventory", "days_of_"])]
        categorical = [c for c in all_features if c.endswith("_code")]

        return FeatureMetadata(
            total_features=len(all_features),
            feature_names=all_features,
            temporal_features=temporal,
            lag_features=lag,
            rolling_features=rolling,
            trend_features=trend,
            business_features=business,
            categorical_features=categorical,
            target_column=self.target_col,
            warmup_days_required=max(self.lags) if self.lags else 0,
        )
