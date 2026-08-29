"""Natural language justification generation for prescriptive recommendations."""

from foresight.config.constants import RecommendationAction
from foresight.inventory.schema import InventoryOptimizationResult, InventoryParameters
from foresight.risk.schema import RiskAssessment


def build_recommendation_justification(
    action: RecommendationAction,
    qty: float,
    opt_result: InventoryOptimizationResult,
    risk: RiskAssessment,
    params: InventoryParameters,
) -> str:
    """Synthesize human-readable justification for inventory controllers and supply chain executives."""
    if action == RecommendationAction.EXPEDITE:
        return (
            f"Imminent stockout detected: Net stock ({opt_result.net_stock:.0f} units) covers only "
            f"{opt_result.days_of_supply:.1f} days of supply against a {params.lead_time_days:.0f}-day lead time. "
            f"Stockout probability is {risk.stockout_probability * 100:.1f}%. "
            f"Expedite emergency PO for {qty:.0f} units to protect ${risk.lost_margin_risk:,.2f} in gross margin."
        )

    elif action == RecommendationAction.ORDER:
        return (
            f"Inventory breached Reorder Point ({opt_result.net_stock:.0f} <= {opt_result.reorder_point:.0f} units). "
            f"Place standard replenishment purchase order for {qty:.0f} units (EOQ = {opt_result.economic_order_quantity:.0f}) "
            f"to restore safety stock buffer ({opt_result.safety_stock:.0f} units)."
        )

    elif action == RecommendationAction.REDUCE:
        return (
            f"Excess inventory accumulation: Position covers {opt_result.days_of_supply:.1f} days of supply "
            f"({risk.excess_stock_units:.0f} units above target max buffer). "
            f"Pause inbound replenishment and consider promotional markdown to release "
            f"${risk.excess_holding_cost_risk:,.2f}/yr in holding capital."
        )

    elif action == RecommendationAction.MONITOR:
        return (
            f"Inventory position is optimal ({opt_result.days_of_supply:.1f}d supply), but stockout risk is "
            f"{risk.stockout_probability * 100:.1f}%. Maintain active monitoring on next demand cycle."
        )

    else:
        return (
            f"Stock position healthy ({opt_result.days_of_supply:.1f}d supply, {opt_result.net_stock:.0f} units). "
            f"Safety stock buffer ({opt_result.safety_stock:.0f} units) fully maintained. No action required."
        )
