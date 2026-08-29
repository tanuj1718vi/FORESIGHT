"""Integration tests for Risk and Prescriptive REST endpoints."""

from fastapi.testclient import TestClient
import pytest

from foresight.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def base_inventory_payload() -> dict:
    return {
        "sku_id": "SKU-1001",
        "store_id": "STORE-001",
        "current_on_hand": 5.0,
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


@pytest.mark.api
def test_assess_risk_endpoint(client: TestClient, base_inventory_payload: dict) -> None:
    """Verify POST /api/v1/risk/assess calculates financial exposure."""
    resp = client.post("/api/v1/risk/assess", json=base_inventory_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "composite_risk_score" in data
    assert "total_financial_exposure" in data
    assert data["risk_level"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


@pytest.mark.api
def test_prescribe_endpoint(client: TestClient, base_inventory_payload: dict) -> None:
    """Verify POST /api/v1/risk/prescribe generates prioritized action."""
    resp = client.post("/api/v1/risk/prescribe", json=base_inventory_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["action"] in ["EXPEDITE", "ORDER", "HOLD", "REDUCE", "MONITOR", "REBALANCE"]
    assert "justification" in data
    assert data["confidence_score"] > 0.0


@pytest.mark.api
def test_simulate_scenario_endpoint(client: TestClient, base_inventory_payload: dict) -> None:
    """Verify POST /api/v1/risk/simulate returns before vs after deltas."""
    payload = {
        "inventory_params": base_inventory_payload,
        "scenario": {
            "scenario_name": "Supplier Lead Time Bottleneck",
            "lead_time_multiplier": 1.5,
            "demand_multiplier": 1.2,
            "target_service_level": 0.98,
        },
    }
    resp = client.post("/api/v1/risk/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    assert data["result"]["delta_safety_stock"] > 0
