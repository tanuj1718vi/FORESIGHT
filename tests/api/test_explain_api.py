"""Integration tests for Explainability REST endpoints."""

from fastapi.testclient import TestClient
import pytest

from foresight.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.api
def test_explain_drivers_endpoint(client: TestClient) -> None:
    """Verify POST /api/v1/explain/drivers returns SHAP attributions and executive narrative."""
    payload = {
        "sku_id": "SKU-1001",
        "store_id": "STORE-001",
        "date": "2024-08-01",
        "features": {
            "lag_1": 25.0,
            "lag_7": 24.0,
            "rolling_mean_7": 26.0,
            "rolling_mean_14": 25.5,
            "rolling_mean_28": 25.0,
            "is_promoted": 1,
            "is_weekend": 0,
            "day_of_week": 3,
            "month": 8,
            "discount_percentage": 0.15,
            "price_ratio": 0.85,
        },
    }
    resp = client.post("/api/v1/explain/drivers", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sku_id"] == "SKU-1001"
    assert data["predicted_value"] > 0
    assert "business_narrative" in data
    assert len(data["business_narrative"]) > 10
