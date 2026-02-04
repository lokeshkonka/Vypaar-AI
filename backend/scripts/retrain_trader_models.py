import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from datetime import datetime, timedelta
from loguru import logger

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_async_session, get_sync_session
from app.database.models import MarketPrice, Commodity, Market
from app.ml.preprocessor import DataPreprocessor
from app.ml.trainer import ModelTrainer
from app.ml.ensemble import EnsembleManager
import pandas as pd
import numpy as np
import joblib


TRADER_COMMODITIES = [
    'Wheat', 'Rice', 'Maize', 'Barley',
    'Soybean', 'Chickpea', 'Pigeon Pea', 'Lentil',
    'Green Gram', 'Black Gram', 'Kidney Bean',
    'Mustard', 'Groundnut', 'Sunflower', 'Sesame',
    'Cotton', 'Jute'
]


async def fetch_training_data():
    logger.info("Fetching historical price data for trader commodities")
    
    async for session in get_async_session():
        result = await session.execute(
            select(MarketPrice, Commodity.name, Market.name)
            .join(Commodity, MarketPrice.commodity_id == Commodity.id)
            .join(Market, MarketPrice.market_id == Market.id)
            .where(Commodity.name.in_(TRADER_COMMODITIES))
            .order_by(MarketPrice.date.desc())
        )
        
        records = result.all()
        
        if not records:
            logger.warning("No data found for trader commodities")
            return pd.DataFrame()
        
        data = []
        for price, commodity_name, market_name in records:
            data.append({
                'date': price.date,
                'commodity': commodity_name,
                'commodity_id': price.commodity_id,
                'market': market_name,
                'market_id': price.market_id,
                'price': price.modal_price or price.price,
                'min_price': price.min_price,
                'max_price': price.max_price,
                'arrival': price.arrival or 100.0,
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Fetched {len(df)} price records for {df['commodity'].nunique()} commodities")
        
        return df


async def train_models():
    logger.info("Starting model retraining with 29 features for trader commodities")
    
    df = await fetch_training_data()
    
    if df.empty:
        logger.error("No training data available")
        return False
    
    logger.info(f"Training data shape: {df.shape}")
    logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    logger.info(f"Commodities: {df['commodity'].unique().tolist()}")
    
    preprocessor = DataPreprocessor(scaler_type="standard")
    
    try:
        features, target = preprocessor.prepare_training_data(
            data=df,
            numeric_cols=['price', 'min_price', 'max_price', 'arrival', 'commodity_id', 'market_id'],
            categorical_cols=None,
            date_col='date',
            target_col='price',
            handle_missing=True,
            handle_outliers_=True
        )
        
        logger.info(f"Prepared training data: {features.shape[0]} samples, {features.shape[1]} features")
        logger.info(f"Feature names ({len(preprocessor.feature_names)}): {preprocessor.feature_names[:15]}...")
        
        if features.shape[1] < 29:
            logger.warning(f"Expected at least 29 features but got {features.shape[1]}")
        
        train_size = int(0.8 * len(features))
        X_train, X_test = features[:train_size], features[train_size:]
        y_train, y_test = target[:train_size], target[train_size:]
        
        logger.info(f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples")
        
        models = {}
        
        logger.info("Training Random Forest...")
        from sklearn.ensemble import RandomForestRegressor
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        rf_score = rf_model.score(X_test, y_test)
        models['random_forest'] = rf_model
        logger.info(f"Random Forest R² score: {rf_score:.4f}")
        
        logger.info("Training Gradient Boosting...")
        from sklearn.ensemble import GradientBoostingRegressor
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        gb_model.fit(X_train, y_train)
        gb_score = gb_model.score(X_test, y_test)
        models['gradient_boosting'] = gb_model
        logger.info(f"Gradient Boosting R² score: {gb_score:.4f}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = Path(__file__).parent.parent / "data" / "models"
        model_dir.mkdir(exist_ok=True, parents=True)
        
        ensemble_data = {
            'random_forest': models['random_forest'],
            'gradient_boosting': models['gradient_boosting'],
            'model_weights': {
                'random_forest': 0.5,
                'gradient_boosting': 0.5
            },
            'feature_names': preprocessor.feature_names,
            'n_features': features.shape[1],
            'timestamp': timestamp,
            'rf_score': rf_score,
            'gb_score': gb_score
        }
        
        model_path = model_dir / f"ensemble_{timestamp}.joblib"
        preprocessor_path = model_dir / f"preprocessor_{timestamp}.joblib"
        
        joblib.dump(ensemble_data, str(model_path))
        joblib.dump(preprocessor, str(preprocessor_path))
        
        logger.success(f"Models trained and saved successfully with {features.shape[1]} features")
        logger.info(f"Model: {model_path}")
        logger.info(f"Preprocessor: {preprocessor_path}")
        logger.info(f"Random Forest score: {rf_score:.4f}")
        logger.info(f"Gradient Boosting score: {gb_score:.4f}")
        
        test_predictions_rf = rf_model.predict(X_test[:5])
        test_predictions_gb = gb_model.predict(X_test[:5])
        logger.info(f"Sample RF predictions: {test_predictions_rf}")
        logger.info(f"Sample GB predictions: {test_predictions_gb}")
        logger.info(f"Actual values: {y_test[:5]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Trader-Focused Model Retraining with Enhanced Features")
    logger.info("=" * 80)
    
    success = asyncio.run(train_models())
    
    if success:
        logger.success("Training completed successfully")
    else:
        logger.error("Training failed")
        sys.exit(1)
