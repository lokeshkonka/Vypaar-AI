
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings

@pytest.fixture(scope="session")
def test_app():

    return app

@pytest.fixture(scope="function")
def client(test_app):

    with TestClient(test_app) as test_client:
        yield test_client

@pytest.fixture(scope="session")
def test_settings():

    return settings

@pytest.fixture(scope="function")
def sample_market_data():

    return {
        "market": "Delhi",
        "commodity": "Wheat",
        "price": 2500.0,
        "arrival": 1000.0,
        "date": "2026-01-21",
        "state": "Delhi"
    }

@pytest.fixture(scope="function")
def sample_prediction_request():

    return {
        "market": "Delhi",
        "commodity": "Wheat",
        "date": "2026-01-30",
        "features": {
            "historical_price": 2400.0,
            "season": "winter",
            "day_of_week": 4
        }
    }

@pytest.fixture(scope="function")
def sample_inventory_request():

    return {
        "commodity": "Wheat",
        "current_stock": 1000,
        "location": "Delhi",
        "forecast_days": 30
    }

@pytest.fixture(scope="function")
def sample_alert_config():

    return {
        "alert_type": "PRICE_THRESHOLD",
        "commodity": "Wheat",
        "market": "Delhi",
        "conditions": {
            "price_above": 2800,
            "price_below": 2200
        },
        "priority": "HIGH",
        "channels": ["in_app", "email"]
    }

@pytest.fixture(autouse=True)
def reset_loggers():

    import logging
    
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.setLevel(logging.WARNING)
    
    yield

@pytest.fixture(scope="function")
def mock_ml_model(monkeypatch):

    class MockModel:
        def predict(self, X):
            import numpy as np
            return np.array([2500.0] * len(X))
        
        def predict_proba(self, X):
            import numpy as np
            return np.array([[0.15, 0.85]] * len(X))
    
    return MockModel()

@pytest.fixture(scope="function")
def mock_redis(monkeypatch):

    class MockRedis:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value, ex=None):
            self.data[key] = value
            return True
        
        def delete(self, key):
            if key in self.data:
                del self.data[key]
            return True
        
        def exists(self, key):
            return key in self.data
    
    return MockRedis()
