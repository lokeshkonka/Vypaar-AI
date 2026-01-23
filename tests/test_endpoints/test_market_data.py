"""Tests for market data endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestCommodityEndpoints:
    """Test commodity endpoints."""
    
    def test_list_commodities_empty(self, test_client: TestClient):
        """Test listing commodities when database is empty."""
        response = test_client.get("/api/v1/market-data/commodities")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_commodities_with_data(self, test_client: TestClient, test_async_db_session, sample_commodity_data):
        """Test listing commodities with data."""
        # TODO: Add commodity via repository
        response = test_client.get("/api/v1/market-data/commodities?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_commodity_not_found(self, test_client: TestClient):
        """Test getting non-existent commodity."""
        response = test_client.get("/api/v1/market-data/commodities/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_search_commodities(self, test_client: TestClient):
        """Test commodity search."""
        response = test_client.get("/api/v1/market-data/commodities?search=wheat")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestMarketEndpoints:
    """Test market endpoints."""
    
    def test_list_markets_empty(self, test_client: TestClient):
        """Test listing markets when database is empty."""
        response = test_client.get("/api/v1/market-data/markets")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_markets_with_pagination(self, test_client: TestClient):
        """Test market listing with pagination."""
        response = test_client.get("/api/v1/market-data/markets?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_get_market_not_found(self, test_client: TestClient):
        """Test getting non-existent market."""
        response = test_client.get("/api/v1/market-data/markets/99999")
        assert response.status_code == 404


class TestPriceEndpoints:
    """Test price endpoints."""
    
    def test_list_prices_with_filters(self, test_client: TestClient):
        """Test listing prices with filters."""
        response = test_client.get(
            "/api/v1/market-data/prices?commodity_id=1&market_id=1&limit=10"
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
    
    def test_get_latest_price(self, test_client: TestClient):
        """Test getting latest price."""
        response = test_client.get("/api/v1/market-data/prices/1/1/latest")
        # Should return 404 or valid data
        assert response.status_code in [200, 404]
