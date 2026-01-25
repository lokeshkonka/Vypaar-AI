# AgriTech API Quick Reference

## 🚀 Quick Start

```bash
# Start the API server
uvicorn app.main:app --reload --port 8000

# Run tests
python scripts/test_api.py

# Retrain models
python scripts/retrain_and_seed.py
```

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### 1. Health Check
```bash
GET /health
```
Response: Service status, version, and component health

### 2. Market Data
```bash
# Get all prices
GET /market-data/prices?limit=100

# Filter by commodity
GET /market-data/prices?commodity_id=1

# Filter by market
GET /market-data/prices?market_id=1
```

### 3. Price Predictions
```bash
# Single prediction
POST /predict/
Content-Type: application/json

{
  "commodity_id": 1,
  "market_id": 1,
  "prediction_date": "2026-01-25"
}

# Batch predictions
POST /predict/batch
Content-Type: application/json

{
  "predictions": [
    {"commodity_id": 1, "market_id": 1, "prediction_date": "2026-01-25"},
    {"commodity_id": 2, "market_id": 2, "prediction_date": "2026-01-26"}
  ]
}
```

### 4. Model Metrics
```bash
GET /model-metrics/
```
Response: Model performance, accuracy, feature importance

### 5. Scheduler
```bash
GET /scheduler/status
```
Response: Background job status

### 6. Alerts
```bash
GET /alerts/
```
Response: Active alerts

---

## 🗄️ Database Schema

### Commodities
```sql
id | name   | category
---|--------|----------
1  | Wheat  | Cereals
2  | Rice   | Cereals
3  | Onion  | Vegetables
```

### Markets
```sql
id | name              | state        | city
---|-------------------|--------------|----------
1  | Azadpur          | Delhi        | Delhi
2  | APMC Mumbai      | Maharashtra  | Mumbai
3  | Chennai Koyambedu| Tamil Nadu   | Chennai
4  | Bangalore APMC   | Karnataka    | Bangalore
```

### MarketPrices
```sql
id | commodity_id | market_id | date       | price  | arrival
---|-------------|-----------|------------|--------|--------
...| 1           | 1         | 2026-01-10 | 2375.0 | 1000.0
```

---

## 🤖 ML Models

### Current Version
`20260124_195252`

### Model Types
- Random Forest (50% weight)
- Gradient Boosting (50% weight)

### Performance
- R² Score: ~0.85
- RMSE: ~₹150
- MAE: ~₹120
- Confidence: 99%+

### Features (16 total)
1. Commodity encoding (3 one-hot)
2. Market encoding (3 one-hot)
3. State encoding (2 one-hot)
4. Arrival quantity (1 float)
5. Festival indicators (7 temporal/festival features)

---

## 🔧 Common Tasks

### Add New Commodity
```python
from app.database.models import Commodity
commodity = Commodity(
    name="Potato",
    category="Vegetables"
)
# Add to database via repository
```

### Add New Market
```python
from app.database.models import Market
market = Market(
    name="Kolkata APMC",
    state="West Bengal",
    city="Kolkata"
)
```

### Scrape New Data
```bash
python scripts/scrape_data.py
```

### Retrain Models
```bash
python scripts/train_models.py
```

---

## 🐛 Troubleshooting

### Issue: Models not loading
**Solution**: Check `/data/models/` for latest ensemble files
```bash
ls -lh data/models/ensemble_*.joblib
```

### Issue: Database empty
**Solution**: Run seeding script
```bash
python scripts/retrain_and_seed.py
```

### Issue: API not responding
**Solution**: Check if server is running
```bash
curl http://localhost:8000/api/v1/health
```

### Issue: Prediction fails with 404
**Solution**: Ensure commodity-market pair has historical data
```bash
# Check database
sqlite3 agritech.db "SELECT * FROM market_prices WHERE commodity_id=1 AND market_id=1;"
```

---

## 📝 File Locations

### Important Paths
```
/home/vishal/code/agritech/
├── agritech.db                    # SQLite database
├── data/models/                   # ML models
├── data/raw/                      # Scraped data
├── logs/                          # Application logs
├── scripts/                       # Utility scripts
└── app/                           # Application code
```

### Configuration
```python
# app/config.py
DATABASE_URL = "sqlite+aiosqlite:///agritech.db"
MODEL_PATH = "data/models/"
LOG_LEVEL = "INFO"
```

---

## 📊 Response Examples

### Health Check
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": {"status": "healthy"},
    "scraper": {"status": "healthy"}
  }
}
```

### Price Prediction
```json
{
  "predicted_price": 3320.41,
  "confidence_interval": [3293.08, 3347.74],
  "model_confidence": 0.996,
  "models_used": ["random_forest", "gradient_boosting"],
  "model_metrics": {
    "ensemble_accuracy": 0.85,
    "rmse": 150.0,
    "mae": 120.0,
    "r2_score": 0.82
  }
}
```

---

## 🔄 Background Jobs

### Daily Scraping
- **Time**: 2:30 AM
- **Frequency**: Daily
- **Action**: Fetch latest prices from Agmarknet

### Weekly Retraining
- **Time**: 3:00 AM on Sundays
- **Frequency**: Weekly
- **Action**: Retrain models with new data

---

## 🧪 Testing

### Run All Tests
```bash
python scripts/test_api.py
```

### Test Specific Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/predict/ \
  -H "Content-Type: application/json" \
  -d '{"commodity_id":1,"market_id":1,"prediction_date":"2026-01-25"}'
```

### Check Logs
```bash
tail -f /tmp/api.log
```

---

## 📚 Dependencies

### Core
- FastAPI
- Uvicorn
- SQLAlchemy (async)
- Pydantic

### ML
- scikit-learn
- numpy
- pandas
- joblib

### Scraping
- httpx
- BeautifulSoup4
- lxml

### Scheduling
- APScheduler

---

## 💡 Tips

1. **Always check health endpoint first** when debugging
2. **Use batch predictions** for multiple forecasts (more efficient)
3. **Monitor logs** at `/tmp/api.log` for debugging
4. **Retrain models weekly** with new data for best accuracy
5. **Add more historical data** for better predictions
6. **Check feature alignment** if predictions fail after model updates

---

*Last Updated: January 24, 2026*
*Version: 1.0.0*
