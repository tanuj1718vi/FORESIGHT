"""Unit tests for What-If disruption scenario simulator."""

import pytest

from foresight.inventory.schema import InventoryParameters
from foresight.risk.schema import ScenarioParameters
from foresight.risk.simulator import WhatIfSimulator


@pytest.fixture
def baseline_sku_params() -> InventoryParameters:
    return InventoryParameters(
        sku_id="SKU-3001",
        store_id="STORE-001",
        current_on_hand=50.0,
        units_on_order=0.0,
        backorders=0.0,
        unit_cost=30.0,
        unit_price=70.0,
        lead_time_days=6.0,
        lead_time_std_days=1.0,
        holding_cost_annual_rate=0.20,
        fixed_order_cost=50.0,
        min_order_qty=10.0,
        target_service_level=0.95,
        forecast_daily_demand_mean=10.0,
        forecast_daily_demand_std=2.0,
    )


@pytest.mark.risk
def test_simulator_lead_time_surge(baseline_sku_params: InventoryParameters) -> None:
    """Verify +50% lead time increases safety stock, ROP, and working capital."""
    simulator = WhatIfSimulator()
    scenario = ScenarioParameters(
        scenario_name="Supplier Lead Time Disruption",
        lead_time_multiplier=1.50,
    )
    result = simulator.simulate_sku(baseline_sku_params, scenario)

    assert result.delta_safety_stock > 0
    assert result.delta_reorder_point > 0
    assert result.delta_working_capital > 0
    assert result.simulated_safety_stock > result.baseline_safety_stock
    assert result.simulated_reorder_point > result.baseline_reorder_point


@pytest.mark.risk
def test_simulator_service_level_increase(baseline_sku_params: InventoryParameters) -> None:
    """Verify raising service level from 95% to 99% elevates safety stock."""
    simulator = WhatIfSimulator()
    scenario = ScenarioParameters(
        scenario_name="Service Level Elevation",
        target_service_level=0.99,
    )
    result = simulator.simulate_sku(baseline_sku_params, scenario)

    assert result.delta_safety_stock > 0
    assert result.simulated_safety_stock > result.baseline_safety_stock
