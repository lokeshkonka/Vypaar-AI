<<<<<<< Updated upstream
<<<<<<< Updated upstream
# Trader-Focused Agricultural Platform Restructuring Plan

## Executive Summary
Transform Vypaar-AI into a professional trading platform focused on commodities with long shelf life (grains, pulses, oilseeds) that traders actually need for price forecasting and market analysis.

## Current Issues Identified

### 1. Data Pipeline Problems
- ❌ Scraped data not stored in database (Class 'builtins.dict' is not mapped error)
- ❌ Model expects 29 features but receives 16 features
- ❌ Only 30 days of data (insufficient for accurate predictions)
- ❌ Includes perishable vegetables (not trader-relevant)

### 2. Focus Issues
- Current: Mixed vegetables + grains
- Needed: Trader commodities (grains, pulses, oilseeds with 3-12 month shelf life)

## Solution Architecture

### Phase 1: Database & Storage Fix (Priority 1)

#### Fix the scraped data storage issue:
```python
# Problem: Passing dict objects to SQLAlchemy instead of model instances
# Solution: Ensure proper model instantiation in scheduler._store_scraped_data
```

### Phase 2: Commodity Focus (Priority 1)

#### Trader-Relevant Commodities Only:

**Cereals & Grains (Storage: 6-12 months)**
- Wheat
- Rice (Basmati, Non-Basmati)
- Maize (Corn)
- Bajra (Pearl Millet)
- Jowar (Sorghum)
- Barley
- Ragi (Finger Millet)

**Pulses & Lentils (Storage: 12 months)**
- Moong Dal (Green Gram)
- Chana (Chickpea)
- Toor Dal (Pigeon Pea)
- Urad Dal (Black Gram)
- Masoor Dal (Red Lentil)
- Rajma (Kidney Beans)

**Oilseeds (Storage: 6-9 months)**
- Soybean
- Groundnut (Peanut)
- Mustard
- Sunflower
- Sesame

**Spices (Long shelf life)**
- Turmeric
- Coriander Seeds
- Cumin
- Black Pepper

**Remove from platform:**
- All leafy vegetables (spoil in days)
- Tomato, Potato, Onion (perishable, high volatility)
- Short-shelf-life vegetables

### Phase 3: Data Collection Requirements (Priority 1)

#### Historical Data Requirement:
- Minimum: 6 months (180 days)
- Optimal: 1 year (365 days)
- Frequency: Daily scraping at multiple times

#### Scraping Schedule:
```
- 02:30 AM IST: Overnight data collection
- 08:00 AM IST: Morning market refresh
- 02:00 PM IST: Afternoon market refresh
- Sunday 03:00 AM: Weekly model retraining
```

### Phase 4: ML Pipeline Restructuring (Priority 2)

#### Feature Engineering (Target: 29 features):
```python
Features to Include:
1. Price features (5):
   - current_price
   - price_7day_avg
   - price_30day_avg
   - price_volatility_7day
   - price_trend_30day

2. Temporal features (8):
   - day_of_week
   - day_of_month
   - month
   - quarter
   - is_weekend
   - week_of_year
   - days_since_year_start
   - is_festival_season

3. Market features (6):
   - market_avg_price (by market)
   - commodity_market_volume
   - market_price_rank
   - distance_from_market_avg
   - market_volatility
   - relative_price_index

4. Commodity features (5):
   - commodity_category_encoded
   - commodity_avg_price (across all markets)
   - commodity_price_trend
   - seasonal_index
   - demand_indicator

5. Lag features (5):
   - price_lag_1day
   - price_lag_7days
   - price_lag_30days
   - arrival_lag_7days
   - price_change_7day
```

### Phase 5: Implementation Steps

#### Step 1: Clean Database
```bash
# Remove old data
rm data/agritech.db
rm data/vypaar.db
rm data/agricultural_prices.db

# Remove old models
rm -rf data/models/*
```

#### Step 2: Update Commodity List
```python
# File: backend/app/scraper/agmarknet_scraper.py
# Update scrape_commodities() to include only trader-relevant commodities
```

#### Step 3: Fix Data Storage
```python
# File: backend/app/services/scheduler.py
# Fix _store_scraped_data to properly create model instances
```

#### Step 4: Extend Historical Scraping
```python
# Update scrape_all() to collect 6 months of data
result = self.scraper.scrape_all(days_back=30, historical_days=180)
```

#### Step 5: Update Feature Engineering
```python
# File: backend/app/ml/preprocessor.py
# Add all 29 features as specified above
```

#### Step 6: Retrain Models
```bash
# After collecting 6 months data
python backend/scripts/retrain_models.py
```

### Phase 6: Frontend Adjustments

#### Dashboard Changes:
1. **Market Overview**
   - Show only trader commodities
   - Display storage life information
   - Add seasonal trends

2. **Price Analytics**
   - 6-month historical charts
   - Support/resistance levels
   - Volume analysis

3. **Forecasting**
   - 7-day, 15-day, 30-day predictions
   - Confidence intervals
   - Risk indicators

4. **Trading Signals**
   - Buy/sell recommendations
   - Price momentum indicators
   - Market sentiment

### Phase 7: Data Quality & Validation

#### Validation Rules:
```python
- Price range validation (min 100, max 100000 per quintal)
- Date validation (not future dates)
- Arrival validation (positive numbers)
- Duplicate detection (same commodity-market-date)
- Outlier detection (3-sigma rule)
```

### Phase 8: Performance Optimization

#### Database Indexes:
```sql
CREATE INDEX idx_market_prices_date ON market_prices(date);
CREATE INDEX idx_market_prices_commodity ON market_prices(commodity_id);
CREATE INDEX idx_market_prices_market ON market_prices(market_id);
CREATE INDEX idx_market_prices_composite ON market_prices(commodity_id, market_id, date);
```

## Implementation Timeline

### Week 1: Critical Fixes
- [x] Fix data storage error
- [ ] Update commodity list (trader-focused only)
- [ ] Extend historical scraping to 6 months
- [ ] Clean database and restart data collection

### Week 2: Feature Engineering
- [ ] Implement 29-feature preprocessing
- [ ] Update model training pipeline
- [ ] Add validation and quality checks
- [ ] Test end-to-end pipeline

### Week 3: Model Training & Testing
- [ ] Collect 6 months historical data
- [ ] Train models with correct features
- [ ] Validate prediction accuracy
- [ ] Fine-tune hyperparameters

### Week 4: Frontend & Polish
- [ ] Update dashboard for trader focus
- [ ] Remove vegetable-related features
- [ ] Add trading signals
- [ ] User testing and refinements

## Success Metrics

### Data Quality:
- ✅ 180+ days of historical data
- ✅ Daily data updates
- ✅ <5% missing data points
- ✅ Zero storage errors

### Model Performance:
- ✅ MAPE < 8% for 7-day predictions
- ✅ MAPE < 12% for 30-day predictions
- ✅ R² score > 0.75
- ✅ Consistent performance across commodities

### User Experience:
- ✅ <2 second page load
- ✅ Real-time data updates
- ✅ Accurate trading signals
- ✅ Intuitive trader interface

## Technical Debt to Address

1. Remove all vegetable-specific code
2. Consolidate multiple databases into one
3. Add proper error handling in scheduler
4. Implement data backup strategy
5. Add monitoring and alerting
6. Document API endpoints
7. Add unit tests for data pipeline
8. Implement data versioning

## Risk Mitigation

### Data Risks:
- **Risk**: Agmarknet website changes
- **Mitigation**: Implement robust scraping with fallbacks

### Model Risks:
- **Risk**: Poor predictions on new commodities
- **Mitigation**: Require minimum 3 months data before predictions

### Business Risks:
- **Risk**: Users expect vegetable data
- **Mitigation**: Clear communication about trader focus

## Conclusion

This restructuring transforms Vypaar-AI from a general agricultural platform into a professional trader tool focused on storable commodities. By collecting 6 months of historical data, implementing proper feature engineering (29 features), and focusing on trader-relevant commodities, we ensure accurate predictions and actionable insights for commodity traders.

## Next Actions

1. **Immediate**: Fix data storage error in scheduler
2. **Today**: Update commodity list to trader-focused only
3. **This Week**: Collect 6 months historical data
4. **Next Week**: Retrain models with 29 features
5. **Following Week**: Update frontend for trader experience
=======
=======
>>>>>>> Stashed changes
# Trader-Focused Agricultural Price Prediction Platform - Restructuring Plan

## Executive Summary
Transform the application into a professional trading platform focused on long-shelf-life commodities with accurate, real-time market data and predictive analytics.

## Current Critical Issues

### 1. Model Feature Mismatch
- **Problem**: Models expect 29 features, preprocessor provides 16
- **Impact**: All predictions fail, system uses fallback dummy data
- **Fix Required**: Retrain models or fix preprocessor alignment

### 2. Data Storage Failure
- **Problem**: `Class 'builtins.dict' is not mapped` error
- **Impact**: 3360+ scraped records cannot be saved to database
- **Fix Required**: Update database models to accept dictionary data structures

### 3. Stale Data Display
- **Problem**: Dashboard shows data only up to January 30th
- **Impact**: Traders making decisions on outdated information
- **Fix Required**: Fix storage pipeline and re-scrape recent data

### 4. Incorrect Commodity Focus
- **Problem**: Includes perishables (tomatoes, potatoes) unsuitable for trading
- **Impact**: Poor model accuracy, irrelevant for professional traders
- **Fix Required**: Filter to long-shelf-life commodities only

## Target User Profile: Professional Commodity Trader

### Primary Needs
1. **Real-time Market Data**: Live prices across multiple mandis
2. **Price Forecasting**: 7-30 day predictions for trading decisions
3. **Market Comparison**: Cross-market arbitrage opportunities
4. **Historical Trends**: 6+ months data for pattern analysis
5. **Risk Assessment**: Volatility indicators and confidence intervals

### Secondary Needs
1. Buy/Sell signal alerts
2. Market sentiment analysis
3. Weather impact predictions
4. Festival/seasonal trend analysis
5. Export data for external analysis

## Commodity Selection Strategy

### Include: Long Shelf-Life Commodities

#### Grains (Primary Focus)
- Wheat (6-12 months shelf life)
- Rice (Basmati, Non-Basmati) (12+ months)
- Maize/Corn (6-12 months)
- Barley (6-12 months)
- Bajra/Pearl Millet (6-12 months)
- Jowar/Sorghum (6-12 months)
- Ragi/Finger Millet (6-12 months)

#### Pulses (High Trading Volume)
- Chana/Chickpea (12+ months)
- Tur/Arhar/Pigeon Pea (12+ months)
- Moong/Green Gram (12+ months)
- Urad/Black Gram (12+ months)
- Masoor/Red Lentil (12+ months)
- Rajma/Kidney Beans (12+ months)

#### Oilseeds (Major Trading Category)
- Soybean (6-12 months)
- Groundnut/Peanut (6-12 months)
- Mustard (12+ months)
- Sunflower (6-12 months)
- Sesame (12+ months)
- Safflower (12+ months)

#### Spices (High Value Trading)
- Turmeric (12+ months)
- Coriander Seeds (12+ months)
- Cumin (12+ months)
- Fennel (12+ months)
- Fenugreek (12+ months)
- Black Pepper (12+ months)
- Cardamom (12+ months)

#### Cash Crops
- Cotton (12+ months)
- Jute (12+ months)

### Exclude: Perishable Commodities
- Tomatoes, Potatoes, Onions (high volatility, short shelf life)
- Leafy vegetables (unsuitable for medium-term trading)
- Fresh fruits (perishable nature)

**Total Target Commodities: ~35-40** (down from current 61)

## Data Requirements

### Historical Data Depth
- **Minimum**: 6 months (180 days) continuous data
- **Optimal**: 12-24 months for seasonal pattern detection
- **Granularity**: Daily prices (modal, minimum, maximum)

### Data Points Per Commodity
- **Market Coverage**: 20-40 major mandis per commodity
- **Total Records Target**: ~250,000 price records
  - 35 commodities × 30 markets × 180 days = 189,000 records minimum

### Real-time Data Updates
- **Frequency**: 3 times daily (Morning 8 AM, Afternoon 2 PM, Evening 8 PM)
- **Sources**: Agmarknet, State agriculture portals
- **Fallback**: Previous day data with staleness indicator

## Technical Architecture Fixes

### Phase 1: Database Schema Fix (Priority: Critical)

#### Issue: Dictionary Data Not Saving
```python
# Problem: Raw dictionaries passed to SQLAlchemy
scraped_data = [{"commodity": "Wheat", "price": 2000, ...}]
session.add(scraped_data)  # Fails - dict not mapped to model
```

#### Solution: Proper ORM Mapping
```python
# Fix: Convert dict to MarketPrice model instances
from app.database.models import MarketPrice

for record in scraped_data:
    price_entry = MarketPrice(
        commodity_name=record["commodity"],
        market_name=record["market"],
        modal_price=record["modal_price"],
        date=record["date"],
        # ... map all fields
    )
    session.add(price_entry)
```

#### Implementation Steps
1. Update `app/services/scheduler.py:_store_scraped_data()` method
2. Add proper dict-to-model conversion logic
3. Add batch insert for performance (500 records per transaction)
4. Add error handling with partial save capability

### Phase 2: Model Retraining (Priority: Critical)

#### Issue: 29 vs 16 Feature Mismatch

**Current Model Features (29):**
- Preprocessor generates only 16 features
- Models trained on different feature set

**Solution: Align Features**

**Standard Feature Set (24 features):**
1. Price features (5): modal_price, min_price, max_price, price_range, price_volatility
2. Date features (3): day_of_year, month, day_of_week
3. Lag features (7): price_lag_1, price_lag_7, price_lag_14, rolling_mean_7, rolling_mean_30, rolling_std_7, rolling_std_30
4. Seasonal (2): is_festival_season, is_harvest_season
5. Market indicators (2): market_volume_index, supply_demand_ratio
6. Trend features (3): price_trend_7d, price_trend_30d, momentum
7. Encoded features (2): commodity_encoded, market_encoded

#### Retraining Process
```bash
# 1. Clear old models
rm data/models/*.joblib

# 2. Retrain with aligned features
python backend/scripts/train_aligned.py

# 3. Validate feature count
python -c "
import joblib
model = joblib.load('data/models/random_forest_latest.joblib')
print(f'Model expects: {model.n_features_in_} features')
"
```

### Phase 3: Data Collection Pipeline (Priority: High)

#### 6-Month Historical Data Scraping

```python
# New script: backend/scripts/collect_historical_data.py
import asyncio
from datetime import datetime, timedelta
from app.scraper.agmarknet_scraper import AgmarknetScraper
from app.services.data_storage import store_market_prices

async def collect_6_months_data():
    """Collect 180 days of historical data"""
    scraper = AgmarknetScraper()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Focus on trader commodities only
    trader_commodities = [
        "Wheat", "Rice", "Soybean", "Chana", "Tur", 
        "Maize", "Mustard", "Turmeric", "Cotton"
        # ... full list of 35 commodities
    ]
    
    all_data = []
    current_date = start_date
    
    while current_date <= end_date:
        print(f"Scraping data for {current_date.date()}")
        
        # Scrape weekly to avoid rate limiting
        weekly_data = await scraper.scrape_historical_data(
            start_date=current_date,
            end_date=current_date + timedelta(days=7),
            commodities=trader_commodities
        )
        
        all_data.extend(weekly_data)
        current_date += timedelta(days=7)
        
        # Be respectful to server
        await asyncio.sleep(5)
    
    # Store in database
    await store_market_prices(all_data)
    print(f"Collected {len(all_data)} historical records")

if __name__ == "__main__":
    asyncio.run(collect_6_months_data())
```

#### Execution Plan
```bash
# Run during off-peak hours
nohup python backend/scripts/collect_historical_data.py > logs/historical_collection.log 2>&1 &

# Monitor progress
tail -f logs/historical_collection.log
```

### Phase 4: Scheduled Daily Updates (Priority: Medium)

#### Fix Existing Scheduler
```python
# Update app/services/scheduler.py

class DataScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = AgmarknetScraper()
        
    async def daily_data_collection(self):
        """Collect today's market data"""
        try:
            # Only scrape trader-relevant commodities
            trader_commodities = load_commodity_config()
            
            data = await self.scraper.scrape_market_prices(
                commodities=trader_commodities,
                days=1
            )
            
            # FIX: Convert dict to ORM models
            saved_count = await self._store_scraped_data_fixed(data)
            
            logger.info(f"Stored {saved_count} new price records")
            
            # Update model if data crosses threshold
            if self._should_retrain():
                await self.retrain_models()
                
        except Exception as e:
            logger.error(f"Daily collection failed: {e}")
            # Alert admin
            send_alert_email(f"Data collection failed: {e}")
    
    async def _store_scraped_data_fixed(self, scraped_data: list[dict]):
        """Convert dicts to ORM models and save"""
        from app.database.models import MarketPrice
        from app.database.connection import get_async_session
        
        async with get_async_session() as session:
            records = []
            for data in scraped_data:
                record = MarketPrice(
                    commodity_name=data.get("commodity"),
                    market_name=data.get("market"),
                    modal_price=data.get("modal_price"),
                    min_price=data.get("min_price"),
                    max_price=data.get("max_price"),
                    date=data.get("date"),
                    # Add all required fields
                )
                records.append(record)
            
            # Batch insert
            session.add_all(records)
            await session.commit()
            
            return len(records)
```

## Feature Prioritization for Traders

### Must-Have Features (Phase 1)
1. ✅ Real-time price dashboard with auto-refresh
2. ✅ 7-day price forecasts with confidence intervals
3. ✅ Market comparison (arbitrage opportunities)
4. ✅ Historical price charts (6 months)
5. ✅ Buy/Sell signal alerts

### Important Features (Phase 2)
1. ✅ 30-day extended forecasts
2. ✅ Volatility indicators (ATR, Bollinger Bands)
3. ✅ Seasonal trend analysis
4. ✅ Market sentiment indicators
5. ✅ Export data (CSV, Excel)

### Nice-to-Have Features (Phase 3)
1. Weather impact predictions
2. News sentiment analysis
3. Crop condition reports
4. Government policy alerts
5. Price correlation matrix

## Implementation Roadmap

### Week 1: Critical Fixes
- **Day 1-2**: Fix database storage (dict to ORM conversion)
- **Day 3-4**: Retrain models with aligned features (29 or 16, consistent)
- **Day 5**: Test and validate predictions
- **Day 6-7**: Update commodity filter (remove perishables)

### Week 2: Data Collection
- **Day 1-3**: Run 6-month historical data collection
- **Day 4**: Validate data quality and completeness
- **Day 5**: Fix scheduler for daily updates
- **Day 6-7**: Test automated data pipeline

### Week 3: Model Improvement
- **Day 1-2**: Retrain on full 6-month dataset
- **Day 3-4**: Validate model accuracy (target: >80% for 7-day forecast)
- **Day 5**: Implement confidence intervals
- **Day 6-7**: Add volatility predictions

### Week 4: Frontend Refinement
- **Day 1-2**: Update dashboard for trader focus
- **Day 3-4**: Add professional charts (candlestick, volume)
- **Day 5**: Implement real-time updates
- **Day 6-7**: User testing and bug fixes

## Success Metrics

### Data Quality Metrics
- **Completeness**: >95% of expected daily records
- **Timeliness**: Data updated within 2 hours of market close
- **Accuracy**: <5% deviation from official sources

### Model Performance Metrics
- **7-day Forecast**: MAE < 3%, MAPE < 5%
- **30-day Forecast**: MAE < 8%, MAPE < 12%
- **Directional Accuracy**: >75% for price movement direction

### User Experience Metrics
- **Page Load**: <2 seconds
- **Data Freshness**: <3 hours old
- **Uptime**: >99.5%

## Risk Mitigation

### Data Source Failures
- **Backup Sources**: State agriculture portals, commodity exchanges
- **Fallback Strategy**: Use previous day data with clear indicators
- **Monitoring**: Alert system for failed scrapes

### Model Performance Degradation
- **Weekly Retraining**: Scheduled every Sunday
- **Performance Monitoring**: Track MAE, MAPE daily
- **A/B Testing**: Keep previous model version as fallback

### System Downtime
- **Database Backups**: Daily automated backups
- **Redundancy**: Multi-instance deployment
- **Health Checks**: Automated monitoring with alerts

## Final Checklist

### Before Production Release
- [ ] All 35 trader commodities configured
- [ ] 6 months historical data collected and validated
- [ ] Models retrained with correct features
- [ ] Daily scraping tested for 7 days
- [ ] Database storage verified (no dict errors)
- [ ] Dashboard shows current day data
- [ ] Prediction accuracy validated
- [ ] Load testing completed (100 concurrent users)
- [ ] Security audit passed
- [ ] Documentation updated

---

## Immediate Action Items (Today)

1. **Fix Database Storage** (2 hours)
   ```bash
   # Edit app/services/scheduler.py
   vim backend/app/services/scheduler.py
   # Implement _store_scraped_data_fixed() method
   ```

2. **Start Historical Data Collection** (4 hours setup, 24-48 hours runtime)
   ```bash
   python backend/scripts/collect_historical_data.py
   ```

3. **Model Retraining** (3 hours)
   ```bash
   python backend/scripts/train_aligned.py
   ```

4. **Update Commodity Filter** (1 hour)
   ```bash
   # Edit config file
   vim backend/app/config.py
   # Update TRADER_COMMODITIES list
   ```

**Estimated Total Time: 1-2 weeks for full implementation**

---

*Document Version: 1.0*  
*Last Updated: 2026-02-04*  
*Author: System Analysis*
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
