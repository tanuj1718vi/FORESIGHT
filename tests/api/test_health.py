"""Integration tests for Health and Governance REST endpoints."""

from fastapi.testclient import TestClient
import pytest

from foresight.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.api
def test_health_liveness_endpoint(client: TestClient) -> None:
    """Verify /health returns 200 and healthy status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


@pytest.mark.api
def test_readiness_endpoint(client: TestClient) -> None:
    """Verify /readiness checks model and data availability."""
    resp = client.get("/readiness")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "champion_model_loaded" in data


@pytest.mark.api
def test_version_endpoint(client: TestClient) -> None:
    """Verify /version returns metadata and registered models."""
    resp = client.get("/version")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "1.0.0"
    assert "champion_forecaster" in data["models"]
