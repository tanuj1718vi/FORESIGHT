"""Unit tests for InventoryOptimizer engine and policy decisions."""

import pytest

from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import (
    InventoryHealthStatus,
    InventoryParameters,
    OrderAction,
    SafetyStockMethod,
)


@pytest.fixture
def stockout_risk_sku() -> InventoryParameters:
    """Provide SKU parameters with dangerously depleted inventory."""
    return InventoryParameters(
        sku_id="SKU-1001",
        store_id="STORE-001",
        current_on_hand=5.0,
        units_on_order=0.0,
        backorders=0.0,
        unit_cost=30.0,
        unit_price=60.0,
        lead_time_days=7.0,
        lead_time_std_days=1.0,
        holding_cost_annual_rate=0.20,
        fixed_order_cost=50.0,
        min_order_qty=10.0,
        target_service_level=0.95,
        forecast_daily_demand_mean=20.0,
        forecast_daily_demand_std=4.0,
    )


@pytest.fixture
def overstocked_sku() -> InventoryParameters:
    """Provide SKU parameters with massive excess stock."""
    return InventoryParameters(
        sku_id="SKU-1002",
        store_id="STORE-001",
        current_on_hand=500.0,
        units_on_order=0.0,
        backorders=0.0,
        unit_cost=30.0,
        unit_price=60.0,
        lead_time_days=7.0,
        lead_time_std_days=1.0,
        holding_cost_annual_rate=0.20,
        fixed_order_cost=50.0,
        min_order_qty=10.0,
        target_service_level=0.95,
        forecast_daily_demand_mean=5.0,  # 500 / 5 = 100 days of supply
        forecast_daily_demand_std=1.0,
    )


@pytest.mark.inventory
def test_optimizer_stockout_detection(stockout_risk_sku: InventoryParameters) -> None:
    """Verify depleted SKU triggers urgent order / expedite action."""
    optimizer = InventoryOptimizer()
    res = optimizer.optimize_sku(stockout_risk_sku)

    assert res.reorder_triggered is True
    assert res.recommended_action in [OrderAction.ORDER, OrderAction.EXPEDITE]
    assert res.health_status in [InventoryHealthStatus.UNDERSTOCKED, InventoryHealthStatus.STOCKOUT_IMMINENT]
    assert res.recommended_order_quantity > 0
    assert res.stockout_risk_prob > 0.50


@pytest.mark.inventory
def test_optimizer_overstock_detection(overstocked_sku: InventoryParameters) -> None:
    """Verify massive excess stock triggers REDUCE action."""
    optimizer = InventoryOptimizer()
    res = optimizer.optimize_sku(overstocked_sku)

    assert res.reorder_triggered is False
    assert res.recommended_action == OrderAction.REDUCE
    assert res.health_status in [InventoryHealthStatus.OVERSTOCKED, InventoryHealthStatus.CRITICAL_EXCESS]
    assert res.recommended_order_quantity == 0.0
    assert res.days_of_supply >= 45.0
