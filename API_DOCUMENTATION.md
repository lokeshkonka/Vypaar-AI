# Agri-Tech Backend - API Documentation

## Overview

The Agri-Tech Backend provides a comprehensive REST API for agricultural market data analysis, price predictions, inventory management, and intelligent alerts. Built with FastAPI, it features ensemble ML models, real-time data scraping, and automated insights.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**API Prefix**: `/api/v1`

---

## 📑 Table of Contents

1. [Authentication](#authentication)
2. [Health & Status](#health--status)
3. [Market Data](#market-data)
4. [Price Predictions](#price-predictions)
5. [Inventory Management](#inventory-management)
6. [Alerts](#alerts)
7. [Model Metrics](#model-metrics)
8. [Scheduler](#scheduler)
9. [Response Codes](#response-codes)
10. [Error Handling](#error-handling)

---

## 🔐 Authentication

Currently, the API does not require authentication. Future versions will implement API key-based authentication.

---

## 🏥 Health & Status

### Check API Health

Get the health status of the API and all its services.

**Endpoint**: `GET /api/v1/health`

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-25T10:30:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "timestamp": "2026-01-25T10:30:00Z"
    },
    "ml_models": {
      "status": "loaded",
      "timestamp": "2026-01-25T10:30:00Z"
    },
    "scraper": {
      "status": "healthy",
      "timestamp": "2026-01-25T10:30:00Z"
    }
  }
}
```

---

## 📊 Market Data

### List Commodities

Get a list of all agricultural commodities.

**Endpoint**: `GET /api/v1/market-data/commodities`

**Query Parameters**:
- `category` (optional): Filter by category (e.g., "Cereals", "Vegetables")
- `search` (optional): Search by name
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 100, max: 500): Number of results

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/market-data/commodities?category=Vegetables&limit=10"
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "Wheat",
    "category": "Cereals",
    "unit": "Quintal",
    "created_at": "2026-01-20T12:00:00Z",
    "updated_at": "2026-01-20T12:00:00Z"
  },
  {
    "id": 3,
    "name": "Onion",
    "category": "Vegetables",
    "unit": "Quintal",
    "created_at": "2026-01-20T12:00:00Z",
    "updated_at": "2026-01-20T12:00:00Z"
  }
]
```

### Get Commodity by ID

Get detailed information about a specific commodity.

**Endpoint**: `GET /api/v1/market-data/commodities/{commodity_id}`

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/market-data/commodities/1"
```

**Response**:
```json
{
  "id": 1,
  "name": "Wheat",
  "category": "Cereals",
  "unit": "Quintal",
  "created_at": "2026-01-20T12:00:00Z",
  "updated_at": "2026-01-20T12:00:00Z"
}
```

### List Markets

Get a list of all agricultural markets.

**Endpoint**: `GET /api/v1/market-data/markets`

**Query Parameters**:
- `state` (optional): Filter by state
- `search` (optional): Search by name
- `skip` (optional): Pagination offset
- `limit` (optional): Number of results

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/market-data/markets?state=Maharashtra"
```

**Response**:
```json
[
  {
    "id": 2,
    "name": "Mumbai APMC",
    "state": "Maharashtra",
    "district": "Mumbai",
    "address": null,
    "latitude": null,
    "longitude": null,
    "created_at": "2026-01-20T12:00:00Z",
    "updated_at": "2026-01-20T12:00:00Z"
  }
]
```

### Get Market Prices

Query market prices with filters and pagination.

**Endpoint**: `GET /api/v1/market-data/prices`

**Query Parameters**:
- `commodity_id` (optional): Filter by commodity ID
- `market_id` (optional): Filter by market ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `skip` (optional): Pagination offset
- `limit` (optional): Number of results

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/market-data/prices?commodity_id=1&market_id=1&limit=10"
```

**Response**:
```json
{
  "data": [
    {
      "id": 1,
      "commodity_id": 1,
      "commodity_name": "Wheat",
      "market_id": 1,
      "market_name": "Azadpur",
      "date": "2026-01-25",
      "price": 2500.00,
      "min_price": 2400.00,
      "max_price": 2600.00,
      "modal_price": 2500.00,
      "arrival": 1500.50,
      "created_at": "2026-01-25T10:00:00Z",
      "updated_at": "2026-01-25T10:00:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 10,
  "timestamp": "2026-01-25T10:30:00Z"
}
```

### Get Latest Price

Get the latest price for a specific commodity-market pair.

**Endpoint**: `GET /api/v1/market-data/prices/{commodity_id}/{market_id}/latest`

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/market-data/prices/1/1/latest"
```

**Response**:
```json
{
  "id": 1,
  "commodity_id": 1,
  "commodity_name": "Wheat",
  "market_id": 1,
  "market_name": "Azadpur",
  "date": "2026-01-25",
  "price": 2500.00,
  "min_price": 2400.00,
  "max_price": 2600.00,
  "modal_price": 2500.00,
  "arrival": 1500.50,
  "created_at": "2026-01-25T10:00:00Z",
  "updated_at": "2026-01-25T10:00:00Z"
}
```

---

## 🔮 Price Predictions

### Predict Price (Single)

Get AI-powered price prediction with ensemble model metrics.

**Endpoint**: `POST /api/v1/predict/`

**Request Body**:
```json
{
  "commodity_id": 1,
  "market_id": 1,
  "prediction_date": "2026-01-26"
}
```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "commodity_id": 1,
    "market_id": 1,
    "prediction_date": "2026-01-26"
  }'
```

**Response**:
```json
{
  "predicted_price": 2550.00,
  "confidence_interval": [2450.00, 2650.00],
  "model_confidence": 0.87,
  "confidence_score": 0.87,
  "models_used": ["random_forest", "gradient_boosting"],
  "model_metrics": {
    "ensemble_accuracy": 0.92,
    "rmse": 85.30,
    "mae": 62.10,
    "r2_score": 0.89,
    "individual_models": [
      {
        "name": "random_forest",
        "accuracy": 0.91,
        "weight": 0.50,
        "status": "ACTIVE"
      },
      {
        "name": "gradient_boosting",
        "accuracy": 0.93,
        "weight": 0.50,
        "status": "ACTIVE"
      }
    ],
    "feature_importance": {
      "historical_price": 0.35,
      "season": 0.22,
      "market_arrival": 0.18,
      "day_of_week": 0.12,
      "festival_proximity": 0.08
    },
    "model_version": "20260124_212903",
    "trained_on": "2026-01-24",
    "training_samples": 12500
  },
  "prediction_metadata": {
    "timestamp": "2026-01-25T10:30:00Z",
    "processing_time_ms": 145,
    "data_freshness": "30 days historical data"
  }
}
```

### Batch Predict

Get predictions for multiple commodity-market pairs in one request.

**Endpoint**: `POST /api/v1/predict/batch`

**Request Body**:
```json
{
  "predictions": [
    {
      "commodity_id": 1,
      "market_id": 1,
      "prediction_date": "2026-01-26"
    },
    {
      "commodity_id": 2,
      "market_id": 2,
      "prediction_date": "2026-01-26"
    }
  ]
}
```

**Response**:
```json
{
  "predictions": [
    {
      "predicted_price": 2550.00,
      "confidence_interval": [2450.00, 2650.00],
      "model_confidence": 0.87,
      "models_used": ["random_forest", "gradient_boosting"],
      "model_metrics": { "..." },
      "prediction_metadata": { "..." }
    },
    {
      "predicted_price": 3600.00,
      "confidence_interval": [3450.00, 3750.00],
      "model_confidence": 0.85,
      "models_used": ["random_forest", "gradient_boosting"],
      "model_metrics": { "..." },
      "prediction_metadata": { "..." }
    }
  ],
  "total_predictions": 2,
  "successful": 2,
  "failed": 0,
  "timestamp": "2026-01-25T10:30:00Z"
}
```

### Get Prediction History

Retrieve historical predictions and their accuracy.

**Endpoint**: `GET /api/v1/predict/history/{commodity_id}/{market_id}`

**Query Parameters**:
- `days` (optional, default: 30): Number of days to look back

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/predict/history/1/1?days=7"
```

**Response**:
```json
[
  {
    "commodity_id": 1,
    "market_id": 1,
    "date": "2026-01-24",
    "predicted_price": 2480.00,
    "actual_price": 2500.00,
    "error": 20.00,
    "accuracy": 0.992,
    "confidence": 0.88,
    "average_accuracy": 0.91
  }
]
```

---

## 📦 Inventory Management

### List Inventory

Get inventory levels for all commodity-market pairs.

**Endpoint**: `GET /api/v1/inventory/`

**Query Parameters**:
- `commodity_id` (optional): Filter by commodity
- `market_id` (optional): Filter by market
- `low_stock_only` (optional): Show only low stock items
- `skip` (optional): Pagination offset
- `limit` (optional): Number of results

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/inventory/?low_stock_only=true"
```

**Response**:
```json
[
  {
    "id": 1,
    "commodity_id": 1,
    "commodity_name": "Wheat",
    "market_id": 1,
    "market_name": "Azadpur",
    "current_stock": 850.00,
    "optimal_stock": 2000.00,
    "min_stock": 500.00,
    "max_stock": 3000.00,
    "reorder_point": 1000.00,
    "last_restocked_at": "2026-01-20T10:00:00Z",
    "forecast_demand": 1200.00,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-25T10:00:00Z"
  }
]
```

### Get Inventory Suggestions

Get AI-powered inventory recommendations based on demand forecasting.

**Endpoint**: `POST /api/v1/inventory/suggestions`

**Request Body**:
```json
{
  "commodity_id": 1,
  "market_id": 1,
  "forecast_days": 30
}
```

**Response**:
```json
{
  "commodity_id": 1,
  "commodity_name": "Wheat",
  "market_id": 1,
  "market_name": "Azadpur",
  "current_stock": 850.00,
  "optimal_stock": 2200.00,
  "safety_stock": 450.00,
  "reorder_point": 1100.00,
  "reorder_quantity": 1350.00,
  "needs_reorder": true,
  "forecast_demand": 1750.00,
  "forecast_days": 30,
  "days_until_stockout": 12,
  "priority": "HIGH",
  "confidence": 0.85,
  "reasoning": [
    "Average daily demand: 58.33 units",
    "Forecast period: 30 days",
    "Safety stock: 450.00 units",
    "Current stock covers 12 days"
  ],
  "timestamp": "2026-01-25T10:30:00Z"
}
```

### Update Inventory

Update inventory stock levels.

**Endpoint**: `PUT /api/v1/inventory/{inventory_id}`

**Request Body**:
```json
{
  "current_stock": 1500.00,
  "optimal_stock": 2000.00,
  "reorder_point": 1000.00
}
```

---

## 🔔 Alerts

### Create Alert

Configure a new alert for price or inventory monitoring.

**Endpoint**: `POST /api/v1/alerts/`

**Request Body**:
```json
{
  "alert_type": "PRICE_THRESHOLD",
  "commodity_id": 1,
  "market_id": 1,
  "priority": "HIGH",
  "conditions": {
    "price_above": 3000
  },
  "notification_channels": ["email", "in_app"],
  "message": "Wheat price exceeded ₹3000/quintal"
}
```

**Alert Types**:
- `PRICE_THRESHOLD`: Alert when price crosses a threshold
- `INVENTORY_LOW`: Alert when inventory is low
- `INVENTORY_OVERSTOCK`: Alert for overstock
- `PRICE_VOLATILITY`: Alert on price volatility
- `TREND_CHANGE`: Alert on trend changes
- `EXPIRY_WARNING`: Alert for expiring stock

**Priority Levels**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`

**Response**:
```json
{
  "id": 1,
  "alert_type": "PRICE_THRESHOLD",
  "commodity_id": 1,
  "market_id": 1,
  "priority": "HIGH",
  "status": "ACTIVE",
  "conditions": {
    "price_above": 3000
  },
  "notification_channels": ["email", "in_app"],
  "message": "Wheat price exceeded ₹3000/quintal",
  "triggered_at": null,
  "resolved_at": null,
  "created_at": "2026-01-25T10:30:00Z",
  "updated_at": "2026-01-25T10:30:00Z"
}
```

### List Alerts

Get all configured alerts with optional filters.

**Endpoint**: `GET /api/v1/alerts/`

**Query Parameters**:
- `alert_type` (optional): Filter by type
- `priority` (optional): Filter by priority
- `status` (optional): Filter by status
- `commodity_id` (optional): Filter by commodity
- `market_id` (optional): Filter by market
- `active_only` (optional, default: true): Show only active alerts

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/?priority=HIGH&active_only=true"
```

### Update Alert

Update alert configuration or status.

**Endpoint**: `PATCH /api/v1/alerts/{alert_id}`

**Request Body**:
```json
{
  "status": "RESOLVED",
  "priority": "MEDIUM"
}
```

### Delete Alert

Delete an alert configuration.

**Endpoint**: `DELETE /api/v1/alerts/{alert_id}`

**Response**: `204 No Content`

---

## 📈 Model Metrics

### Get Model Metrics

Retrieve performance metrics for ML models.

**Endpoint**: `GET /api/v1/model/metrics`

**Query Parameters**:
- `model_name` (optional): Filter by model name
- `latest_only` (optional, default: true): Return only latest metrics

**Response**:
```json
[
  {
    "id": 1,
    "model_name": "random_forest",
    "model_version": "20260124_212903",
    "accuracy": 0.91,
    "rmse": 87.50,
    "mae": 65.30,
    "r2_score": 0.88,
    "mape": 0.026,
    "precision": null,
    "recall": null,
    "f1_score": null,
    "feature_importance": {
      "historical_price": 0.35,
      "season": 0.22
    },
    "training_samples": 10000,
    "test_samples": 2500,
    "training_date": "2026-01-24T12:00:00Z",
    "hyperparameters": {
      "n_estimators": 500,
      "max_depth": 18
    },
    "cross_validation_scores": [0.89, 0.91, 0.90, 0.92, 0.88],
    "created_at": "2026-01-24T15:00:00Z"
  }
]
```

### Get Model Status

Get current status of loaded ML models.

**Endpoint**: `GET /api/v1/model/status`

**Response**:
```json
{
  "ensemble_status": {
    "models_loaded": ["random_forest", "gradient_boosting"],
    "model_count": 2,
    "weights": {
      "random_forest": 0.50,
      "gradient_boosting": 0.50
    },
    "latest_version": "20260124_212903"
  },
  "prediction_statistics": {
    "total_predictions": 1250,
    "mean_prediction": 2650.50,
    "mean_confidence": 0.86,
    "mean_processing_time": 0.145
  },
  "timestamp": "2026-01-25T10:30:00Z"
}
```

---

## ⏰ Scheduler

### Get Scheduler Status

Get status of background automation jobs.

**Endpoint**: `GET /api/v1/scheduler/status`

**Response**:
```json
{
  "status": "running",
  "scheduled_jobs": [
    {
      "id": "daily_scrape",
      "name": "Daily market data collection",
      "next_run": "2026-01-26T02:30:00Z",
      "active": true
    },
    {
      "id": "weekly_retrain",
      "name": "Weekly model retraining",
      "next_run": "2026-01-26T03:00:00Z",
      "active": true
    }
  ],
  "message": "2 automated tasks are active"
}
```

### Trigger Manual Scrape

Manually trigger data collection.

**Endpoint**: `POST /api/v1/scheduler/trigger/scrape`

**Response**:
```json
{
  "status": "success",
  "message": "Data collection initiated successfully"
}
```

### Trigger Manual Retrain

Manually trigger model retraining.

**Endpoint**: `POST /api/v1/scheduler/trigger/retrain`

**Response**:
```json
{
  "status": "success",
  "message": "Model retraining initiated successfully"
}
```

---

## 📋 Response Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 201  | Created |
| 204  | No Content (successful deletion) |
| 400  | Bad Request (invalid input) |
| 404  | Not Found (resource doesn't exist) |
| 422  | Validation Error (request body validation failed) |
| 500  | Internal Server Error |

---

## ❌ Error Handling

All errors follow a consistent format:

```json
{
  "error": "NotFoundError",
  "message": "Commodity 99999 not found",
  "details": {
    "commodity_id": 99999
  },
  "timestamp": "2026-01-25T10:30:00Z"
}
```

**Validation Error Example**:
```json
{
  "error": "ValidationError",
  "message": "Request validation failed",
  "details": {
    "errors": [
      {
        "loc": ["body", "commodity_id"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  },
  "timestamp": "2026-01-25T10:30:00Z"
}
```

---

## 🔧 Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List commodities
curl http://localhost:8000/api/v1/market-data/commodities

# Get prediction
curl -X POST http://localhost:8000/api/v1/predict/ \
  -H "Content-Type: application/json" \
  -d '{"commodity_id": 1, "market_id": 1, "prediction_date": "2026-01-26"}'
```

### Using Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Get prediction
response = requests.post(
    f"{BASE_URL}/predict/",
    json={
        "commodity_id": 1,
        "market_id": 1,
        "prediction_date": "2026-01-26"
    }
)
print(response.json())
```

### Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📞 Support

For issues, questions, or feature requests:
- Check `/docs` for interactive API documentation
- Review logs in `logs/` directory
- Open an issue on GitHub

---

**Last Updated**: January 25, 2026  
**API Version**: 1.0.0
