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
