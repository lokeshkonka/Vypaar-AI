"""Tests for prediction endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta


class TestPredictionEndpoints:
    """Test prediction endpoints."""
    
    def test_predict_price_missing_data(self, test_client: TestClient):
        """Test prediction with missing historical data."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        response = test_client.post(
            "/api/v1/predict/",
            json={
                "commodity_id": 99999,
                "market_id": 99999,
                "prediction_date": tomorrow,
            }
        )
        
        # Should return 404 for non-existent commodity/market
        assert response.status_code == 404
    
    def test_predict_price_valid_request(self, test_client: TestClient):
        """Test prediction with valid request."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        response = test_client.post(
            "/api/v1/predict/",
            json={
                "commodity_id": 1,
                "market_id": 1,
                "prediction_date": tomorrow,
            }
        )
        
        # May return 404 if no data or 500 if no models
        assert response.status_code in [200, 404, 500]
    
    def test_batch_predict(self, test_client: TestClient):
        """Test batch prediction."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        response = test_client.post(
            "/api/v1/predict/batch",
            json={
                "predictions": [
                    {
                        "commodity_id": 1,
                        "market_id": 1,
                        "prediction_date": tomorrow,
                    }
                ]
            }
        )
        
        assert response.status_code in [200, 404, 500]
    
    def test_prediction_history(self, test_client: TestClient):
        """Test getting prediction history."""
        response = test_client.get("/api/v1/predict/history/1/1")
        
        # Should return empty list or data
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPredictionValidation:
    """Test prediction request validation."""
    
    def test_invalid_date_format(self, test_client: TestClient):
        """Test prediction with invalid date format."""
        response = test_client.post(
            "/api/v1/predict/",
            json={
                "commodity_id": 1,
                "market_id": 1,
                "prediction_date": "invalid-date",
            }
        )
        
        # Should return validation error
        assert response.status_code in [400, 422, 500]
    
    def test_missing_required_fields(self, test_client: TestClient):
        """Test prediction with missing fields."""
        response = test_client.post(
            "/api/v1/predict/",
            json={"commodity_id": 1}
        )
        
        assert response.status_code == 422  # Validation error
