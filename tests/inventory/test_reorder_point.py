"""Unit tests for Reorder Point (ROP) and net stock triggers."""

import pytest

from foresight.inventory.reorder_point import (
    calculate_lead_time_demand,
    calculate_reorder_point,
    evaluate_net_stock,
    is_reorder_triggered,
)


@pytest.mark.inventory
def test_lead_time_demand_and_rop() -> None:
    """Verify LTD = d * L and ROP = LTD + SS."""
    ltd = calculate_lead_time_demand(mean_daily_demand=15.0, lead_time_days=7.0)
    assert ltd == 105.0

    rop = calculate_reorder_point(lead_time_demand=ltd, safety_stock=25.0)
    assert rop == 130.0


@pytest.mark.inventory
def test_net_stock_and_reorder_trigger() -> None:
    """Verify net inventory position and threshold trigger."""
    # On Hand = 80, On Order = 40, Backorders = 10 -> Net = 110
    net = evaluate_net_stock(on_hand=80.0, on_order=40.0, backorders=10.0)
    assert net == 110.0

    # ROP = 120 -> Net (110) <= ROP (120) -> TRIGGERED
    assert is_reorder_triggered(net_stock=net, reorder_point=120.0) is True

    # ROP = 100 -> Net (110) > ROP (100) -> NOT TRIGGERED
    assert is_reorder_triggered(net_stock=net, reorder_point=100.0) is False
