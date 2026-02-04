# Critical Fixes Applied - Feb 4, 2026

## 1. ✅ FIXED: Database Duplicate Error
**Error:** `Multiple rows were found when one or none was required`

**Solution:**
- Changed `scalar_one_or_none()` to `scalars().first()` in:
  - `CommodityRepository.get_by_name()`
  - `MarketRepository.get_by_name()`

## 2. ✅ FIXED: Extended Forecast Ranges  
Added support for 3-month and 6-month forecasts:
- 7 days (1 week)
- 14 days (2 weeks)
- 30 days (1 month) ← NEW
- 90 days (3 months) ← NEW  
- 180 days (6 months) ← NEW

## 3. ⏳ TODO: Remove Hardcoded Data

### Backend Hardcoded Values to Remove:

**File: `/backend/app/api/frontend.py`**

Lines 145-152 - Hardcoded daily variations and fallback pricing:
```python
daily_variations = [1.02, 1.08, 0.98, 1.12, 1.05, 0.96, 0.92]  # REMOVE
# Replace with model predictions only, no fallbacks
```

Lines 298-299 - Hardcoded traditional accuracy:
```python
traditional_accuracy = max(50.0, ai_accuracy - 14.5)  # REMOVE
# Calculate from actual historical data
```

Lines 290-296 - Fallback model metrics:
```python
ai_accuracy = float(ensemble_metrics.get("accuracy", 0.85) * 100)  # REMOVE defaults
mae = float(ensemble_metrics.get("mae", 12.0))  # REMOVE defaults
# Use only real metrics, raise error if missing
```

## 4. ⏳ TODO: Add 13 Features (16 → 29)

Current features in preprocessor: 16  
Required features: 29  
Missing: 13

### Suggested New Features:
1. **Rolling Statistics** (3 features)
   - `price_ma_7` - 7-day moving average
   - `price_ma_30` - 30-day moving average
   - `price_std_14` - 14-day rolling std dev

2. **Volatility Metrics** (2 features)
   - `price_volatility` - Price volatility score
   - `arrival_volatility` - Supply volatility

3. **Seasonal Features** (3 features)
   - `quarter` - Quarter of year (1-4)
   - `month_encoded` - Cyclical month encoding
   - `season_score` - Agricultural season indicator

4. **Market Features** (2 features)
   - `market_tier` - Market importance rank
   - `state_encoded` - State location encoding

5. **Price Momentum** (3 features)
   - `price_change_pct` - % change from previous day
   - `price_trend_7d` - 7-day trend direction
   - `price_percentile` - Current price vs historical percentile

## 5. ⏳ TODO: Verify Real Data Usage

### Check These Components:

**Festival Impact:**
- File: `/backend/app/core/festival_calendar.py`
- Verify: Indian festival dates are accurate
- Verify: Impact calculations use historical data

**Market Trends:**
- Files: `/backend/app/api/v1/endpoints/buysell_alerts.py`
- Verify: Buy/sell signals calculated from real data
- Verify: No dummy trend data

**Demand Forecast:**
- Verify: Forecast vs past sales uses real historical comparison
- Remove any placeholder data

## 6. Model Retraining Required

**Steps:**
1. Scrape 6 months historical data (not just 30 days)
2. Focus on trader commodities:
   - Grains: Wheat, Rice, Maize, Barley
   - Pulses: Chickpea, Lentil, Pigeon Pea
   - Oilseeds: Mustard, Soybean, Groundnut
3. Update preprocessor with 13 new features
4. Train models with 29 features total
5. Validate on recent data
6. Store real metrics in database

**Command to run:**
```bash
cd backend
python scripts/train_models.py --months 6 --features 29
```

## Testing Checklist

- [ ] No duplicate errors when scraping
- [ ] Forecasts work for 30, 90, 180 days
- [ ] Model accuracy shows real metrics (not 0.85, 12.0)
- [ ] No hardcoded fallback pricing
- [ ] Festival impact reflects real data
- [ ] Buy/sell alerts based on real trends
- [ ] Models use 29 features
- [ ] 6 months of data in database

## Success Criteria

✅ Database storage fixed  
✅ Extended forecast ranges  
⏳ All hardcoded data removed  
⏳ Real model metrics only  
⏳ 29 features implemented  
⏳ Models retrained on 6-month data  
⏳ No dummy data anywhere  

---

**Priority Order:**
1. Remove hardcoded pricing/accuracy (HIGH - affects trust)
2. Add 13 features to models (HIGH - model performance)
3. Retrain with 6-month data (HIGH - accuracy)
4. Verify all real data (MEDIUM - validation)
