"""Demand forecasting REST endpoints."""

from fastapi import APIRouter, HTTPException
import numpy as np
import pandas as pd

from foresight.api.schemas.forecast import (
    BatchForecastRequest,
    BatchForecastResponse,
    ForecastRequest,
    ForecastResponse,
)
from foresight.config.constants import MODELS_DIR
from foresight.forecasting.base import BaseForecaster
from foresight.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/forecast", tags=["Forecasting"])

_champion_model: BaseForecaster | None = None
_quantile_model: BaseForecaster | None = None


def get_models() -> tuple[BaseForecaster, BaseForecaster | None]:
    """Lazy load forecasting models."""
    global _champion_model, _quantile_model
    if _champion_model is None:
        c_path = MODELS_DIR / "champion_forecaster.pkl"
        if not c_path.exists():
            raise HTTPException(status_code=503, detail="Champion model artifact not found.")
        _champion_model = BaseForecaster.load(c_path)

    if _quantile_model is None:
        q_path = MODELS_DIR / "quantile_forecaster.pkl"
        if q_path.exists():
            _quantile_model = BaseForecaster.load(q_path)

    return _champion_model, _quantile_model


@router.post("/predict", response_model=ForecastResponse)
def predict_single(req: ForecastRequest) -> ForecastResponse:
    """Generate real-time point prediction and prediction interval for a single SKU-Store observation."""
    champ, quant = get_models()
    features = champ.feature_names_ or []

    # Construct input dataframe
    row_dict = {f: req.features.get(f, 0.0) for f in features}
    df = pd.DataFrame([row_dict]).replace([np.inf, -np.inf], np.nan).fillna(0.0)

    pred = float(champ.predict(df)[0])

    p10, p90 = None, None
    if quant is not None:
        try:
            q_res = quant.predict_quantiles(df, quantiles=[0.10, 0.90])
            p10 = max(0.0, float(q_res[0.10][0]))
            p90 = max(p10, float(q_res[0.90][0]))
        except Exception as e:
            logger.warning(f"Quantile interval inference failed: {e}")

    return ForecastResponse(
        sku_id=req.sku_id,
        store_id=req.store_id,
        date=req.date,
        predicted_demand=round(max(0.0, pred), 2),
        p10_lower_bound=round(p10, 2) if p10 is not None else None,
        p90_upper_bound=round(p90, 2) if p90 is not None else None,
        model_name=champ.name,
    )


@router.post("/predict/batch", response_model=BatchForecastResponse)
def predict_batch(req: BatchForecastRequest) -> BatchForecastResponse:
    """Generate batch point predictions and prediction intervals for a collection of SKU-Store items."""
    champ, quant = get_models()
    features = champ.feature_names_ or []

    rows = []
    for item in req.items:
        row_dict = {f: item.features.get(f, 0.0) for f in features}
        rows.append(row_dict)

    df = pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    preds = champ.predict(df)

    p10_list, p90_list = [None] * len(rows), [None] * len(rows)
    if quant is not None:
        try:
            q_res = quant.predict_quantiles(df, quantiles=[0.10, 0.90])
            p10_list = [max(0.0, float(v)) for v in q_res[0.10]]
            p90_list = [max(p10_list[i], float(v)) for i, v in enumerate(q_res[0.90])]
        except Exception as e:
            logger.warning(f"Batch quantile inference failed: {e}")

    results = []
    for i, item in enumerate(req.items):
        results.append(
            ForecastResponse(
                sku_id=item.sku_id,
                store_id=item.store_id,
                date=item.date,
                predicted_demand=round(max(0.0, float(preds[i])), 2),
                p10_lower_bound=round(p10_list[i], 2) if p10_list[i] is not None else None,
                p90_upper_bound=round(p90_list[i], 2) if p90_list[i] is not None else None,
                model_name=champ.name,
            )
        )

    return BatchForecastResponse(total_items=len(results), predictions=results)
