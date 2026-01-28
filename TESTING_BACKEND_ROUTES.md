# Backend Routes Testing Guide

## Quick Test Commands

### 1. Test User Initialization
```bash
curl -X POST http://localhost:8000/api/users/init \
  -H "Authorization: Bearer test_token_12345" \
  -H "Content-Type: application/json"
```

Expected Response:
```json
{
  "status": "success",
  "message": "User initialized",
  "timestamp": "2026-01-28T18:00:00.000Z",
  "user": {
    "initialized": true
  }
}
```

---

### 2. Test Inventory Dashboard
```bash
curl -X GET "http://localhost:8000/api/inventory/dashboard?limit=10" \
  -H "Content-Type: application/json"
```

Expected Response:
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

---

### 3. Test Inventory Filter
```bash
# Filter by market
curl -X GET "http://localhost:8000/api/inventory/filter?market=Delhi" \
  -H "Content-Type: application/json"

# Filter by risk level
curl -X GET "http://localhost:8000/api/inventory/filter?risk=High" \
  -H "Content-Type: application/json"

# Multiple filters
curl -X GET "http://localhost:8000/api/inventory/filter?market=Delhi&risk=High&category=Grains" \
  -H "Content-Type: application/json"
```

---

### 4. Test Inventory Update
```bash
curl -X POST http://localhost:8000/api/inventory/update \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

Expected Response:
```json
{
  "status": "success",
  "message": "Updated 1 inventory items",
  "timestamp": "2026-01-28T18:00:00.000Z",
  "items_updated": 1
}
```

---

### 5. Test Forecast Generation
```bash
curl -X POST http://localhost:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "market": "Delhi",
    "product": "Rice",
    "forecast_range": 7
  }'
```

---

### 6. Test Commodities Endpoint
```bash
curl -X GET http://localhost:8000/api/commodities \
  -H "Content-Type: application/json"
```

---

### 7. Test Markets Endpoint
```bash
curl -X GET http://localhost:8000/api/markets \
  -H "Content-Type: application/json"
```

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI (OpenAPI):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Testing from Frontend

### In Browser Console

```javascript
// Test user init
fetch('http://localhost:8000/api/users/init', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer test_token',
    'Content-Type': 'application/json'
  }
}).then(r => r.json()).then(console.log)

// Test inventory dashboard
fetch('http://localhost:8000/api/inventory/dashboard')
  .then(r => r.json())
  .then(console.log)

// Test inventory filter
fetch('http://localhost:8000/api/inventory/filter?market=Delhi&risk=High')
  .then(r => r.json())
  .then(console.log)

// Test inventory update
fetch('http://localhost:8000/api/inventory/update', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filters: { market: 'Delhi' },
    items: [{ market: 'Delhi', product: 'Rice', current: 500, suggested: 575, risk: 'Medium' }]
  })
}).then(r => r.json()).then(console.log)
```

---

## Troubleshooting

### CORS Issues
- Ensure CORS is enabled in backend (already configured)
- Check `settings.cors_origins` includes frontend URL

### Connection Refused
- Verify backend is running on port 8000
- Check firewall settings
- Ensure no other service is using port 8000

### Invalid Token
- Bearer token format: `Authorization: Bearer {token}`
- Token is extracted but not currently validated
- Implementation ready for Clerk integration

### Empty Inventory Results
- Ensure database has inventory records
- Run seed script: `python scripts/seed_data.py`
- Check database connection

---

## Database Seeding

Before testing, seed the database with test data:

```bash
# From project root
cd backend
python scripts/seed_data.py
```

This will create:
- 4 Commodities (Rice, Wheat, Sugar, Cotton)
- 4 Markets (Delhi, Mumbai, Chennai, Bangalore)
- Sample inventory records
- Sample price records

---

## Performance Considerations

### Query Limits
- Default limit: 100 items
- Maximum limit: 500 items
- Adjust in query parameters as needed

### Pagination
- Use `skip` and `limit` for pagination
- Example: `?skip=100&limit=50` (items 100-150)

### Filtering
- Client-side filtering is applied after fetching
- For production, implement server-side filtering for large datasets

---

## Frontend Integration Checklist

- [ ] `/users/init` endpoint responding with Bearer token
- [ ] `/inventory/dashboard` returning filtered inventory
- [ ] `/inventory/filter` supporting market, category, product, risk filters
- [ ] `/inventory/update` accepting POST requests
- [ ] `/forecast` generating predictions
- [ ] All endpoints returning correct response formats
- [ ] Error responses properly formatted
- [ ] CORS headers set correctly
- [ ] Authentication/Bearer token handling

---

## Next Steps

1. ✅ Backend routes implemented
2. ✅ Frontend expecting these routes
3. 🔄 Test all endpoints with sample data
4. 🔄 Verify response formats match frontend expectations
5. 🔄 Deploy to production when verified

---

Generated: January 28, 2026
