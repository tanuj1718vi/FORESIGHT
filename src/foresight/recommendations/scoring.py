"""Prescriptive scoring and confidence estimation algorithms."""

from foresight.inventory.schema import InventoryParameters


def calculate_recommendation_confidence(
    params: InventoryParameters,
    confidence_baseline: float = 0.90,
) -> float:
    """Compute confidence score based on demand coefficient of variation (CV)."""
    cv_demand = params.forecast_daily_demand_std / (params.forecast_daily_demand_mean + 1e-5)
    return float(max(0.65, min(0.98, confidence_baseline - (cv_demand * 0.10))))
