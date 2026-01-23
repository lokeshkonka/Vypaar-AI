"""Test health endpoint."""

import pytest
from fastapi import status


@pytest.mark.api
def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "services" in data
    
    # Check services
    services = data["services"]
    assert "database" in services
    assert "redis" in services
    assert "ml_models" in services
    assert "scraper" in services


@pytest.mark.api
def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"
    assert "docs" in data
    assert "timestamp" in data
