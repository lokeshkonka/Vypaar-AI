# Model Retraining Guide

## Current Status
- ✅ Database query fixed (no more duplicate row errors)
- ✅ Features increased from 16 to 29
- ⏳ Need to retrain models with new data and features

## Quick Retrain

```bash
cd /home/vishal/code/Vypaar-AI/backend
python scripts/retrain_with_new_features.py
```

## Manual Retrain (if needed)

```bash
cd /home/vishal/code/Vypaar-AI/backend
python scripts/train_models.py
```

## What Happens During Retraining

1. **Data Collection** (180 days)
   - Fetches historical prices from database
   - Applies new 29-feature preprocessing
   - Splits into train/test (80/20)

2. **Model Training**
   - Random Forest Regressor
   - Gradient Boosting Regressor
   - Both trained with 29 input features

3. **Model Saving**
   - Saves to: `data/models/ensemble_YYYYMMDD_HHMMSS.joblib`
   - Saves preprocessor: `data/models/preprocessor_YYYYMMDD_HHMMSS.joblib`
   - Records metrics in database

## Expected Training Time
- Data loading: ~5-10 seconds
- Feature engineering: ~10-15 seconds
- Model training: ~30-60 seconds
- Total: ~1-2 minutes

## Verification After Training

1. **Check Logs**
   ```
   Loaded X samples for training
   Training random_forest model
   Training gradient_boosting model
   Models saved successfully
   ```

2. **Test Prediction**
   ```bash
   cd backend
   python -c "
   from app.api.dependencies import get_predictor
   predictor = get_predictor()
   print('Models loaded:', len(predictor.ensemble.models))
   "
   ```

3. **Check Feature Count**
   - Should see: `Prepared prediction data: shape=(X, 29), features=29`
   - No more "X has 16 features, but expecting 29" errors

## Troubleshooting

### Error: "Not enough data"
- Run scraper first to collect 6 months of data
- Check database has sufficient records

### Error: "Feature mismatch"
- Delete old models: `rm -rf data/models/*`
- Retrain from scratch

### Error: "Database connection"
- Ensure database exists: `ls -la data/agritech.db`
- Re-run migrations if needed

## After Successful Training

1. Restart backend server
2. Check forecasts work
3. Verify all 29 features appear in logs
4. Test predictions for different commodities

## Automated Retraining

The scheduler automatically retrains models:
- **Weekly:** Sunday at 3:00 AM
- **Manual:** Via `/api/model/retrain` endpoint (admin only)
