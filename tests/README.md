# Agritech Backend Tests

Comprehensive test suite for the agricultural market analysis backend.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_health.py           # Health endpoint tests
├── test_endpoints/          # API endpoint tests
│   ├── test_market_data.py  # Market data endpoints
│   ├── test_predictions.py  # Prediction endpoints
│   └── test_inventory.py    # Inventory endpoints
├── test_ml/                 # Machine learning tests
│   └── test_preprocessor.py # Data preprocessing tests
└── test_repositories/       # Database repository tests
    └── test_commodity_repository.py
```

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_health.py

# Run specific test class
pytest tests/test_endpoints/test_market_data.py::TestCommodityEndpoints

# Run specific test function
pytest tests/test_health.py::test_health_endpoint
```

### Run Tests with Verbosity

```bash
# Verbose output
pytest -v

# Very verbose (show each test)
pytest -vv

# Show print statements
pytest -s
```

## Test Coverage

Generate coverage report:

```bash
pytest --cov=app --cov-report=html
```

View report:
```bash
open htmlcov/index.html
```

## Writing New Tests

### Test Fixtures

Use fixtures from `conftest.py`:

```python
def test_example(test_client, sample_commodity_data):
    response = test_client.post("/api/v1/commodities", json=sample_commodity_data)
    assert response.status_code == 201
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_operation(test_async_db_session):
    repo = CommodityRepository(test_async_db_session)
    result = await repo.create(name="Test", category="Test")
    assert result.id is not None
```

### Test Markers

```python
@pytest.mark.unit
def test_unit_example():
    pass

@pytest.mark.slow
@pytest.mark.integration
def test_slow_integration():
    pass
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Push to main branch
- Scheduled nightly builds

## Test Database

Tests use a separate SQLite database (`test_agritech.db`) that is:
- Created before each test function
- Cleaned up after each test
- Isolated from production/development data

## Mocking

For external dependencies:

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('app.scraper.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        # Test code
```

## Performance Testing

For performance benchmarks:

```bash
pytest tests/test_performance.py --benchmark-only
```

## Current Coverage

Target: 80%+

Run coverage to see current status:
```bash
pytest --cov=app --cov-report=term-missing
```
