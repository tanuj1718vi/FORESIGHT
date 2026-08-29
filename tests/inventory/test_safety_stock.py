"""Unit tests for safety stock mathematical formulas."""

import numpy as np
import pytest

from foresight.inventory.safety_stock import (
    calculate_safety_stock,
    calculate_safety_stock_combined,
    calculate_safety_stock_demand_uncertainty,
    calculate_safety_stock_lead_time_uncertainty,
    calculate_safety_stock_quantile,
    calculate_z_score,
)
from foresight.inventory.schema import SafetyStockMethod
from foresight.utils.exceptions import InventoryOptimizationError


@pytest.mark.inventory
def test_z_score_calculation() -> None:
    """Verify normal critical values for standard service levels."""
    assert np.isclose(calculate_z_score(0.5001), 0.0, atol=0.01)
    assert np.isclose(calculate_z_score(0.8413), 1.0, atol=0.01)
    assert np.isclose(calculate_z_score(0.95), 1.6449, atol=1e-3)
    assert np.isclose(calculate_z_score(0.9772), 2.0, atol=0.01)
    assert np.isclose(calculate_z_score(0.99), 2.3263, atol=1e-3)

    with pytest.raises(InventoryOptimizationError):
        calculate_z_score(0.40)  # Below 0.50 invalid

    with pytest.raises(InventoryOptimizationError):
        calculate_z_score(1.0)   # >= 1.0 invalid


@pytest.mark.inventory
def test_safety_stock_demand_uncertainty() -> None:
    """Verify SS = Z * sigma_d * sqrt(L)."""
    # L = 9 (sqrt = 3), sigma_d = 4, service_level = 0.95 (Z = 1.6449)
    # SS = 1.6449 * 4 * 3 = 19.7388 -> 19.74
    ss = calculate_safety_stock_demand_uncertainty(mean_lead_time=9.0, std_demand=4.0, service_level=0.95)
    assert np.isclose(ss, 19.74, atol=0.05)


@pytest.mark.inventory
def test_safety_stock_lead_time_uncertainty() -> None:
    """Verify SS = Z * mean_d * sigma_L."""
    # mean_d = 20, sigma_L = 2, Z = 1.6449 -> SS = 1.6449 * 20 * 2 = 65.80
    ss = calculate_safety_stock_lead_time_uncertainty(mean_demand=20.0, std_lead_time=2.0, service_level=0.95)
    assert np.isclose(ss, 65.80, atol=0.05)


@pytest.mark.inventory
def test_safety_stock_combined_uncertainty() -> None:
    """Verify SS = Z * sqrt( L * sigma_d^2 + mean_d^2 * sigma_L^2 )."""
    # L = 4, sigma_d = 3 -> L * sigma_d^2 = 36
    # mean_d = 8, sigma_L = 1 -> mean_d^2 * sigma_L^2 = 64
    # variance = 100, sqrt = 10 -> SS = 1.6449 * 10 = 16.45
    ss = calculate_safety_stock_combined(
        mean_demand=8.0,
        std_demand=3.0,
        mean_lead_time=4.0,
        std_lead_time=1.0,
        service_level=0.95,
    )
    assert np.isclose(ss, 16.45, atol=0.05)


@pytest.mark.inventory
def test_safety_stock_dispatch_enum() -> None:
    """Verify calculate_safety_stock dispatcher operates across all enum methods."""
    ss_comb = calculate_safety_stock(
        method=SafetyStockMethod.COMBINED_UNCERTAINTY,
        mean_demand=8.0,
        std_demand=3.0,
        mean_lead_time=4.0,
        std_lead_time=1.0,
        service_level=0.95,
    )
    assert ss_comb > 0.0

    ss_quant = calculate_safety_stock(
        method=SafetyStockMethod.QUANTILE_ML,
        forecast_p50_daily=10.0,
        forecast_p95_daily=15.0,
        mean_lead_time=4.0,
    )
    assert np.isclose(ss_quant, 10.0)  # (15 - 10) * sqrt(4) = 10.0
