"""Mathematical risk scoring engine and financial exposure quantification."""

import math
from scipy.stats import norm

from foresight.config.constants import RiskLevel
from foresight.inventory.schema import InventoryOptimizationResult, InventoryParameters
from foresight.risk.schema import RiskAssessment


def standard_normal_loss_function(z: float) -> float:
    """Compute the standard normal unit loss function L(z) = phi(z) - z * (1 - Phi(z))."""
    phi_z = norm.pdf(z)
    one_minus_phi_z = 1.0 - norm.cdf(z)
    loss = phi_z - (z * one_minus_phi_z)
    return float(max(0.0, loss))


def calculate_expected_lost_sales(
    net_stock: float,
    lead_time_demand: float,
    std_lead_time_demand: float,
) -> float:
    """Compute expected unmet customer demand during lead time using the unit loss integral.

    Formula: E[Lost Sales] = sigma_LTD * L( (Net Stock - LTD) / sigma_LTD )
    """
    if std_lead_time_demand <= 0:
        return float(max(0.0, lead_time_demand - net_stock))

    z = (net_stock - lead_time_demand) / std_lead_time_demand
    expected_lost = std_lead_time_demand * standard_normal_loss_function(z)
    return round(float(max(0.0, expected_lost)), 2)


def calculate_excess_inventory_units(
    net_stock: float,
    lead_time_demand: float,
    safety_stock: float,
) -> float:
    """Compute excess/dead inventory units exceeding optimal target replenishment buffer.

    Formula: Excess = max(0, Net Stock - (LTD + 2 * SS))
    """
    target_max_buffer = lead_time_demand + (2.0 * safety_stock)
    excess = max(0.0, net_stock - target_max_buffer)
    return round(float(excess), 2)


def calculate_composite_risk_score(
    stockout_prob: float,
    days_of_supply: float,
    excess_units: float,
    safety_stock: float,
) -> tuple[float, float, float]:
    """Compute normalized 0-100 risk indices for stockout, overstock, and composite exposure.

    Returns:
        Tuple of (stockout_score, overstock_score, composite_score).
    """
    # 1. Stockout risk score (0 to 100)
    stockout_score = stockout_prob * 100.0
    if days_of_supply < 2.0 and stockout_prob > 0.30:
        stockout_score = min(100.0, stockout_score * 1.25)

    # 2. Overstock risk score (0 to 100)
    denom = max(1.0, safety_stock)
    excess_ratio = excess_units / denom
    overstock_score = min(100.0, (excess_ratio * 30.0) + (max(0.0, days_of_supply - 30.0) * 1.5))

    # 3. Composite score (dominant risk)
    composite = max(stockout_score, overstock_score)

    return round(stockout_score, 1), round(overstock_score, 1), round(composite, 1)


def classify_risk_severity(composite_score: float) -> RiskLevel:
    """Classify 0-100 risk score into standard enterprise severity tiers."""
    if composite_score >= 75.0:
        return RiskLevel.CRITICAL
    elif composite_score >= 50.0:
        return RiskLevel.HIGH
    elif composite_score >= 25.0:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def assess_sku_risk(
    opt_result: InventoryOptimizationResult,
    params: InventoryParameters,
) -> RiskAssessment:
    """Perform comprehensive financial risk assessment on an individual SKU-Store node."""
    # 1. Lead time demand volatility
    var_ltd = (params.lead_time_days * (params.forecast_daily_demand_std ** 2)) + (
        (params.forecast_daily_demand_mean ** 2) * (params.lead_time_std_days ** 2)
    )
    std_ltd = math.sqrt(max(0.01, var_ltd))

    # 2. Expected Lost Sales
    expected_lost = calculate_expected_lost_sales(
        net_stock=opt_result.net_stock,
        lead_time_demand=opt_result.lead_time_demand,
        std_lead_time_demand=std_ltd,
    )

    # 3. Overstock / Excess Units
    excess_units = calculate_excess_inventory_units(
        net_stock=opt_result.net_stock,
        lead_time_demand=opt_result.lead_time_demand,
        safety_stock=opt_result.safety_stock,
    )

    # 4. Financial Exposures
    margin_per_unit = max(0.0, params.unit_price - params.unit_cost)
    lost_revenue = expected_lost * params.unit_price
    lost_margin = expected_lost * margin_per_unit
    excess_holding_risk = excess_units * params.unit_cost * params.holding_cost_annual_rate
    total_exposure = lost_margin + excess_holding_risk

    # 5. Overstock Probability
    overstock_prob = float(min(1.0, max(0.0, (opt_result.days_of_supply - 20.0) / 40.0))) if opt_result.days_of_supply > 20.0 else 0.0

    # 6. Risk Scores & Classification
    stockout_score, overstock_score, composite_score = calculate_composite_risk_score(
        stockout_prob=opt_result.stockout_risk_prob,
        days_of_supply=opt_result.days_of_supply,
        excess_units=excess_units,
        safety_stock=opt_result.safety_stock,
    )
    severity = classify_risk_severity(composite_score)

    return RiskAssessment(
        sku_id=params.sku_id,
        store_id=params.store_id,
        risk_level=severity,
        composite_risk_score=composite_score,
        stockout_risk_score=stockout_score,
        overstock_risk_score=overstock_score,
        stockout_probability=opt_result.stockout_risk_prob,
        overstock_probability=round(overstock_prob, 4),
        expected_lost_sales_units=expected_lost,
        lost_revenue_risk=round(lost_revenue, 2),
        lost_margin_risk=round(lost_margin, 2),
        excess_stock_units=excess_units,
        excess_holding_cost_risk=round(excess_holding_risk, 2),
        total_financial_exposure=round(total_exposure, 2),
    )
