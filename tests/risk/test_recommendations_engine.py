"""Unit tests for the unified prescriptive recommendations engine."""

import pytest

from foresight.config.constants import RecommendationAction, RecommendationUrgency
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import InventoryParameters
from foresight.recommendations.engine import PrescriptiveEngine
from foresight.risk.scorer import assess_sku_risk


@pytest.mark.risk
def test_prescriptive_engine_stockout_imminent() -> None:
    """Verify EXPEDITE action generated when stockout is imminent."""
    engine = PrescriptiveEngine()

    params = InventoryParameters(
        sku_id="SKU-TEST",
        store_id="STORE-1",
        current_on_hand=2.0,
        units_on_order=0.0,
        backorders=0.0,
        unit_cost=10.0,
        unit_price=25.0,
        lead_time_days=7.0,
        forecast_daily_demand_mean=10.0,
        forecast_daily_demand_std=2.0,
    )

    optimizer = InventoryOptimizer()
    opt_result = optimizer.optimize_sku(params)

    risk = assess_sku_risk(opt_result, params)

    rec = engine.generate_recommendation(opt_result, risk, params)

    assert rec.action in [RecommendationAction.EXPEDITE, RecommendationAction.ORDER]
    assert rec.urgency in [RecommendationUrgency.CRITICAL, RecommendationUrgency.HIGH]
    assert rec.recommended_quantity > 0.0
    assert rec.expected_financial_impact > 0.0
    assert len(rec.justification) > 10
