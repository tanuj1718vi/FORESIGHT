"""Master Inventory Optimization Engine coordinating safety stock, ROP, EOQ, and prescriptive action."""

import math
from typing import Any
import numpy as np

from foresight.inventory.eoq import calculate_eoq, calculate_inventory_cost_breakdown
from foresight.inventory.reorder_point import (
    calculate_lead_time_demand,
    calculate_reorder_point,
    evaluate_net_stock,
    is_reorder_triggered,
)
from foresight.inventory.safety_stock import calculate_safety_stock, calculate_z_score
from foresight.inventory.schema import (
    InventoryHealthStatus,
    InventoryOptimizationResult,
    InventoryParameters,
    OrderAction,
    SafetyStockMethod,
)
from foresight.inventory.turnover import (
    calculate_days_of_supply,
    calculate_working_capital_committed,
    estimate_stockout_probability,
)


class InventoryOptimizer:
    """Enterprise inventory policy optimization engine."""

    def __init__(self, default_method: SafetyStockMethod = SafetyStockMethod.COMBINED_UNCERTAINTY) -> None:
        self.default_method = default_method

    def optimize_sku(
        self,
        params: InventoryParameters,
        method: SafetyStockMethod | None = None,
    ) -> InventoryOptimizationResult:
        """Compute optimal inventory policies and operational actions for an individual SKU."""
        chosen_method = method or self.default_method

        # 1. Safety Stock
        ss = calculate_safety_stock(
            method=chosen_method,
            mean_demand=params.forecast_daily_demand_mean,
            std_demand=params.forecast_daily_demand_std,
            mean_lead_time=params.lead_time_days,
            std_lead_time=params.lead_time_std_days,
            service_level=params.target_service_level,
            forecast_p50_daily=params.forecast_daily_demand_mean,
            forecast_p95_daily=params.forecast_daily_demand_p95,
        )

        # 2. Lead Time Demand & Reorder Point
        ltd = calculate_lead_time_demand(
            mean_daily_demand=params.forecast_daily_demand_mean,
            lead_time_days=params.lead_time_days,
        )
        rop = calculate_reorder_point(lead_time_demand=ltd, safety_stock=ss)

        # 3. Net Stock & Reorder Trigger
        net_stock = evaluate_net_stock(
            on_hand=params.current_on_hand,
            on_order=params.units_on_order,
            backorders=params.backorders,
        )
        triggered = is_reorder_triggered(net_stock=net_stock, reorder_point=rop)

        # 4. Economic Order Quantity (EOQ)
        annual_demand = params.forecast_daily_demand_mean * 365.0
        eoq = calculate_eoq(
            annual_demand=annual_demand,
            fixed_order_cost=params.fixed_order_cost,
            unit_cost=params.unit_cost,
            holding_cost_annual_rate=params.holding_cost_annual_rate,
            min_order_qty=params.min_order_qty,
        )

        # 5. Order Recommendation Quantity
        if triggered:
            # Order to bring net position up to ROP + EOQ (order-up-to level) clamped at MOQ
            deficit = max(0.0, rop - net_stock)
            rec_order_qty = max(params.min_order_qty, round(deficit + eoq, 0))
        else:
            rec_order_qty = 0.0

        # 6. Days of Supply & Working Capital
        dos = calculate_days_of_supply(
            on_hand_stock=params.current_on_hand,
            daily_demand_rate=params.forecast_daily_demand_mean,
        )
        working_capital = calculate_working_capital_committed(
            safety_stock=ss,
            order_quantity=eoq,
            unit_cost=params.unit_cost,
        )

        # 7. Stockout Probability Estimation
        # Variance of LTD = L * sigma_d^2 + d^2 * sigma_L^2
        var_ltd = (params.lead_time_days * (params.forecast_daily_demand_std ** 2)) + (
            (params.forecast_daily_demand_mean ** 2) * (params.lead_time_std_days ** 2)
        )
        std_ltd = math.sqrt(max(0.01, var_ltd))
        stockout_prob = estimate_stockout_probability(
            net_stock=net_stock,
            lead_time_demand=ltd,
            std_lead_time_demand=std_ltd,
        )

        # 8. Health Status & Prescriptive Action
        if net_stock <= 0 or (dos < 2.0 and params.forecast_daily_demand_mean > 0):
            health = InventoryHealthStatus.STOCKOUT_IMMINENT
            action = OrderAction.EXPEDITE
        elif net_stock <= rop:
            health = InventoryHealthStatus.UNDERSTOCKED
            action = OrderAction.ORDER
        elif dos > 45.0:
            health = InventoryHealthStatus.CRITICAL_EXCESS
            action = OrderAction.REDUCE
        elif dos > 30.0:
            health = InventoryHealthStatus.OVERSTOCKED
            action = OrderAction.REDUCE
        else:
            health = InventoryHealthStatus.OPTIMAL
            action = OrderAction.HOLD

        # 9. Cost Breakdown
        cost_breakdown = calculate_inventory_cost_breakdown(
            annual_demand=annual_demand,
            order_quantity=eoq,
            fixed_order_cost=params.fixed_order_cost,
            unit_cost=params.unit_cost,
            holding_cost_annual_rate=params.holding_cost_annual_rate,
            safety_stock=ss,
        )

        z = calculate_z_score(params.target_service_level)

        return InventoryOptimizationResult(
            sku_id=params.sku_id,
            store_id=params.store_id,
            service_level=params.target_service_level,
            z_score=round(z, 4),
            safety_stock=ss,
            lead_time_demand=ltd,
            reorder_point=rop,
            net_stock=net_stock,
            days_of_supply=dos,
            economic_order_quantity=eoq,
            recommended_order_quantity=rec_order_qty,
            reorder_triggered=triggered,
            recommended_action=action,
            health_status=health,
            stockout_risk_prob=stockout_prob,
            working_capital_committed=working_capital,
            annual_holding_cost=cost_breakdown["annual_holding_cost"],
            annual_ordering_cost=cost_breakdown["annual_ordering_cost"],
            total_annual_inventory_cost=cost_breakdown["total_annual_cost"],
        )
