"""Tests for health endpoint."""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient):
    """Test health check endpoint."""
    response = test_client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "services" in data
    
    # Check services
    services = data["services"]
    assert "database" in services
    assert "ml_models" in services
    assert "scraper" in services


def test_health_endpoint_structure(test_client: TestClient):
    """Test health endpoint response structure."""
    response = test_client.get("/api/v1/health")
    data = response.json()
    
    # Validate service structure
    for service_name, service_data in data["services"].items():
        assert "status" in service_data
        assert "timestamp" in service_data
