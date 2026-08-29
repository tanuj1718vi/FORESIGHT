"""Unit tests for Prescriptive Recommendation Engine and lateral rebalancing."""

import pytest

from foresight.config.constants import RecommendationAction, RecommendationUrgency
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import InventoryParameters
from foresight.risk.prescriptive import PrescriptiveEngine
from foresight.risk.scorer import assess_sku_risk


@pytest.fixture
def depleted_sku_params() -> InventoryParameters:
    return InventoryParameters(
        sku_id="SKU-2001",
        store_id="STORE-001",
        current_on_hand=2.0,
        units_on_order=0.0,
        backorders=0.0,
        unit_cost=20.0,
        unit_price=50.0,
        lead_time_days=7.0,
        lead_time_std_days=1.0,
        holding_cost_annual_rate=0.20,
        fixed_order_cost=50.0,
        min_order_qty=10.0,
        target_service_level=0.95,
        forecast_daily_demand_mean=15.0,
        forecast_daily_demand_std=3.0,
    )


@pytest.fixture
def surplus_sku_params() -> InventoryParameters:
    return InventoryParameters(
        sku_id="SKU-2001",
        store_id="STORE-002",
        current_on_hand=300.0,
        units_on_order=0.0,
        backorders=0.0,
        unit_cost=20.0,
        unit_price=50.0,
        lead_time_days=7.0,
        lead_time_std_days=1.0,
        holding_cost_annual_rate=0.20,
        fixed_order_cost=50.0,
        min_order_qty=10.0,
        target_service_level=0.95,
        forecast_daily_demand_mean=3.0,
        forecast_daily_demand_std=0.5,
    )


@pytest.mark.risk
def test_generate_recommendation_stockout_imminent(depleted_sku_params: InventoryParameters) -> None:
    """Verify depleted SKU generates EXPEDITE action with business justification."""
    optimizer = InventoryOptimizer()
    engine = PrescriptiveEngine()

    opt_res = optimizer.optimize_sku(depleted_sku_params)
    risk = assess_sku_risk(opt_res, depleted_sku_params)
    rec = engine.generate_recommendation(opt_res, risk, depleted_sku_params)

    assert rec.action == RecommendationAction.EXPEDITE
    assert rec.urgency == RecommendationUrgency.CRITICAL
    assert rec.recommended_quantity > 0
    assert "Imminent stockout" in rec.justification
    assert rec.expected_financial_impact > 0.0


@pytest.mark.risk
def test_lateral_rebalance_detection(
    depleted_sku_params: InventoryParameters,
    surplus_sku_params: InventoryParameters,
) -> None:
    """Verify lateral stock transfer is generated between overstocked and understocked stores."""
    optimizer = InventoryOptimizer()
    engine = PrescriptiveEngine()

    opt_dep = optimizer.optimize_sku(depleted_sku_params)
    risk_dep = assess_sku_risk(opt_dep, depleted_sku_params)
    rec_dep = engine.generate_recommendation(opt_dep, risk_dep, depleted_sku_params)

    opt_sur = optimizer.optimize_sku(surplus_sku_params)
    risk_sur = assess_sku_risk(opt_sur, surplus_sku_params)
    rec_sur = engine.generate_recommendation(opt_sur, risk_sur, surplus_sku_params)

    rebalances = engine.identify_lateral_rebalance_opportunities(
        recommendations=[rec_dep, rec_sur],
        inventory_results=[opt_dep, opt_sur],
    )

    assert len(rebalances) == 1
    rebal = rebalances[0]
    assert rebal.action == RecommendationAction.REBALANCE
    assert rebal.sku_id == "SKU-2001"
    assert rebal.store_id == "STORE-001"  # Recipient
    assert rebal.donor_store_id == "STORE-002"  # Donor
    assert rebal.recommended_quantity >= 10.0
