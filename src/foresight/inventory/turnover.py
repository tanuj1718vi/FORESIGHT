"""Days of supply, inventory turnover ratio, working capital, and stockout probability metrics."""

import math
from scipy.stats import norm


def calculate_days_of_supply(on_hand_stock: float, daily_demand_rate: float) -> float:
    """Compute Days of Supply (DOS) coverage at current daily sales rate."""
    if daily_demand_rate <= 0:
        return 365.0 if on_hand_stock > 0 else 0.0
    dos = max(0.0, on_hand_stock) / daily_demand_rate
    return round(float(min(365.0, dos)), 1)


def calculate_inventory_turnover(annual_cogs: float, average_inventory_value: float) -> float:
    """Compute Inventory Turnover Ratio (ITR = Annual COGS / Average Working Capital in Stock)."""
    if average_inventory_value <= 0:
        return 0.0
    return round(float(annual_cogs / average_inventory_value), 2)


def calculate_working_capital_committed(
    safety_stock: float,
    order_quantity: float,
    unit_cost: float,
) -> float:
    """Compute average financial working capital tied up in cycle and safety inventory."""
    average_units = max(0.0, safety_stock) + (max(0.0, order_quantity) / 2.0)
    capital = average_units * max(0.0, unit_cost)
    return round(float(capital), 2)


def estimate_stockout_probability(
    net_stock: float,
    lead_time_demand: float,
    std_lead_time_demand: float,
) -> float:
    """Estimate probability of experiencing a stockout before next replenishment arrives.

    Formula: P(Stockout) = 1 - Phi( (Net Stock - Lead Time Demand) / sigma_LTD )
    """
    if std_lead_time_demand <= 0:
        return 1.0 if net_stock < lead_time_demand else 0.0
    z_stat = (net_stock - lead_time_demand) / std_lead_time_demand
    prob_stockout = float(1.0 - norm.cdf(z_stat))
    return round(float(max(0.0, min(1.0, prob_stockout))), 4)
