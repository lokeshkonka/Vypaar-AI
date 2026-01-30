# 🚀 Quick Start Guide - New Features

## What's New?

Three major features have been implemented:

1. **Real Discussions System** - Production-ready community board
2. **Watchlist Feature** - Save favorite commodities/markets  
3. **Market Trend Analysis** - AI-powered price trend insights

## Getting Started

### Step 1: Database Migration

Run the Alembic migration to create new tables:

```bash
cd backend
alembic upgrade head
```

This creates 3 new tables:
- `discussions` - Community discussions
- `watchlists` - User favorites
- `market_trend_analysis` - Trend data

### Step 2: Start the Backend

```bash
cd backend
python run.py
```

Visit Swagger UI: `http://localhost:8000/docs`

### Step 3: Test the Endpoints

#### Create a Discussion
```bash
curl -X POST http://localhost:8000/api/v1/discussions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Gold prices rising",
    "content": "Gold has broken through $2050 resistance...",
    "commodity": "Gold",
    "author": "TraderJoe",
    "tags": ["gold", "bullish"]
  }'
```

#### Add to Watchlist
```bash
curl -X POST http://localhost:8000/api/v1/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "commodity_id": 1,
    "market_id": 1,
    "alert_on_price_change": true,
    "price_change_threshold": 5.0
  }'
```

#### Get Trend Analysis
```bash
curl http://localhost:8000/api/v1/market-trends/1/1
```

## API Endpoints

### Discussions
- `GET /api/v1/discussions` - List all
- `POST /api/v1/discussions` - Create
- `GET /api/v1/discussions/{id}` - Get one
- `PUT /api/v1/discussions/{id}` - Update
- `DELETE /api/v1/discussions/{id}` - Delete
- `POST /api/v1/discussions/{id}/like` - Like
- `GET /api/v1/discussions/commodity/{name}` - Filter by commodity

### Watchlist
- `GET /api/v1/watchlist/{user_id}` - Get user's watchlist
- `POST /api/v1/watchlist` - Add to watchlist
- `PUT /api/v1/watchlist/{id}` - Update
- `DELETE /api/v1/watchlist/{id}` - Remove

### Market Trends
- `GET /api/v1/market-trends/{commodity_id}/{market_id}` - Multi-period comparison
- `GET /api/v1/market-trends/period/{c_id}/{m_id}/{days}` - Specific period
- `GET /api/v1/market-trends/history/{c_id}/{m_id}` - Historical data
- `GET /api/v1/market-trends/analyze/{c_id}/{m_id}` - Real-time analysis

## Frontend Integration (TODO)

Create React components for:
1. DiscussionBoard component
2. WatchlistPanel component  
3. TrendChart component

See [NEW_FEATURES_IMPLEMENTATION.md](NEW_FEATURES_IMPLEMENTATION.md) for detailed docs.

## Key Features

✅ Real database storage (no mocks)  
✅ Pagination & sorting  
✅ Search functionality  
✅ Price alerts  
✅ Trend analysis  
✅ Full error handling  
✅ Comprehensive logging  

## Troubleshooting

**Error: "Discussion not found"**
- Ensure data was seeded or created via POST endpoint

**Error: "Watchlist entry already exists"**
- Each (user_id, commodity_id, market_id) combo must be unique

**Error: "No trend analysis available"**
- Trend data needs to be pre-calculated or populate market_prices table

## Files Changed

- `backend/app/database/models.py` - Added 3 new models
- `backend/app/database/repositories.py` - Added 3 new repos
- `backend/app/models/schemas.py` - Added schemas
- `backend/app/api/v1/endpoints/discussions.py` - Production version
- `backend/app/api/v1/endpoints/watchlist.py` - New file
- `backend/app/api/v1/endpoints/market_trends.py` - New file
- `backend/app/api/v1/router.py` - Registered routes
- `backend/app/api/dependencies.py` - Added dependencies

---

**Questions?** Check the detailed [NEW_FEATURES_IMPLEMENTATION.md](NEW_FEATURES_IMPLEMENTATION.md)
