"""Risk scoring, prescriptive recommendations, and simulation API schemas."""

from pydantic import BaseModel, Field

from foresight.api.schemas.inventory import InventoryOptimizeRequest
from foresight.config.constants import RecommendationAction, RecommendationUrgency, RiskLevel
from foresight.risk.schema import RiskAssessment, ScenarioParameters, ScenarioSimulationResult


class RiskAssessRequest(InventoryOptimizeRequest):
    """Risk assessment request payload."""
    pass


class RiskAssessResponse(BaseModel):
    """Financial risk assessment and exposure payload."""
    sku_id: str
    store_id: str
    risk_level: RiskLevel
    composite_risk_score: float
    stockout_probability: float
    lost_revenue_risk: float
    lost_margin_risk: float
    excess_holding_cost_risk: float
    total_financial_exposure: float


class PrescriptiveRequest(InventoryOptimizeRequest):
    """Prescriptive recommendation request payload."""
    pass


class PrescriptiveResponse(BaseModel):
    """Prescriptive action work order payload."""
    recommendation_id: str
    sku_id: str
    store_id: str
    action: RecommendationAction
    recommended_quantity: float
    urgency: RecommendationUrgency
    justification: str
    expected_financial_impact: float
    confidence_score: float


class ScenarioSimulateRequest(BaseModel):
    """What-If scenario simulation request."""
    inventory_params: InventoryOptimizeRequest
    scenario: ScenarioParameters


class ScenarioSimulateResponse(BaseModel):
    """What-If scenario simulation response."""
    result: ScenarioSimulationResult
