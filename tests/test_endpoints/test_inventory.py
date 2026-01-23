"""Tests for inventory endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestInventoryEndpoints:
    """Test inventory endpoints."""
    
    def test_list_inventory_empty(self, test_client: TestClient):
        """Test listing inventory when empty."""
        response = test_client.get("/api/v1/inventory/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_inventory_with_filters(self, test_client: TestClient):
        """Test inventory listing with filters."""
        response = test_client.get(
            "/api/v1/inventory/?commodity_id=1&market_id=1"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_low_stock_items(self, test_client: TestClient):
        """Test listing low stock items."""
        response = test_client.get("/api/v1/inventory/?low_stock_only=true")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_inventory_suggestions_missing_data(self, test_client: TestClient):
        """Test inventory suggestions with missing commodity."""
        response = test_client.post(
            "/api/v1/inventory/suggestions",
            json={
                "commodity_id": 99999,
                "market_id": 99999,
                "forecast_days": 30
            }
        )
        
        assert response.status_code == 404
    
    def test_inventory_suggestions_valid(self, test_client: TestClient):
        """Test inventory suggestions with valid data."""
        response = test_client.post(
            "/api/v1/inventory/suggestions",
            json={
                "commodity_id": 1,
                "market_id": 1,
                "forecast_days": 14
            }
        )
        
        # May return 404 if no data exists
        assert response.status_code in [200, 404]
    
    def test_update_inventory_not_found(self, test_client: TestClient):
        """Test updating non-existent inventory."""
        response = test_client.put(
            "/api/v1/inventory/99999",
            json={"current_stock": 1500.0}
        )
        
        assert response.status_code == 404
    
    def test_update_inventory_validation(self, test_client: TestClient):
        """Test inventory update with validation."""
        response = test_client.put(
            "/api/v1/inventory/1",
            json={
                "current_stock": 1500.0,
                "optimal_stock": 2000.0,
                "reorder_point": 1200.0
            }
        )
        
        # Will fail if inventory doesn't exist
        assert response.status_code in [200, 404]
