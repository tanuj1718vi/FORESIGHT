"""Integration tests for database-backed REST API endpoints."""

import pytest
from fastapi.testclient import TestClient

from foresight.api.main import app
from foresight.database.seeder import seed_database

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db() -> None:
    """Ensure database has seed records for API queries."""
    seed_database()


@pytest.mark.api
def test_get_products_endpoint() -> None:
    """Verify GET /api/v1/products returns seeded product catalog."""
    resp = client.get("/api/v1/products?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "products" in data
    assert data["total_count"] >= 1
    assert len(data["products"]) <= 10


@pytest.mark.api
def test_get_risk_and_recommendation_endpoints() -> None:
    """Verify GET /api/v1/risk/{sku_id} and GET /api/v1/recommendation/{sku_id}."""
    # First get a valid SKU from products
    resp_prods = client.get("/api/v1/products?limit=1")
    assert resp_prods.status_code == 200
    sample_sku = resp_prods.json()["products"][0]["sku_id"]

    resp_risk = client.get(f"/api/v1/risk/{sample_sku}?store_id=STORE-001")
    assert resp_risk.status_code == 200
    data_risk = resp_risk.json()
    assert "composite_risk_score" in data_risk
    assert data_risk["sku_id"] == sample_sku

    resp_rec = client.get(f"/api/v1/recommendation/{sample_sku}")
    assert resp_rec.status_code == 200
    data_rec = resp_rec.json()
    assert "work_orders" in data_rec


@pytest.mark.api
def test_get_model_performance_and_data_quality() -> None:
    """Verify GET /api/v1/model-performance and GET /api/v1/data-quality."""
    resp_perf = client.get("/api/v1/model-performance")
    assert resp_perf.status_code == 200
    assert "champion_model_name" in resp_perf.json()

    resp_dq = client.get("/api/v1/data-quality")
    assert resp_dq.status_code == 200
    assert resp_dq.json()["overall_status"] == "PASS"
