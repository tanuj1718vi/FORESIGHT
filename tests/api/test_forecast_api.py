"""Integration tests for Forecasting REST endpoints."""

from fastapi.testclient import TestClient
import pytest

from foresight.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.api
def test_predict_single_endpoint(client: TestClient) -> None:
    """Verify POST /api/v1/forecast/predict returns valid point forecast."""
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
    resp = client.post("/api/v1/forecast/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sku_id"] == "SKU-1001"
    assert data["predicted_demand"] >= 0.0
    assert data["model_name"] == "XGBoost"


@pytest.mark.api
def test_predict_batch_endpoint(client: TestClient) -> None:
    """Verify POST /api/v1/forecast/predict/batch processes multiple items."""
    payload = {
        "items": [
            {
                "sku_id": "SKU-1001",
                "store_id": "STORE-001",
                "date": "2024-08-01",
                "features": {"lag_1": 20.0, "rolling_mean_7": 22.0},
            },
            {
                "sku_id": "SKU-1002",
                "store_id": "STORE-002",
                "date": "2024-08-01",
                "features": {"lag_1": 15.0, "rolling_mean_7": 14.0},
            },
        ]
    }
    resp = client.post("/api/v1/forecast/predict/batch", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_items"] == 2
    assert len(data["predictions"]) == 2
