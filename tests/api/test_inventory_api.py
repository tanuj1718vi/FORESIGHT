"""Integration tests for Inventory Optimization REST endpoints."""

from fastapi.testclient import TestClient
import pytest

from foresight.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.api
def test_optimize_single_endpoint(client: TestClient) -> None:
    """Verify POST /api/v1/inventory/optimize returns valid policy parameters."""
    payload = {
        "sku_id": "SKU-1001",
        "store_id": "STORE-001",
        "current_on_hand": 20.0,
        "units_on_order": 0.0,
        "backorders": 0.0,
        "unit_cost": 25.0,
        "unit_price": 60.0,
        "lead_time_days": 7.0,
        "lead_time_std_days": 1.0,
        "holding_cost_annual_rate": 0.20,
        "fixed_order_cost": 50.0,
        "min_order_qty": 10.0,
        "target_service_level": 0.95,
        "forecast_daily_demand_mean": 20.0,
        "forecast_daily_demand_std": 4.0,
    }
    resp = client.post("/api/v1/inventory/optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["safety_stock"] > 0.0
    assert data["reorder_point"] > 0.0
    assert data["economic_order_quantity"] > 0.0
    assert data["health_status"] in ["OPTIMAL", "UNDERSTOCKED", "STOCKOUT_IMMINENT", "OVERSTOCKED", "CRITICAL_EXCESS"]
