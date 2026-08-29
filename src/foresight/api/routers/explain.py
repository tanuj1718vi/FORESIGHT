"""Explainability REST endpoints."""

from fastapi import APIRouter
import numpy as np
import pandas as pd

from foresight.api.routers.forecast import get_models
from foresight.api.schemas.explain import ExplainRequest, ExplainResponse
from foresight.explainability.shap_explainer import ForecastExplainer

router = APIRouter(prefix="/api/v1/explain", tags=["Model Explainability"])
_explainer: ForecastExplainer | None = None


def get_explainer() -> ForecastExplainer:
    """Lazy initialize TreeSHAP explainer."""
    global _explainer
    if _explainer is None:
        champ, _ = get_models()
        _explainer = ForecastExplainer(champ)
    return _explainer


@router.post("/drivers", response_model=ExplainResponse)
def explain_drivers(req: ExplainRequest) -> ExplainResponse:
    """Generate TreeSHAP local driver attributions and executive narrative for a single forecast."""
    explainer = get_explainer()
    champ, _ = get_models()
    features = champ.feature_names_ or []

    row_dict = {f: req.features.get(f, 0.0) for f in features}
    row_series = pd.Series(row_dict)

    explanation = explainer.explain_observation(
        row_features=row_series,
        sku_id=req.sku_id,
        store_id=req.store_id,
        date=req.date,
    )

    return ExplainResponse(
        sku_id=explanation.sku_id,
        store_id=explanation.store_id,
        date=explanation.date,
        base_value=explanation.base_value,
        predicted_value=explanation.predicted_value,
        top_positive_drivers=explanation.top_positive_drivers,
        top_negative_drivers=explanation.top_negative_drivers,
        business_narrative=explanation.business_narrative,
    )
