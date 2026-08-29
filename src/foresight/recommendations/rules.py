"""Business rules for prescriptive supply chain decisions."""

from foresight.config.constants import RecommendationAction, RecommendationUrgency
from foresight.inventory.schema import InventoryHealthStatus, InventoryOptimizationResult, InventoryParameters
from foresight.risk.schema import RiskAssessment


def evaluate_action_rule(
    opt_result: InventoryOptimizationResult,
    risk: RiskAssessment,
    params: InventoryParameters,
) -> tuple[RecommendationAction, RecommendationUrgency, float]:
    """Evaluate core inventory position rules to determine action, urgency, and order quantity."""
    if opt_result.health_status == InventoryHealthStatus.STOCKOUT_IMMINENT:
        action = RecommendationAction.EXPEDITE
        urgency = RecommendationUrgency.CRITICAL
        qty = max(opt_result.recommended_order_quantity, opt_result.reorder_point - opt_result.net_stock)
        return action, urgency, qty

    elif opt_result.health_status == InventoryHealthStatus.UNDERSTOCKED:
        action = RecommendationAction.ORDER
        urgency = RecommendationUrgency.HIGH if risk.composite_risk_score >= 50.0 else RecommendationUrgency.MEDIUM
        qty = opt_result.recommended_order_quantity
        return action, urgency, qty

    elif opt_result.health_status in [InventoryHealthStatus.OVERSTOCKED, InventoryHealthStatus.CRITICAL_EXCESS]:
        action = RecommendationAction.REDUCE
        urgency = RecommendationUrgency.HIGH if opt_result.days_of_supply > 60.0 else RecommendationUrgency.MEDIUM
        qty = risk.excess_stock_units
        return action, urgency, qty

    else:
        # OPTIMAL
        if risk.stockout_probability > 0.20 or opt_result.days_of_supply < (params.lead_time_days * 1.5):
            return RecommendationAction.MONITOR, RecommendationUrgency.LOW, 0.0
        else:
            return RecommendationAction.HOLD, RecommendationUrgency.LOW, 0.0
