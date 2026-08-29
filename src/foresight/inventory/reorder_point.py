"""Reorder Point (ROP) and continuous review inventory trigger logic."""

import numpy as np


def calculate_lead_time_demand(mean_daily_demand: float, lead_time_days: float) -> float:
    """Compute expected total demand consumed during replenishment lead time."""
    ltd = max(0.0, mean_daily_demand) * max(0.0, lead_time_days)
    return round(float(ltd), 2)


def calculate_reorder_point(lead_time_demand: float, safety_stock: float) -> float:
    """Compute Reorder Point (ROP) threshold.

    Formula: ROP = Lead Time Demand + Safety Stock
    """
    rop = max(0.0, lead_time_demand) + max(0.0, safety_stock)
    return round(float(rop), 2)


def evaluate_net_stock(
    on_hand: float,
    on_order: float = 0.0,
    backorders: float = 0.0,
) -> float:
    """Compute current Net Inventory Position.

    Formula: Net Stock = On Hand + On Order - Backorders
    """
    net = float(on_hand + on_order - backorders)
    return round(net, 2)


def is_reorder_triggered(net_stock: float, reorder_point: float) -> bool:
    """Determine if continuous review policy triggers an immediate replenishment order.

    Rule: Trigger if Net Stock <= ROP
    """
    return bool(net_stock <= reorder_point)
