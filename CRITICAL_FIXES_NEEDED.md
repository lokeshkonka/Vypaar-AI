# CRITICAL FIXES - Product Analysis Backend

## URGENT: Function is Broken - Multiple Undefined Variables

### Location
`/backend/app/api/frontend.py` - Function `get_product_analysis()` (lines 485-613)

### Critical Bugs

1. **Line 503-504**: `selected_market` and `selected_commodity` used but NEVER defined
2. **Line 562**: `selected_commodity` used again in fallback
3. **Line 574**: `festival_impacts` used but NEVER defined  
4. **Line 575**: `weather_impacts` used but NEVER defined
5. **Missing**: `price_history` variable referenced but not fetched

### Root Cause
The function queries repositories but never assigns results to the variables it uses.

### Required Fix

```python
@router.get("/product-analysis")
async def get_product_analysis(
    commodity_name: Optional[str] = Query(None),
    market_name: Optional[str] = Query(None),
    days: int = Query(7),
    commodity_repo: CommodityRepository = Depends(get_commodity_repo),
    market_repo: MarketRepository = Depends(get_market_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    market_price_repo: MarketPriceRepository = Depends(get_market_price_repo),
) -> ProductAnalysisResponse:
    try:
        # FIX 1: Define selected_commodity and selected_market
        commodities = await commodity_repo.get_all(limit=100)
        markets = await market_repo.get_all(limit=100)
        
        if not commodities or not markets:
            raise HTTPException(404, "No data available")
        
        # Select commodity
        selected_commodity = None
        if commodity_name:
            selected_commodity = next((c for c in commodities if c.name.lower() == commodity_name.lower()), None)
        if not selected_commodity:
            selected_commodity = commodities[0]
        
        # Select market
        selected_market = None
        if market_name:
            selected_market = next((m for m in markets if m.name.lower() == market_name.lower()), None)
        if not selected_market:
            selected_market = markets[0]
        
        # FIX 2: Fetch price_history
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        price_history = await market_price_repo.get_price_history(
            commodity_id=selected_commodity.id,
            market_id=selected_market.id,
            start_date=start_date,
            end_date=end_date
        )
        
        # FIX 3: Calculate festival_impacts (REAL DATA)
        festival_impacts = []
        upcoming_festivals = get_upcoming_festivals(days=30)  # From festival calendar
        for festival in upcoming_festivals:
            # Calculate historical price increase for this commodity during this festival
            historical_impact = calculate_festival_price_impact(
                selected_commodity, 
                festival.name, 
                price_history
            )
            
            festival_impacts.append(ImpactItem(
                title=festival.name,
                subtitle=f"Increased demand expected",
                delta=f"+{historical_impact:.1f}%" if historical_impact > 0 else f"{historical_impact:.1f}%",
                positive=historical_impact > 0
            ))
        
        # FIX 4: Calculate weather_impacts (REAL DATA)
        weather_impacts = []
        
        # Get weather forecast for the market location
        weather_data = get_weather_forecast(selected_market.state, days=7)
        
        # Calculate correlation between weather and prices from historical data
        temp_impact = calculate_temperature_price_correlation(price_history, weather_data)
        if abs(temp_impact) > 2:  # Significant impact
            weather_impacts.append(ImpactItem(
                title="Temperature Rise" if temp_impact > 0 else "Temperature Drop",
                subtitle=f"Expected {weather_data.temp_change:+.1f}°C",
                delta=f"{temp_impact:+.1f}%",
                positive=temp_impact < 0  # Lower temp usually better for preservation
            ))
        
        rainfall_impact = calculate_rainfall_price_correlation(price_history, weather_data)
        if abs(rainfall_impact) > 2:
            weather_impacts.append(ImpactItem(
                title="Rainfall Pattern",
                subtitle="Moderate precipitation expected",
                delta=f"{rainfall_impact:+.1f}%",
                positive=rainfall_impact > 0  # Rain usually good for supply
            ))
        
        # Rest of the function continues...
        selector_data = SelectorData(
            market=selected_market.name,
            product=selected_commodity.name,
            forecastRange=f"Next {days} Days"
        )
        
        # ... (rest of implementation)
```

## Temporary Workaround (Until Real Implementation)

If real weather API and festival calculations are not ready, at minimum initialize empty lists:

```python
# After selecting commodity and market
festival_impacts = []
weather_impacts = []
```

This prevents the crash, but data will be empty.

## Implementation Priority

1. **NOW** - Define selected_commodity, selected_market (prevents crash)
2. **NOW** - Fetch price_history (prevents crash)
3. **NOW** - Initialize festival_impacts and weather_impacts as empty lists (prevents crash)
4. **SOON** - Implement real festival impact calculations
5. **SOON** - Implement real weather impact calculations
6. **SOON** - Remove hardcoded forecast variations
7. **SOON** - Use real model metrics

## Files to Create

- `/backend/app/services/festival_impact.py` - Festival price impact calculations
- `/backend/app/services/weather_service.py` - Weather API integration
- `/backend/app/services/price_correlation.py` - Statistical correlations

## Testing Command

```bash
curl "http://localhost:8000/api/product-analysis?commodity_name=Wheat&market_name=Delhi&days=7"
```

Should return valid response without crashes.

