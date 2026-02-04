# Data Pipeline Architecture - Vypaar AI

## Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Agmarknet  │────▶│   Scraper    │────▶│  Database   │────▶│    Model     │
│   (Source)  │     │  (6 months)  │     │  (Storage)  │     │  (29 feat.)  │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                                                                       │
                                                                       ▼
                                                              ┌──────────────┐
                                                              │   Frontend   │
                                                              │  (3-6 month) │
                                                              └──────────────┘
```

## 1. Data Collection (Scraper)

**File:** `app/scraper/agmarknet_scraper.py`

### Commodities Focus
- ✅ Grains (12-month shelf life)
- ✅ Pulses (12-month shelf life)
- ✅ Oilseeds (6-12 month shelf life)
- ✅ Fibers (12-month shelf life)
- ❌ Vegetables (excluded - short shelf life)
- ❌ Fruits (excluded - short shelf life)

### Collection Schedule
- **Initial:** 180 days (6 months) on startup
- **Daily:** 2:30 AM - Full day update
- **Morning:** 8:00 AM - Market opening refresh
- **Afternoon:** 2:00 PM - Mid-day refresh

### Data Points Collected
- `commodity_id`, `market_id`, `date`
- `price` (modal/average)
- `min_price`, `max_price`
- `arrival` (quantity in market)

## 2. Data Storage (Database)

**File:** `app/database/models.py`

### Tables
- **commodities** - Trader-focused crops
- **markets** - Major trading hubs
- **market_prices** - Daily price + arrival data
- **prediction_metrics** - Model performance tracking

### Data Retention
- Keep last 180 days of data
- Archive older data for analysis
- No duplicate rows (commodity + market + date unique)

## 3. Feature Engineering (Preprocessor)

**File:** `app/ml/preprocessor.py`

### 29 Features Generated

#### A. Temporal (10 features)
```python
- day_of_week, day_of_month, month, quarter
- week_of_year, day_of_year
- month_sin, month_cos  # Cyclical encoding
- day_sin, day_cos      # Cyclical encoding
```

#### B. Festival Impact (4 features)
```python
- is_festival           # Binary: 0/1
- festival_effect       # Impact score: 0.0-1.0
- days_to_festival      # Countdown
- days_since_festival   # Days passed
```

#### C. Basic Trader (8 features)
```python
- market_size_factor         # Market tier weight
- commodity_shelf_life       # Storage months / 12
- price_to_arrival_ratio     # Price per unit supply
- seasonal_demand_index      # Seasonal multiplier
- festival_demand_multiplier # Festival boost
- supply_shock_indicator     # Sudden supply changes
- demand_trend              # 30-60 day trend
- market_competition_index   # Competition level
```

#### D. Advanced Trader (13 features) ⭐
```python
1. volatility_14d          # 14-day price std dev
2. momentum_7d             # 7-day price change
3. rsi_30d                 # RSI technical indicator
4. supply_volatility       # Supply std dev / mean
5. price_elasticity        # Price vs supply sensitivity
6. is_peak_season          # Binary: demand > 1.2
7. harvest_season          # Binary: Oct-Feb
8. price_trend_90d         # 30d vs 90d MA difference
9. market_premium_factor   # Market-specific premium
10. supply_consistency     # 1 / (7d supply std dev)
11. price_deviation_60d    # Z-score from 60d mean
12. quarter_demand_weight  # Q1:0.9, Q2:1.0, Q3:1.1, Q4:1.3
13. storage_cost_factor    # shelf_life * 0.8
```

### Feature Calculation Flow
```
Raw Data (DB)
    │
    ├─▶ Temporal Features (date extraction)
    │
    ├─▶ Festival Features (calendar lookup)
    │
    ├─▶ Basic Trader (simple calculations)
    │
    └─▶ Advanced Trader (rolling windows, technical indicators)
         │
         ▼
    29 Features Ready for Model
```

## 4. Model Training

**File:** `app/ml/ensemble.py`

### Ensemble Models
- **Random Forest** (weight: 0.5)
- **Gradient Boosting** (weight: 0.5)

### Training Process
```bash
python scripts/train_models.py
```

1. Load 6 months of data from DB
2. Generate 29 features
3. Train both models
4. Calculate metrics (accuracy, MAE, MAPE)
5. Save models + preprocessor + metrics
6. Update prediction_metrics table

### Model Files Saved
```
data/models/
├── ensemble_YYYYMMDD_HHMMSS.joblib
├── preprocessor_YYYYMMDD_HHMMSS.joblib
└── metadata.json
```

## 5. Prediction API

**File:** `app/api/frontend.py`

### Forecast Endpoint
```
POST /api/forecast
{
  "market": "Delhi",
  "product": "Wheat",
  "forecastRange": 90  // 7-180 days
}
```

### Prediction Flow
```
Request
    │
    ├─▶ Fetch historical data (180 days)
    │
    ├─▶ Generate 29 features
    │
    ├─▶ Load trained ensemble
    │
    ├─▶ Predict prices for each day (7-180)
    │
    └─▶ Calculate confidence intervals
         │
         ▼
    Return forecast + trend + metrics
```

### Response Structure
```json
{
  "forecasts": [
    {
      "date": "2026-02-05",
      "predicted_price": 2450.50,
      "lower_bound": 2350.00,
      "upper_bound": 2550.00,
      "confidence": 0.89
    }
  ],
  "trend": "up",
  "avgPrice": 2400.00,
  "forecastRange": "Next 90 Days"
}
```

## 6. Model Metrics Tracking

### Real Metrics (No Hardcoding)
```python
# BEFORE (hardcoded):
ai_accuracy = 0.85
mae = 12.0
mape = 0.06

# AFTER (from database):
latest = await metrics_repo.get_latest()
ai_accuracy = latest.accuracy  # Real value
mae = latest.mae               # Real value
mape = latest.mape             # Real value
```

### Metrics Updated
- After each training session
- Stored in `prediction_metrics` table
- Displayed on dashboard
- Used for model comparison

## 7. Scheduled Tasks

**File:** `app/services/scheduler.py`

### Jobs
1. **Daily Collection** (2:30 AM)
   - Scrape 180 days of data
   - Store in database
   - Update existing records

2. **Morning Refresh** (8:00 AM)
   - Quick scrape of current day
   - Update market opening prices

3. **Afternoon Refresh** (2:00 PM)
   - Mid-day price update
   - Capture price movements

4. **Weekly Retraining** (Sunday 3:00 AM)
   - Retrain all models
   - Update metrics
   - Archive old models

## 8. Data Quality Checks

### Before Storing
- ✅ commodity_id and market_id exist
- ✅ Date is valid
- ✅ Price > 0
- ✅ No duplicates (commodity + market + date)

### Before Training
- ✅ At least 90 days of data
- ✅ No missing price values
- ✅ Outliers clipped (IQR method)
- ✅ Features scaled (StandardScaler)

### Before Prediction
- ✅ Models loaded successfully
- ✅ Preprocessor matches model
- ✅ Feature count = 29
- ✅ Historical data available

## 9. Error Handling

### Scraper Failures
- Log error, continue with other commodities
- Retry failed scrapes next cycle
- Generate fallback data if critical

### Model Failures
- Return 0.0 metrics if no model
- Use historical average as fallback
- Alert administrator

### Database Errors
- Rollback transaction
- Log detailed error
- Retry with exponential backoff

## 10. Performance Optimization

### Database
- Index on (commodity_id, market_id, date)
- Batch inserts (commit every 100 rows)
- Connection pooling

### Feature Generation
- Vectorized operations (pandas/numpy)
- Group-by optimizations
- Cache computed features

### Model Inference
- Load models once (dependency injection)
- Batch predictions when possible
- Parallel processing for multiple forecasts

## Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Feature Count Verification
```bash
python scripts/verify_features.py
# Expected: 29 features ✅
```

### Integration Test
```bash
# 1. Start backend
python run.py

# 2. Wait for initial scraping (15 min)

# 3. Train models
python scripts/train_models.py

# 4. Test forecast API
curl -X POST http://localhost:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{"market":"Delhi","product":"Wheat","forecastRange":90}'
```

## Monitoring

### Logs
- Location: `logs/agritech.log`
- Level: INFO (production), DEBUG (development)
- Rotation: Daily

### Metrics to Track
- Scraping success rate
- Model accuracy (MAE, MAPE)
- API response time
- Database size growth
- Feature generation time

---

**Last Updated:** 2026-02-04
**Pipeline Status:** ✅ Operational
**Feature Count:** 29
**Data Coverage:** 6 months
**Forecast Range:** 7-180 days
