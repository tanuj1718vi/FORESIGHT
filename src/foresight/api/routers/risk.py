"""Risk assessment, prescriptive recommendations, and What-If simulation endpoints."""

from fastapi import APIRouter

from foresight.api.routers.inventory import _request_to_params
from foresight.api.schemas.risk import (
    PrescriptiveRequest,
    PrescriptiveResponse,
    RiskAssessRequest,
    RiskAssessResponse,
    ScenarioSimulateRequest,
    ScenarioSimulateResponse,
)
from foresight.inventory.optimizer import InventoryOptimizer
from foresight.risk.prescriptive import PrescriptiveEngine
from foresight.risk.scorer import assess_sku_risk
from foresight.risk.simulator import WhatIfSimulator

router = APIRouter(prefix="/api/v1/risk", tags=["Risk & Prescriptive Engine"])

_optimizer = InventoryOptimizer()
_prescriptive_engine = PrescriptiveEngine()
_simulator = WhatIfSimulator(_optimizer)


@router.post("/assess", response_model=RiskAssessResponse)
def assess_risk(req: RiskAssessRequest) -> RiskAssessResponse:
    """Perform financial risk quantification and stockout/overstock scoring."""
    params = _request_to_params(req)
    opt_res = _optimizer.optimize_sku(params, method=req.method)
    risk_res = assess_sku_risk(opt_res, params)

    return RiskAssessResponse(
        sku_id=risk_res.sku_id,
        store_id=risk_res.store_id,
        risk_level=risk_res.risk_level,
        composite_risk_score=risk_res.composite_risk_score,
        stockout_probability=risk_res.stockout_probability,
        lost_revenue_risk=risk_res.lost_revenue_risk,
        lost_margin_risk=risk_res.lost_margin_risk,
        excess_holding_cost_risk=risk_res.excess_holding_cost_risk,
        total_financial_exposure=risk_res.total_financial_exposure,
    )


@router.post("/prescribe", response_model=PrescriptiveResponse)
def generate_prescriptive_action(req: PrescriptiveRequest) -> PrescriptiveResponse:
    """Synthesize concrete prescriptive action work order with business justification."""
    params = _request_to_params(req)
    opt_res = _optimizer.optimize_sku(params, method=req.method)
    risk_res = assess_sku_risk(opt_res, params)
    rec = _prescriptive_engine.generate_recommendation(opt_res, risk_res, params)

    return PrescriptiveResponse(
        recommendation_id=rec.recommendation_id,
        sku_id=rec.sku_id,
        store_id=rec.store_id,
        action=rec.action,
        recommended_quantity=rec.recommended_quantity,
        urgency=rec.urgency,
        justification=rec.justification,
        expected_financial_impact=rec.expected_financial_impact,
        confidence_score=rec.confidence_score,
    )


@router.post("/simulate", response_model=ScenarioSimulateResponse)
def simulate_disruption_scenario(req: ScenarioSimulateRequest) -> ScenarioSimulateResponse:
    """Simulate operational and financial impact of supply chain disruption scenarios."""
    params = _request_to_params(req.inventory_params)
    sim_result = _simulator.simulate_sku(params, req.scenario)
    return ScenarioSimulateResponse(result=sim_result)
