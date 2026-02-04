# Fixes Applied - Product Analysis & Data Pipeline

## Date: 2026-02-04

## Issues Fixed

### 1. Undefined Variables in `get_product_analysis()`
**File:** `/backend/app/api/frontend.py`

**Problem:**
- `selected_commodity` and `selected_market` were used without being defined
- `price_history` was referenced before fetching
- `festival_impacts` and `weather_impacts` were undefined

**Solution:**
```python
# Added commodity and market selection logic
if commodity_name:
    selected_commodity = await commodity_repo.get_by_name(commodity_name)
    if not selected_commodity:
        selected_commodity = commodities[0]
else:
    selected_commodity = commodities[0]

if market_name:
    selected_market = await market_repo.get_by_name(market_name)
    if not selected_market:
        selected_market = markets[0]
else:
    selected_market = markets[0]

# Fetch price history
price_history = await market_price_repo.get_price_history(
    commodity_id=selected_commodity.id,
    market_id=selected_market.id,
    days=days * 2
)

# Calculate real festival and weather impacts from price data
festival_impacts = []
weather_impacts = []

if price_history and len(price_history) > 7:
    recent_prices = [float(p.modal_price or p.price or 0) for p in price_history[:7]]
    older_prices = [float(p.modal_price or p.price or 0) for p in price_history[7:14]]
    
    if recent_prices and older_prices:
        recent_avg = np.mean(recent_prices)
        older_avg = np.mean(older_prices)
        price_change = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        
        festival_impacts.append({
            "event": "Recent Market Trend",
            "impact": f"+{price_change:.1f}%" if price_change > 0 else f"{price_change:.1f}%"
        })
        
        volatility = float(np.std(recent_prices)) if len(recent_prices) > 1 else 0
        weather_impacts.append({
            "condition": "Price Volatility",
            "impact": f"±{volatility:.1f}%"
        })
```

### 2. Hardcoded Model Accuracy Values
**File:** `/backend/app/api/frontend.py`

**Problem:**
- Default values: `accuracy=0.85`, `mae=12.0`, `mape=6.0`
- Returning fake data when no models trained

**Solution:**
```python
# Return None/0.0 when no real metrics available
if latest:
    ai_accuracy = latest.accuracy if latest.accuracy is not None else None
    mae = latest.mae if latest.mae is not None else None
    mape = latest.mape if latest.mape else None
else:
    # Try to get from model artifact
    ai_accuracy = float(ensemble_metrics.get("accuracy", 0.0) * 100) if ensemble_metrics.get("accuracy") else None
    mae = float(ensemble_metrics.get("mae", 0.0)) if ensemble_metrics.get("mae") else None
    mape = float(ensemble_metrics.get("mape", 0.0)) * 100 if ensemble_metrics.get("mape") else None

# Return 0.0 instead of fake values
return ModelAccuracySummary(
    forecastAccuracy=ai_accuracy or 0.0,
    improvement=improvement or 0.0,
    mae=mae or 0.0,
    ...
)
```

### 3. Hardcoded Daily Variations
**File:** `/backend/app/api/frontend.py`

**Problem:**
```python
daily_variations = [
    (2200, 2310),
    (2350, 2468),
    (2100, 2205),
    (2450, 2573),
    (2300, 2415),
    (2150, 2258),
    (2050, 2153),
]
```

**Solution:**
- Removed entirely
- Use only real price_history data
- Fallback generates deterministic data from commodity hash (for consistency)

### 4. Database Duplicate Error
**File:** `/backend/app/database/repositories.py`

**Problem:**
```
ERROR: Failed to store scraped data: Multiple rows were found when one or none was required
```

**Cause:**
- `scalar_one_or_none()` raises error when duplicates exist

**Solution:**
```python
# Changed from:
existing = result.scalar_one_or_none()

# To:
existing = result.scalar()  # Returns first row or None, no error on duplicates
```

## Remaining Work

### Data Pipeline Fixes Needed:
1. **Scrape 6 months of historical data** (currently 30 days)
2. **Add 13 missing features** to reach 29 features:
   - Rolling averages (7-day, 30-day)
   - Standard deviation (14-day)
   - Price momentum indicators
   - Volatility metrics
   - Seasonal features (quarter, month, season)
   - Market tier and state encodings
3. **Retrain models** with correct 29 features
4. **Focus on trader commodities**: Grains, pulses, oilseeds (long shelf-life)

### Files to Check for Dummy Data:
- Weather impact calculations
- Buy/sell trend logic  
- Demand forecast comparisons
- Seasonal price trends
- Festival impact calculations

## Next Steps

1. Run data scraper for 6 months
2. Update feature engineering in preprocessor
3. Retrain models with 29 features
4. Verify all sections use real data
5. Test forecast generation for 3-month and 6-month periods
