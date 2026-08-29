"""Unit tests for Risk Scorer and financial exposure calculations."""

import numpy as np
import pytest

from foresight.config.constants import RiskLevel
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.inventory.schema import InventoryParameters
from foresight.risk.scorer import (
    assess_sku_risk,
    calculate_composite_risk_score,
    calculate_excess_inventory_units,
    calculate_expected_lost_sales,
    classify_risk_severity,
    standard_normal_loss_function,
)


@pytest.mark.risk
def test_unit_loss_function_properties() -> None:
    """Verify standard normal loss function L(z) >= 0 and decreases monotonically with z."""
    l_neg2 = standard_normal_loss_function(-2.0)
    l_0 = standard_normal_loss_function(0.0)
    l_pos2 = standard_normal_loss_function(2.0)

    # At z=0, L(0) = 1/sqrt(2pi) approx 0.3989
    assert np.isclose(l_0, 0.3989, atol=1e-3)
    assert l_neg2 > l_0 > l_pos2 > 0.0


@pytest.mark.risk
def test_expected_lost_sales_and_excess_stock() -> None:
    """Verify expected lost sales and excess stock unit calculations."""
    # Net stock = 100, LTD = 100, std_LTD = 20 -> z = 0 -> lost = 20 * 0.3989 = 7.98
    lost = calculate_expected_lost_sales(net_stock=100.0, lead_time_demand=100.0, std_lead_time_demand=20.0)
    assert np.isclose(lost, 7.98, atol=0.1)

    # Net stock = 300, LTD = 100, SS = 50 -> Max Buffer = 200 -> Excess = 100
    excess = calculate_excess_inventory_units(net_stock=300.0, lead_time_demand=100.0, safety_stock=50.0)
    assert excess == 100.0


@pytest.mark.risk
def test_risk_severity_classification() -> None:
    """Verify risk severity tiers."""
    assert classify_risk_severity(85.0) == RiskLevel.CRITICAL
    assert classify_risk_severity(60.0) == RiskLevel.HIGH
    assert classify_risk_severity(40.0) == RiskLevel.MEDIUM
    assert classify_risk_severity(15.0) == RiskLevel.LOW


@pytest.mark.risk
def test_assess_sku_risk_end_to_end() -> None:
    """Verify full financial risk evaluation on critical SKU."""
    params = InventoryParameters(
        sku_id="SKU-1001",
        store_id="STORE-001",
        current_on_hand=5.0,
        units_on_order=0.0,
        backorders=0.0,
        unit_cost=25.0,
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
    optimizer = InventoryOptimizer()
    opt_res = optimizer.optimize_sku(params)
    risk = assess_sku_risk(opt_res, params)

    assert risk.stockout_probability > 0.50
    assert risk.lost_margin_risk > 0.0
    assert risk.total_financial_exposure > 0.0
    assert risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
