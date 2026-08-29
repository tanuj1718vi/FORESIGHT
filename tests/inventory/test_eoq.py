"""Unit tests for Wilson Economic Order Quantity (EOQ) and cost breakdowns."""

import numpy as np
import pytest

from foresight.inventory.eoq import calculate_eoq, calculate_inventory_cost_breakdown


@pytest.mark.inventory
def test_wilson_eoq_calculation() -> None:
    """Verify EOQ = sqrt( 2 * D * S / H )."""
    # D = 10,000, S = 50, Unit Cost = 25, Holding Rate = 0.20 -> H = 5.0
    # 2 * 10,000 * 50 / 5.0 = 1,000,000 / 5 = 200,000 -> sqrt = 447.21
    eoq = calculate_eoq(
        annual_demand=10000.0,
        fixed_order_cost=50.0,
        unit_cost=25.0,
        holding_cost_annual_rate=0.20,
        min_order_qty=1.0,
    )
    assert np.isclose(eoq, 447.21, atol=0.05)


@pytest.mark.inventory
def test_eoq_moq_constraint() -> None:
    """Verify MOQ floor is respected if EOQ is below MOQ."""
    eoq = calculate_eoq(
        annual_demand=100.0,
        fixed_order_cost=10.0,
        unit_cost=50.0,
        holding_cost_annual_rate=0.20,
        min_order_qty=50.0,
    )
    assert eoq == 50.0


@pytest.mark.inventory
def test_inventory_cost_breakdown() -> None:
    """Verify ordering and holding costs are symmetric at optimal unconstrained EOQ."""
    # At exact unconstrained EOQ with 0 safety stock, ordering cost equals holding cost
    costs = calculate_inventory_cost_breakdown(
        annual_demand=10000.0,
        order_quantity=447.21,
        fixed_order_cost=50.0,
        unit_cost=25.0,
        holding_cost_annual_rate=0.20,
        safety_stock=0.0,
    )
    assert np.isclose(costs["annual_ordering_cost"], costs["annual_holding_cost"], atol=1.0)
    assert costs["total_annual_cost"] > 0.0
