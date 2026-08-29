"""Wilson Economic Order Quantity (EOQ) and inventory cost curve optimization."""

import math


def calculate_eoq(
    annual_demand: float,
    fixed_order_cost: float = 50.0,
    unit_cost: float = 20.0,
    holding_cost_annual_rate: float = 0.20,
    min_order_qty: float = 1.0,
) -> float:
    """Compute optimal Economic Order Quantity (EOQ) minimizing total setup and holding costs.

    Formula: EOQ = sqrt( (2 * D * S) / H )
    where:
    - D = Annual Demand Units
    - S = Fixed cost per purchase order
    - H = Annual unit holding cost = unit_cost * holding_cost_annual_rate
    """
    if annual_demand <= 0 or unit_cost <= 0 or holding_cost_annual_rate <= 0:
        return float(max(1.0, min_order_qty))

    h = unit_cost * holding_cost_annual_rate
    eoq_unconstrained = math.sqrt((2.0 * annual_demand * fixed_order_cost) / h)
    eoq_final = max(eoq_unconstrained, min_order_qty)
    return round(float(eoq_final), 2)


def calculate_inventory_cost_breakdown(
    annual_demand: float,
    order_quantity: float,
    fixed_order_cost: float = 50.0,
    unit_cost: float = 20.0,
    holding_cost_annual_rate: float = 0.20,
    safety_stock: float = 0.0,
) -> dict[str, float]:
    """Compute annual holding, ordering, and total inventory management costs."""
    if order_quantity <= 0 or annual_demand <= 0:
        return {
            "annual_ordering_cost": 0.0,
            "annual_holding_cost": 0.0,
            "total_annual_cost": 0.0,
        }

    h = unit_cost * holding_cost_annual_rate

    # Annual ordering cost: (D / Q) * S
    orders_per_year = annual_demand / order_quantity
    annual_ordering = orders_per_year * fixed_order_cost

    # Annual holding cost: (Q / 2 + SS) * H
    avg_cycle_stock = order_quantity / 2.0
    annual_holding = (avg_cycle_stock + safety_stock) * h

    total_cost = annual_ordering + annual_holding

    return {
        "annual_ordering_cost": round(float(annual_ordering), 2),
        "annual_holding_cost": round(float(annual_holding), 2),
        "total_annual_cost": round(float(total_cost), 2),
    }
