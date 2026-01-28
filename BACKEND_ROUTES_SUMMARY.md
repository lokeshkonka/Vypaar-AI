# Backend Routes Summary

## Frontend-Backend API Integration

All routes are available at multiple prefixes:
- `/api/*` - Primary endpoint
- `/api/v1/*` - Versioned endpoint  
- `/*` - Root level (for special routes)

---

## User Management Routes

### POST `/users/init`
**Purpose:** Initialize or sync user with backend (Clerk integration)

**Request:**
```bash
POST /api/users/init
Authorization: Bearer {token}
```

**Response:**
```json
{
  "status": "success",
  "message": "User initialized",
  "timestamp": "2026-01-28T18:00:00Z",
  "user": {
    "initialized": true
  }
}
```

**Status:** ✅ Implemented

---

## Inventory Routes

### GET `/inventory/dashboard`
**Purpose:** Get all inventory items for dashboard display

**Query Parameters:**
- `skip` (optional): Number of items to skip (default: 0)
- `limit` (optional): Maximum items to return (default: 100, max: 500)

**Response:**
```json
[
  {
    "market": "Delhi",
    "category": "Grains",
    "product": "Rice",
    "current": 500,
    "suggested": 575,
    "risk": "Medium"
  }
]
```

**Status:** ✅ Implemented

---

### GET `/inventory/filter`
**Purpose:** Filter inventory items by market, category, product, or risk level

**Query Parameters:**
- `market` (optional): Filter by market name
- `category` (optional): Filter by commodity category
- `product` (optional): Filter by product name
- `risk` (optional): Filter by risk level (High, Medium, Low)
- `skip` (optional): Number of items to skip (default: 0)
- `limit` (optional): Maximum items to return (default: 100, max: 500)

**Example Request:**
```bash
GET /api/inventory/filter?market=Delhi&risk=High&limit=50
```

**Response:** Same as `/inventory/dashboard`

**Status:** ✅ Implemented

---

### POST `/inventory/update`
**Purpose:** Update inventory items

**Request Body:**
```json
{
  "filters": {
    "market": "Delhi",
    "category": "Grains"
  },
  "items": [
    {
      "market": "Delhi",
      "category": "Grains",
      "product": "Rice",
      "current": 500,
      "suggested": 575,
      "risk": "Medium"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Updated 1 inventory items",
  "timestamp": "2026-01-28T18:00:00Z",
  "items_updated": 1
}
```

**Status:** ✅ Implemented

---

## Forecast Routes

### POST `/forecast`
**Purpose:** Generate price forecast for a product in a market

**Request Body:**
```json
{
  "market": "Delhi",
  "product": "Rice",
  "forecast_range": 7
}
```

**Response:**
```json
{
  "market": "Delhi",
  "product": "Rice",
  "forecasts": [
    {
      "day": "Mon",
      "predicted_price": 50.5
    }
  ],
  "trend": "up",
  "averagePrice": 50.0
}
```

**Status:** ✅ Implemented

---

## Analysis Routes

### GET `/product-analysis`
**Purpose:** Get product analysis data (stock metrics, demand graph, impacts)

**Response:**
```json
{
  "selector_data": {
    "market": "Delhi",
    "product": "Rice",
    "forecastRange": "7 Days"
  },
  "stock_metrics": {
    "predictedDemand": 600,
    "stockNeeded": 690,
    "overstockRisk": 15,
    "understockRisk": 20
  },
  "demand_graph_data": [...],
  "impact_data": {
    "weather": [...],
    "festival": [...]
  },
  "recommendation_table": [...]
}
```

**Status:** ✅ Implemented

---

### GET `/insights`
**Purpose:** Get market insights and recommendations

**Status:** ✅ Implemented

---

### GET `/model/accuracy`
**Purpose:** Get ML model accuracy metrics

**Status:** ✅ Implemented

---

## Data Selector Routes

### GET `/commodities`
**Purpose:** Get list of all commodities

**Response:**
```json
[
  {
    "id": 1,
    "name": "Rice"
  }
]
```

**Status:** ✅ Implemented

---

### GET `/markets`
**Purpose:** Get list of all markets

**Response:**
```json
[
  {
    "id": 1,
    "name": "Delhi",
    "state": "Delhi"
  }
]
```

**Status:** ✅ Implemented

---

## Implementation Status

| Route | Method | Implemented | Frontend Compatible |
|-------|--------|-------------|-------------------|
| `/users/init` | POST | ✅ | ✅ |
| `/inventory/dashboard` | GET | ✅ | ✅ |
| `/inventory/filter` | GET | ✅ | ✅ |
| `/inventory/update` | POST | ✅ | ✅ |
| `/forecast` | POST | ✅ | ✅ |
| `/product-analysis` | GET | ✅ | ✅ |
| `/insights` | GET | ✅ | ✅ |
| `/model/accuracy` | GET | ✅ | ✅ |
| `/commodities` | GET | ✅ | ✅ |
| `/markets` | GET | ✅ | ✅ |

---

## Frontend Integration Points

### InventoryContext
- Calls `/api/inventory/dashboard` on mount
- Calls `/api/inventory/update` on save

### ForecastContext
- Calls `/api/forecast` POST with market, product, forecast_range

### UserSync Component
- Calls `/api/users/init` POST with Bearer token on mount

### ContextAnalysis
- Reads forecast data from localStorage
- Transforms and calculates stock metrics
- Falls back to `/api/product-analysis` GET if no cache

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `422`: Validation error
- `500`: Server error

Error responses follow this format:
```json
{
  "error": "ErrorType",
  "message": "Human readable message",
  "details": {...},
  "timestamp": "2026-01-28T18:00:00Z"
}
```

---

## Running the Backend

```bash
# From project root
cd backend

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# View API docs
# http://localhost:8000/docs
```

---

## Last Updated
January 28, 2026

## Changes Made
1. ✅ Updated `/users/init` to accept Bearer token from Authorization header
2. ✅ Added `/inventory/filter` endpoint with multi-filter support
3. ✅ Added `/inventory/update` POST endpoint
4. ✅ All endpoints properly integrated and aligned with frontend expectations
