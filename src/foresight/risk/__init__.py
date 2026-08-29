"""Risk assessment, financial exposure scoring, prescriptive recommendations, and What-If simulator."""

from foresight.risk.prescriptive import PrescriptiveEngine
from foresight.risk.run_risk_audit import PortfolioRiskReport, run_portfolio_risk_audit
from foresight.risk.schema import (
    PrescriptiveRecommendation,
    RiskAssessment,
    ScenarioParameters,
    ScenarioSimulationResult,
)
from foresight.risk.scorer import (
    assess_sku_risk,
    calculate_composite_risk_score,
    calculate_excess_inventory_units,
    calculate_expected_lost_sales,
    classify_risk_severity,
    standard_normal_loss_function,
)
from foresight.risk.simulator import WhatIfSimulator

__all__ = [
    "RiskAssessment",
    "PrescriptiveRecommendation",
    "ScenarioParameters",
    "ScenarioSimulationResult",
    "PortfolioRiskReport",
    "standard_normal_loss_function",
    "calculate_expected_lost_sales",
    "calculate_excess_inventory_units",
    "calculate_composite_risk_score",
    "classify_risk_severity",
    "assess_sku_risk",
    "PrescriptiveEngine",
    "WhatIfSimulator",
    "run_portfolio_risk_audit",
]
