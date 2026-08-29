"""Safety stock calculation algorithms and uncertainty modeling for Project FORESIGHT."""

import math
from scipy.stats import norm

from foresight.inventory.schema import SafetyStockMethod
from foresight.utils.exceptions import InventoryOptimizationError


def calculate_z_score(service_level: float) -> float:
    """Compute normal distribution critical value Z_alpha = Phi^-1(service_level)."""
    if not (0.50 < service_level < 1.0):
        raise InventoryOptimizationError(f"Service level must be in (0.50, 1.00), got {service_level}")
    return float(norm.ppf(service_level))


def calculate_safety_stock_demand_uncertainty(
    mean_lead_time: float = 7.0,
    std_demand: float = 2.0,
    service_level: float = 0.95,
    **kwargs: float,
) -> float:
    """Compute safety stock considering demand volatility during constant lead time.

    Formula: SS = Z_alpha * sigma_d * sqrt(L)
    """
    # Support positional or keyword variation
    lead_time = kwargs.get("lead_time", mean_lead_time)
    sigma_d = kwargs.get("std_d", std_demand)
    z = calculate_z_score(service_level)
    ss = z * sigma_d * math.sqrt(max(1.0, lead_time))
    return round(float(max(0.0, ss)), 2)


def calculate_safety_stock_lead_time_uncertainty(
    mean_demand: float = 10.0,
    std_lead_time: float = 1.0,
    service_level: float = 0.95,
    **kwargs: float,
) -> float:
    """Compute safety stock considering lead time variability under steady demand.

    Formula: SS = Z_alpha * mean_d * sigma_L
    """
    mean_d = kwargs.get("mean_d", mean_demand)
    sigma_l = kwargs.get("lead_time_std", std_lead_time)
    z = calculate_z_score(service_level)
    ss = z * mean_d * max(0.0, sigma_l)
    return round(float(max(0.0, ss)), 2)


def calculate_safety_stock_combined(
    mean_demand: float = 10.0,
    std_demand: float = 2.0,
    mean_lead_time: float = 7.0,
    std_lead_time: float = 1.0,
    service_level: float = 0.95,
) -> float:
    """Compute safety stock considering BOTH demand volatility and supplier lead time variability.

    Formula: SS = Z_alpha * sqrt( L * sigma_d^2 + mean_d^2 * sigma_L^2 )
    This is the standard enterprise supply chain standard.
    """
    z = calculate_z_score(service_level)
    variance_term = (mean_lead_time * (std_demand ** 2)) + ((mean_demand ** 2) * (std_lead_time ** 2))
    ss = z * math.sqrt(max(0.0, variance_term))
    return round(float(max(0.0, ss)), 2)


def calculate_safety_stock_quantile(
    forecast_p50_daily: float | None = None,
    forecast_p95_daily: float | None = None,
    lead_time_days: float = 7.0,
    p50_demand: float | None = None,
    p95_demand: float | None = None,
) -> float:
    """Compute non-parametric safety stock directly from machine learning quantile forecast.

    Formula: SS_ML = (P95_daily - P50_daily) * sqrt(L)
    """
    p50 = forecast_p50_daily if forecast_p50_daily is not None else (p50_demand if p50_demand is not None else 10.0)
    p95 = forecast_p95_daily if forecast_p95_daily is not None else (p95_demand if p95_demand is not None else 15.0)
    spread = max(0.0, p95 - p50)
    ss = spread * math.sqrt(max(1.0, lead_time_days))
    return round(float(ss), 2)


def calculate_safety_stock(
    method: SafetyStockMethod = SafetyStockMethod.COMBINED_UNCERTAINTY,
    mean_demand: float = 10.0,
    std_demand: float = 2.0,
    mean_lead_time: float = 7.0,
    std_lead_time: float = 1.0,
    service_level: float = 0.95,
    forecast_p50_daily: float | None = None,
    forecast_p95_daily: float | None = None,
) -> float:
    """Dispatch safety stock calculation based on the specified industrial method."""
    if method == SafetyStockMethod.COMBINED_UNCERTAINTY:
        return calculate_safety_stock_combined(
            mean_demand=mean_demand,
            std_demand=std_demand,
            mean_lead_time=mean_lead_time,
            std_lead_time=std_lead_time,
            service_level=service_level,
        )
    elif method == SafetyStockMethod.DEMAND_ONLY:
        return calculate_safety_stock_demand_uncertainty(
            mean_lead_time=mean_lead_time,
            std_demand=std_demand,
            service_level=service_level,
        )
    elif method == SafetyStockMethod.LEAD_TIME_ONLY:
        return calculate_safety_stock_lead_time_uncertainty(
            mean_demand=mean_demand,
            std_lead_time=std_lead_time,
            service_level=service_level,
        )
    elif method == SafetyStockMethod.QUANTILE_ML:
        p50 = forecast_p50_daily if forecast_p50_daily is not None else mean_demand
        p95 = forecast_p95_daily if forecast_p95_daily is not None else (mean_demand + 1.645 * std_demand)
        return calculate_safety_stock_quantile(
            forecast_p50_daily=p50,
            forecast_p95_daily=p95,
            lead_time_days=mean_lead_time,
        )
    else:
        raise InventoryOptimizationError(f"Unknown safety stock method: '{method}'")


# Aliases for flexible integration
calculate_combined_uncertainty_safety_stock = calculate_safety_stock_combined
calculate_demand_uncertainty_safety_stock = calculate_safety_stock_demand_uncertainty
calculate_lead_time_uncertainty_safety_stock = calculate_safety_stock_lead_time_uncertainty
calculate_ml_quantile_safety_stock = calculate_safety_stock_quantile
