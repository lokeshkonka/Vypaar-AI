#!/usr/bin/env python3
"""
Training script that uses aligned features with prediction.
Generates exactly 29 features matching prepare_prediction_data.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.ml.preprocessor import DataPreprocessor
from app.config import settings
from app.database.connection import init_sync_db, get_sync_session
from app.database.models import MarketPrice

logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, format="<level>{message}</level>")

# Standard 29 features matching prepare_prediction_data
STANDARD_FEATURES = [
    'commodity_id', 'market_id', 'arrival', 'min_price', 'max_price', 'modal_price',
    'day_of_week', 'day_of_month', 'month', 'quarter', 'week_of_year', 'day_of_year', 'season',
    'month_sin', 'month_cos', 'day_sin', 'day_cos',
    'is_festival', 'festival_proximity', 'is_harvest_season', 'season_type', 'is_weekend',
    'is_month_end', 'is_month_start', 'is_sowing_period', 'is_harvest_period',
    'is_procurement_period', 'is_festival_week', 'is_major_festival'
]


def load_data_from_db(days: int = 365) -> pd.DataFrame:
    """Load market price data from database."""
    print(f"   • Loading data from database (last {days} days)...")
    
    init_sync_db()
    session = next(get_sync_session())
    
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        prices = session.query(MarketPrice).filter(
            MarketPrice.date >= start_date
        ).order_by(MarketPrice.date).all()
        
        data_list = []
        for price in prices:
            data_list.append({
                'date': price.date,
                'commodity_id': price.commodity_id,
                'market_id': price.market_id,
                'price': price.price,
                'min_price': price.min_price or price.price * 0.9,
                'max_price': price.max_price or price.price * 1.1,
                'modal_price': price.modal_price or price.price,
                'arrival': price.arrival or 0,
            })
        
        df = pd.DataFrame(data_list)
        print(f"   ✓ Loaded {len(df)} records from database")
        return df
    finally:
        session.close()


def prepare_features(df: pd.DataFrame, preprocessor: DataPreprocessor) -> pd.DataFrame:
    """Prepare features matching prepare_prediction_data (29 features)."""
    
    # Extract temporal features
    temporal_features = preprocessor.extract_temporal_features(df['date'])
    
    # Build features dataframe
    features = pd.DataFrame()
    
    # Add numeric columns
    for col in ['commodity_id', 'market_id', 'arrival', 'min_price', 'max_price', 'modal_price']:
        if col in df.columns:
            features[col] = df[col]
        else:
            features[col] = 0.0
    
    # Add temporal/festival features
    features = pd.concat([features.reset_index(drop=True), temporal_features.reset_index(drop=True)], axis=1)
    
    # Ensure all standard features exist
    for col in STANDARD_FEATURES:
        if col not in features.columns:
            features[col] = 0.0
    
    # Select only standard features in order
    features = features[STANDARD_FEATURES].copy()
    
    # Handle missing values
    features = features.fillna(features.mean(numeric_only=True))
    features = features.fillna(0.0)
    
    return features


def main():
    print("\n" + "="*70)
    print("AGRITECH: ALIGNED MODEL TRAINING (29 FEATURES)")
    print("="*70 + "\n")
    
    print("📥 STEP 1: Loading Market Data")
    print("-" * 70)
    
    df = load_data_from_db(days=365)
    
    if len(df) == 0:
        print("   ❌ No data in database!")
        return
    
    print(f"   • Dataset shape: {df.shape}")
    print(f"   • Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   • Commodities: {df['commodity_id'].nunique()}")
    print(f"   • Markets: {df['market_id'].nunique()}\n")
    
    print("📊 STEP 2: Preparing Features (29 aligned features)")
    print("-" * 70)
    
    preprocessor = DataPreprocessor()
    features_df = prepare_features(df, preprocessor)
    
    X = features_df.values.astype(np.float64)
    y = df['price'].values.astype(np.float64)
    
    # Remove rows with NaN
    valid_idx = ~(np.isnan(X).any(axis=1) | np.isnan(y))
    X = X[valid_idx]
    y = y[valid_idx]
    
    print(f"   ✓ Feature matrix: {X.shape}")
    print(f"   ✓ Target values: {len(y)}")
    print(f"   ✓ Features: {STANDARD_FEATURES[:5]}... ({len(STANDARD_FEATURES)} total)\n")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("🤖 STEP 3: Training Ensemble Models")
    print("-" * 70)
    
    models = {}
    metrics = {}
    
    # Random Forest
    print("   • Training Random Forest...")
    rf = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    metrics['random_forest'] = {
        'mae': mean_absolute_error(y_test, y_pred_rf),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
        'r2': r2_score(y_test, y_pred_rf)
    }
    models['random_forest'] = rf
    print(f"   ✓ Random Forest: MAE=₹{metrics['random_forest']['mae']:.2f}, R²={metrics['random_forest']['r2']:.4f}")
    
    # Gradient Boosting
    print("   • Training Gradient Boosting...")
    gb = GradientBoostingRegressor(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42)
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    metrics['gradient_boosting'] = {
        'mae': mean_absolute_error(y_test, y_pred_gb),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
        'r2': r2_score(y_test, y_pred_gb)
    }
    models['gradient_boosting'] = gb
    print(f"   ✓ Gradient Boosting: MAE=₹{metrics['gradient_boosting']['mae']:.2f}, R²={metrics['gradient_boosting']['r2']:.4f}\n")
    
    print("📈 STEP 4: Model Performance Summary")
    print("-" * 70)
    print(f"{'Model':<20} {'MAE (₹)':<15} {'RMSE (₹)':<15} {'R² Score':<12}")
    print("-" * 70)
    
    best_model_name = None
    best_rmse = float('inf')
    
    for model_name, m in metrics.items():
        print(f"{model_name:<20} ₹{m['mae']:>12.2f}  ₹{m['rmse']:>12.2f}  {m['r2']:>10.4f}")
        if m['rmse'] < best_rmse:
            best_rmse = m['rmse']
            best_model_name = model_name
    
    print("-" * 70)
    print(f"🏆 Best Model: {best_model_name}\n")
    
    print("💾 STEP 5: Saving Trained Models")
    print("-" * 70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = Path(settings.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save ensemble bundle
    ensemble_bundle = {
        'random_forest': models['random_forest'],
        'gradient_boosting': models['gradient_boosting'],
        'best_model': models[best_model_name],
        'best_model_name': best_model_name,
        'features': STANDARD_FEATURES,
        'feature_count': len(STANDARD_FEATURES),
        'timestamp': timestamp,
        'metrics': metrics,
    }
    
    ensemble_path = model_dir / f"ensemble_{timestamp}.joblib"
    joblib.dump(ensemble_bundle, ensemble_path)
    print(f"   ✓ Ensemble saved: {ensemble_path.name}")
    
    # Save preprocessor with feature names
    preprocessor.feature_names = STANDARD_FEATURES
    preprocessor_path = model_dir / f"preprocessor_{timestamp}.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    print(f"   ✓ Preprocessor saved: {preprocessor_path.name}\n")
    
    print("="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   • Trained on {len(df)} market records")
    print(f"   • Features: {len(STANDARD_FEATURES)} aligned features")
    print(f"   • Best model: {best_model_name} (RMSE: ₹{best_rmse:.2f})")
    print(f"   • Models ready for predictions!\n")


if __name__ == "__main__":
    main()
