# Remove All Dummy Data - Implementation Plan

## Current Issues

### Backend (/backend/app/api/frontend.py)

1. **Product Analysis Endpoint (line 485-613)**
   - `festival_impacts` variable used but NEVER defined (line 574)
   - `weather_impacts` variable used but NEVER defined (line 575)
   - `daily_variations` hardcoded (lines 541-549) - NOT USED
   - Demand forecast uses fallback dummy data (lines 560-571)
   - Missing variables causing runtime errors

2. **Forecast Endpoint (lines 118-240)**
   - Hardcoded daily variations: `[1.02, 1.08, 0.98, 1.05...]` (lines 145-152)
   - These dummy multipliers are applied to all forecasts
   - Should use ML model predictions instead

3. **Model Accuracy (lines 283-307)**
   - Fallback to hardcoded metrics when real data unavailable:
     - Forecast accuracy: 0.85 (85%)
     - MAE: 12.0
     - MAPE: 0.06 (6%)
   - Traditional method calculation is approximation
   - Should return actual model performance metrics

### Frontend Components

1. **WeatherImpact.tsx** - Uses static dummy data
2. **SeasonalTrends.tsx** - Hardcoded seasonal patterns
3. **DemandGraph.tsx** - Falls back to dummy when no data
4. **ImpactComponent.tsx** - Festival/weather from undefined backend vars
5. **RecommendTable.tsx** - Stock recommendations partially computed

## Solution: Real Data Implementation

### Step 1: Fix Backend Product Analysis

```python
# File: /backend/app/api/frontend.py
# Function: get_product_analysis()

# Calculate real festival impacts
async def calculate_festival_impacts(
    commodity: Commodity,
    price_history: List[MarketPrice],
    festival_calendar: FestivalCalendar
) -> List[ImpactItem]:
    impacts = []
    upcoming_festivals = festival_calendar.get_upcoming_festivals(days=30)
    
    for festival in upcoming_festivals:
        # Calculate price increase from historical data
        historical_impact = await calculate_historical_festival_impact(
            commodity, festival.name, price_history
        )
        impacts.append(ImpactItem(
            title=festival.name,
            subtitle=f"High demand expected",
            delta=f"+{historical_impact:.1f}%",
            positive=True
        ))
    return impacts

# Calculate real weather impacts
async def calculate_weather_impacts(
    commodity: Commodity,
    market: Market,
    price_history: List[MarketPrice]
) -> List[ImpactItem]:
    impacts = []
    
    # Get weather data (temperature, rainfall from external API or database)
    weather_data = await get_weather_forecast(market.state, market.district)
    
    # Analyze correlation between weather and prices
    if weather_data.temperature_rise > 5:
        temp_impact = calculate_temperature_price_correlation(price_history)
        impacts.append(ImpactItem(
            title="Temperature Rise",
            subtitle=f"Expected +{weather_data.temperature_rise}°C",
            delta=f"+{temp_impact:.1f}%",
            positive=False
        ))
    
    if weather_data.rainfall_forecast:
        rain_impact = calculate_rainfall_price_correlation(price_history)
        impacts.append(ImpactItem(
            title="Rainfall Pattern",
            subtitle="Moderate precipitation expected",
            delta=f"{rain_impact:+.1f}%",
            positive=rain_impact < 0
        ))
    
    return impacts
```

### Step 2: Remove Hardcoded Forecast Variations

```python
# File: /backend/app/api/frontend.py
# Function: generate_forecast()

# REMOVE lines 145-152 (hardcoded daily_variations)
# REMOVE the multiplication by these dummy values

# Instead, use ONLY ML model predictions:
for day_offset in range(1, days + 1):
    target_date = start_date + timedelta(days=day_offset)
    
    # Prepare real features (29 features)
    features = preprocessor.prepare_prediction_data(
        commodity=commodity,
        market=market,
        target_date=target_date,
        historical_prices=historical_prices
    )
    
    # Get ONLY model prediction (no dummy multipliers)
    pred, confidence = predictor.predict_with_confidence(features)
    
    forecast_data.append({
        "date": target_date.strftime("%Y-%m-%d"),
        "predicted_price": float(pred),
        "confidence": float(confidence)
    })
```

### Step 3: Real Model Accuracy Metrics

```python
# File: /backend/app/api/frontend.py
# Function: get_model_accuracy()

# REMOVE fallback hardcoded metrics (lines 290-296)
# Calculate from actual model performance on test data

def get_model_accuracy():
    # Load saved model metrics from training
    metrics_file = "data/models/latest_metrics.json"
    
    if not os.path.exists(metrics_file):
        raise HTTPException(404, "Model metrics not available. Please train model first.")
    
    with open(metrics_file) as f:
        metrics = json.load(f)
    
    # Use REAL metrics from model evaluation
    return {
        "forecastAccuracy": metrics["r2_score"] * 100,  # R² to percentage
        "mae": metrics["mae"],
        "mape": metrics["mape"],
        "improvement": metrics["improvement_over_baseline"]
    }
```

### Step 4: Calculate Demand Forecast from Sales Data

```python
# Add to product-analysis endpoint

# Fetch actual sales/arrival data
sales_data = await get_sales_history(commodity, market, days=90)

demand_graph = []
for i in range(days):
    date = today + timedelta(days=i)
    
    # Calculate actual demand from arrivals/sales
    historical_same_day = [
        s for s in sales_data 
        if s.date.weekday() == date.weekday()
    ]
    
    actual = np.mean([s.arrival for s in historical_same_day]) if historical_same_day else 0
    
    # Forecast using trend + seasonality
    forecast = predict_demand_ml(commodity, market, date, sales_data)
    
    demand_graph.append(DemandGraphPoint(
        day=date.strftime("%a"),
        actual=int(actual),
        forecast=int(forecast)
    ))
```

### Step 5: Seasonal Trends from Real Data

```python
# New endpoint: /api/seasonal-trends

@router.get("/seasonal-trends")
async def get_seasonal_trends(
    commodity_name: str,
    market_price_repo: MarketPriceRepository = Depends(get_market_price_repo)
):
    # Get 12 months of data
    prices = await market_price_repo.get_price_history(
        commodity_name=commodity_name,
        days=365
    )
    
    # Calculate average price by month
    monthly_avg = {}
    for price in prices:
        month = price.date.month
        if month not in monthly_avg:
            monthly_avg[month] = []
        monthly_avg[month].append(price.modal_price)
    
    seasonal_data = [
        {"month": month, "avg_price": np.mean(prices)}
        for month, prices in sorted(monthly_avg.items())
    ]
    
    # Identify best buying months (lowest prices)
    sorted_months = sorted(seasonal_data, key=lambda x: x["avg_price"])
    best_months = [m["month"] for m in sorted_months[:3]]
    
    return {
        "seasonal_data": seasonal_data,
        "best_buying_months": best_months
    }
```

### Step 6: Stock Recommendations from Inventory Analysis

```python
# Improve recommendation logic

for item in inventory_items:
    # Calculate based on:
    # 1. Historical demand patterns
    # 2. Upcoming festivals
    # 3. Seasonal trends
    # 4. Current stock levels
    
    demand_forecast = predict_demand(item.commodity, days=30)
    seasonal_factor = get_seasonal_multiplier(item.commodity, current_month)
    festival_boost = get_festival_demand_boost(item.commodity, days=30)
    
    suggested_stock = int(
        demand_forecast * seasonal_factor * (1 + festival_boost)
    )
    
    # Risk calculation
    days_of_stock = item.current_stock / (demand_forecast / 30)
    if days_of_stock < 7:
        risk = "High"
    elif days_of_stock < 15:
        risk = "Medium"
    else:
        risk = "Low"
```

## Implementation Steps

1. ✅ Fix undefined variables (festival_impacts, weather_impacts)
2. ⏳ Add real festival impact calculations
3. ⏳ Add real weather impact calculations  
4. ⏳ Remove hardcoded forecast variations
5. ⏳ Use only ML predictions
6. ⏳ Load real model metrics from training
7. ⏳ Calculate demand from actual arrivals
8. ⏳ Create seasonal trends endpoint with real data
9. ⏳ Improve stock recommendations logic
10. ⏳ Update frontend to remove fallbacks

## Testing Checklist

- [ ] Product analysis returns real festival data
- [ ] Weather impacts show actual correlations
- [ ] Forecasts use only ML models (no dummy multipliers)
- [ ] Model accuracy reflects actual performance
- [ ] Demand graph shows real sales vs forecast
- [ ] Seasonal trends calculated from 12 months data
- [ ] Stock recommendations based on real demand
- [ ] No dummy data in any endpoint
- [ ] All calculations traceable to database or ML models

## Files to Modify

### Backend
- `/backend/app/api/frontend.py` - Fix product_analysis, generate_forecast, model_accuracy
- `/backend/app/services/weather_service.py` - Create new service for weather data
- `/backend/app/services/festival_impact_service.py` - Create new service
- `/backend/app/services/demand_forecasting.py` - Create new service

### Frontend
- `/frontend/src/components/ProductAnalysis/WeatherImpact.tsx` - Remove dummy data
- `/frontend/src/components/ProductAnalysis/SeasonalTrends.tsx` - Use real API
- `/frontend/src/components/ProductAnalysis/DemandGraph.tsx` - Remove fallbacks
- `/frontend/src/components/ProductAnalysis/ImpactComponent.tsx` - Use real data

## Priority Order

1. **CRITICAL** - Fix undefined variables (causes crashes)
2. **HIGH** - Remove forecast variations (wrong predictions)
3. **HIGH** - Real model metrics (misleading users)
4. **MEDIUM** - Festival/weather calculations
5. **MEDIUM** - Seasonal trends
6. **LOW** - UI polish

