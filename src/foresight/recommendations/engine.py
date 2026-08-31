"""Prescriptive recommendation engine and lateral multi-store rebalancing logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

from foresight.config.constants import RecommendationAction, RecommendationUrgency
from foresight.inventory.schema import InventoryHealthStatus, InventoryOptimizationResult, InventoryParameters
from foresight.recommendations.explanations import build_recommendation_justification
from foresight.recommendations.rules import evaluate_action_rule
from foresight.recommendations.schemas import PrescriptiveRecommendation
from foresight.recommendations.scoring import calculate_recommendation_confidence

if TYPE_CHECKING:
    from foresight.risk.schema import RiskAssessment



class PrescriptiveEngine:
    """Enterprise decision engine generating prioritized prescriptive action work orders."""

    def __init__(self, confidence_baseline: float = 0.90) -> None:
        self.confidence_baseline = confidence_baseline

    def generate_recommendation(
        self,
        opt_result: InventoryOptimizationResult,
        risk: RiskAssessment,
        params: InventoryParameters,
    ) -> PrescriptiveRecommendation:
        """Map risk profile and inventory position to an actionable operational recommendation."""
        rec_id = f"REC-{params.store_id}-{params.sku_id}"

        action, urgency, qty = evaluate_action_rule(opt_result, risk, params)

        if action in [RecommendationAction.EXPEDITE, RecommendationAction.ORDER]:
            financial_impact = risk.lost_margin_risk
        elif action == RecommendationAction.REDUCE:
            financial_impact = risk.excess_holding_cost_risk
        else:
            financial_impact = 0.0

        justification = build_recommendation_justification(
            action=action,
            qty=qty,
            opt_result=opt_result,
            risk=risk,
            params=params,
        )

        confidence = calculate_recommendation_confidence(params, self.confidence_baseline)

        return PrescriptiveRecommendation(
            recommendation_id=rec_id,
            sku_id=params.sku_id,
            store_id=params.store_id,
            action=action,
            recommended_quantity=round(float(qty), 0),
            urgency=urgency,
            justification=justification,
            expected_financial_impact=round(float(financial_impact), 2),
            confidence_score=round(confidence, 3),
        )

    def identify_lateral_rebalance_opportunities(
        self,
        recommendations: list[PrescriptiveRecommendation],
        inventory_results: list[InventoryOptimizationResult],
    ) -> list[PrescriptiveRecommendation]:
        """Scan portfolio for intra-network lateral stock transfer opportunities across store locations."""
        rebalanced_recs: list[PrescriptiveRecommendation] = []
        sku_groups: dict[str, list[tuple[PrescriptiveRecommendation, InventoryOptimizationResult]]] = {}

        for rec, opt in zip(recommendations, inventory_results, strict=False):
            sku_groups.setdefault(rec.sku_id, []).append((rec, opt))

        for sku_id, group in sku_groups.items():
            deficits = [(r, o) for r, o in group if r.action in [RecommendationAction.EXPEDITE, RecommendationAction.ORDER]]
            surpluses = [(r, o) for r, o in group if r.action == RecommendationAction.REDUCE and r.recommended_quantity > 0]

            if deficits and surpluses:
                for def_rec, def_opt in deficits:
                    for sur_rec, sur_opt in surpluses:
                        if sur_rec.recommended_quantity <= 0:
                            continue

                        transfer_qty = min(def_rec.recommended_quantity, sur_rec.recommended_quantity)
                        if transfer_qty >= 10.0:
                            rebalance_rec = PrescriptiveRecommendation(
                                recommendation_id=f"REBAL-{def_rec.store_id}-{sur_rec.store_id}-{sku_id}",
                                sku_id=sku_id,
                                store_id=def_rec.store_id,
                                action=RecommendationAction.REBALANCE,
                                recommended_quantity=round(transfer_qty, 0),
                                urgency=RecommendationUrgency.HIGH,
                                justification=(
                                    f"Lateral Rebalance Opportunity: Transfer {transfer_qty:.0f} units of {sku_id} "
                                    f"from overstocked {sur_rec.store_id} ({sur_opt.days_of_supply:.1f}d supply) "
                                    f"to depleted {def_rec.store_id} ({def_opt.days_of_supply:.1f}d supply). "
                                    f"Bypasses supplier lead time and saves working capital."
                                ),
                                expected_financial_impact=def_rec.expected_financial_impact,
                                confidence_score=0.92,
                                donor_store_id=sur_rec.store_id,
                            )
                            rebalanced_recs.append(rebalance_rec)
                            sur_rec.recommended_quantity -= transfer_qty
                            def_rec.recommended_quantity -= transfer_qty
                            break

        return rebalanced_recs
