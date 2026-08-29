"""Pydantic schemas and data contracts for the Risk Engine and Prescriptive Recommendations."""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from foresight.config.constants import RecommendationAction, RecommendationUrgency, RiskLevel
from foresight.inventory.schema import InventoryHealthStatus, InventoryOptimizationResult, InventoryParameters


class RiskAssessment(BaseModel):
    """Quantified risk assessment and financial exposure for a SKU-Store replenishment node."""
    sku_id: str
    store_id: str
    risk_level: RiskLevel
    composite_risk_score: float = Field(..., ge=0.0, le=100.0, description="Normalized risk index from 0 (Safe) to 100 (Critical)")
    stockout_risk_score: float = Field(..., ge=0.0, le=100.0)
    overstock_risk_score: float = Field(..., ge=0.0, le=100.0)
    stockout_probability: float = Field(..., ge=0.0, le=1.0)
    overstock_probability: float = Field(..., ge=0.0, le=1.0)
    expected_lost_sales_units: float = Field(..., ge=0.0)
    lost_revenue_risk: float = Field(..., ge=0.0, description="Financial sales volume at risk of stockout ($)")
    lost_margin_risk: float = Field(..., ge=0.0, description="Financial gross profit at risk of stockout ($)")
    excess_stock_units: float = Field(..., ge=0.0)
    excess_holding_cost_risk: float = Field(..., ge=0.0, description="Annual capital penalty tied up in dead/excess stock ($/yr)")
    total_financial_exposure: float = Field(..., ge=0.0, description="Combined financial risk exposure ($)")


class PrescriptiveRecommendation(BaseModel):
    """Concrete operational replenishment or corrective action order."""
    recommendation_id: str
    sku_id: str
    store_id: str
    action: RecommendationAction
    recommended_quantity: float
    urgency: RecommendationUrgency
    justification: str
    expected_financial_impact: float
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    donor_store_id: str | None = Field(default=None, description="Source store ID if action is REBALANCE transfer")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ScenarioParameters(BaseModel):
    """Stress-test parameters for What-If scenario simulations."""
    scenario_name: str = "Custom Scenario"
    lead_time_multiplier: float = Field(default=1.0, gt=0, description="Multiplier on supplier lead time (e.g. 1.5 for +50%)")
    demand_multiplier: float = Field(default=1.0, gt=0, description="Multiplier on expected demand (e.g. 1.25 for +25%)")
    target_service_level: float | None = Field(default=None, gt=0.5, lt=1.0, description="Override target service level")
    holding_cost_rate_multiplier: float = Field(default=1.0, gt=0, description="Multiplier on holding cost annual rate")


class ScenarioSimulationResult(BaseModel):
    """Comparative simulation outcome comparing baseline policy vs stress scenario."""
    scenario_name: str
    sku_id: str
    store_id: str
    baseline_safety_stock: float
    simulated_safety_stock: float
    delta_safety_stock: float
    baseline_reorder_point: float
    simulated_reorder_point: float
    delta_reorder_point: float
    baseline_working_capital: float
    simulated_working_capital: float
    delta_working_capital: float
    baseline_stockout_risk: float
    simulated_stockout_risk: float
    delta_stockout_risk: float
    baseline_total_annual_cost: float
    simulated_total_annual_cost: float
    delta_total_annual_cost: float
