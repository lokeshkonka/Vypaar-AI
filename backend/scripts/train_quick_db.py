#!/usr/bin/env python3
"""
Quick training script using database data with faster training options.
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

from app.database.connection import init_sync_db, get_sync_session
from app.database.models import MarketPrice
from app.ml.preprocessor import DataPreprocessor
from app.config import settings


def load_data_from_db():
    """Load price data from database."""
    print("📥 Loading data from database...")
    
    init_sync_db()
    session = next(get_sync_session())
    
    try:
        prices = session.query(MarketPrice).all()
        print(f"   ✓ Loaded {len(prices)} price records")
        
        data_list = []
        for price in prices:
            data_list.append({
                'date': price.date,
                'commodity_id': price.commodity_id,
                'market_id': price.market_id,
                'price': price.price,
                'min_price': price.min_price,
                'max_price': price.max_price,
                'modal_price': price.modal_price,
                'arrival': price.arrival or 0,
            })
        
        df = pd.DataFrame(data_list)
        return df
    finally:
        session.close()


def prepare_features(df: pd.DataFrame, preprocessor: DataPreprocessor):
    """Prepare features for training - must match prepare_prediction_data format."""
    print("📊 Preparing features...")
    
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Use preprocessor's temporal feature extraction for consistency
    temporal_features = preprocessor.extract_temporal_features(df['date'])
    
    # Merge temporal features
    for col in temporal_features.columns:
        df[col] = temporal_features[col].values
    
    # Enrich with festival calendar
    df_enriched = preprocessor.festival_calendar.enrich_dataframe(df, 'date')
    
    # Standard 16 features - must match prepare_prediction_data
    standard_features = [
        'commodity_id',      # 1
        'market_id',         # 2
        'arrival',           # 3
        'day_of_week',       # 4
        'month',             # 5
        'season',            # 6
        'is_festival',       # 7
        'festival_effect',   # 8
        'holiday_proximity', # 9
        'monsoon_factor',    # 10
        'harvest_season',    # 11
        'price',             # 12 - will be target, but include for feature alignment
        'week_of_year',      # 13
        'quarter',           # 14
        'month_sin',         # 15
        'month_cos',         # 16
    ]
    
    # Add missing columns with defaults
    for col in standard_features:
        if col not in df_enriched.columns:
            df_enriched[col] = 0.0
    
    # Ensure price column exists for feature alignment
    if 'price' not in df_enriched.columns:
        df_enriched['price'] = df_enriched.get('modal_price', 0)
    
    # Select features (exclude price from X but keep it for y)
    feature_cols = [c for c in standard_features if c != 'price']
    
    X = df_enriched[feature_cols].fillna(0).values
    y = df_enriched['price'].values
    
    # Store feature names in preprocessor (without price)
    preprocessor.feature_names = feature_cols
    
    print(f"   ✓ Feature matrix: {X.shape}")
    print(f"   ✓ Features: {', '.join(feature_cols[:8])}...")
    
    return X, y, feature_cols


def train_models(X_train, y_train, X_test, y_test):
    """Train simple but effective models."""
    print("\n🤖 Training models (simplified)...")
    
    models = {}
    metrics = {}
    
    # Random Forest - fast and effective
    print("   • Training RandomForest...")
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        n_jobs=-1,
        random_state=42
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    
    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
    rf_r2 = r2_score(y_test, rf_pred)
    
    models['random_forest'] = rf
    metrics['random_forest'] = {
        'mae': rf_mae,
        'rmse': rf_rmse,
        'r2': rf_r2,
        'accuracy': rf_r2
    }
    print(f"     ✓ RandomForest: R²={rf_r2:.4f}, MAE=₹{rf_mae:.2f}")
    
    # Gradient Boosting - also fast with limited iterations
    print("   • Training GradientBoosting...")
    gb = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1,
        min_samples_split=10,
        random_state=42
    )
    gb.fit(X_train, y_train)
    gb_pred = gb.predict(X_test)
    
    gb_mae = mean_absolute_error(y_test, gb_pred)
    gb_rmse = np.sqrt(mean_squared_error(y_test, gb_pred))
    gb_r2 = r2_score(y_test, gb_pred)
    
    models['gradient_boosting'] = gb
    metrics['gradient_boosting'] = {
        'mae': gb_mae,
        'rmse': gb_rmse,
        'r2': gb_r2,
        'accuracy': gb_r2
    }
    print(f"     ✓ GradientBoosting: R²={gb_r2:.4f}, MAE=₹{gb_mae:.2f}")
    
    return models, metrics


def save_models(models, preprocessor, metrics, feature_names):
    """Save trained models and preprocessor."""
    print("\n💾 Saving models...")
    
    model_dir = Path(settings.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save ensemble bundle
    ensemble_bundle = {
        **models,
        'feature_names': feature_names,
        'feature_count': len(feature_names),
        'timestamp': timestamp,
        'trained_on': timestamp,
        'metrics': metrics,
    }
    
    ensemble_path = model_dir / f"ensemble_{timestamp}.joblib"
    joblib.dump(ensemble_bundle, ensemble_path)
    print(f"   ✓ Ensemble saved: {ensemble_path.name}")
    
    # Save preprocessor
    preprocessor_path = model_dir / f"preprocessor_{timestamp}.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    print(f"   ✓ Preprocessor saved: {preprocessor_path.name}")
    
    return ensemble_path, preprocessor_path


def main():
    print("\n" + "="*70)
    print("AGRITECH: QUICK MODEL TRAINING")
    print("="*70 + "\n")
    
    # Load data
    df = load_data_from_db()
    
    if df.empty:
        print("❌ No data found in database!")
        print("   Run refresh_all_data.py first to seed data.")
        sys.exit(1)
    
    print(f"   • Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   • Commodities: {df['commodity_id'].nunique()}")
    print(f"   • Markets: {df['market_id'].nunique()}\n")
    
    # Prepare features
    preprocessor = DataPreprocessor()
    X, y, feature_names = prepare_features(df, preprocessor)
    
    # Split data (time-based)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"\n   • Train set: {len(X_train)} samples")
    print(f"   • Test set: {len(X_test)} samples")
    
    # Train models
    models, metrics = train_models(X_train, y_train, X_test, y_test)
    
    # Save models
    ensemble_path, preprocessor_path = save_models(
        models, preprocessor, metrics, feature_names
    )
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   • Trained on {len(df)} price records")
    print(f"   • Features: {len(feature_names)}")
    print(f"   • RandomForest R²: {metrics['random_forest']['r2']:.4f}")
    print(f"   • GradientBoosting R²: {metrics['gradient_boosting']['r2']:.4f}")
    print(f"   • Models saved with version: {datetime.now().strftime('%Y%m%d_%H%M%S')}\n")


if __name__ == "__main__":
    main()
