#!/usr/bin/env python3
"""
Quick training script using database data with simple models (no hyperparameter tuning).
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


def load_data_from_db(days=90):
    """Load data from database."""
    print("   • Loading data from database...")
    
    init_sync_db()
    session = next(get_sync_session())
    
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        prices = session.query(MarketPrice).filter(MarketPrice.date >= start_date).all()
        
        data_list = []
        for price in prices:
            price_val = price.price or 0
            min_price = price.min_price if price.min_price is not None else price_val * 0.9
            max_price = price.max_price if price.max_price is not None else price_val * 1.1
            modal_price = price.modal_price if price.modal_price is not None else price_val
            
            data_list.append({
                'date': price.date,
                'commodity_id': price.commodity_id,
                'market_id': price.market_id,
                'price': price_val,
                'min_price': min_price,
                'max_price': max_price,
                'modal_price': modal_price,
                'arrival': price.arrival or 0,
            })
        
        df = pd.DataFrame(data_list)
        print(f"   ✓ Loaded {len(df)} records from database")
        return df
    finally:
        session.close()


def prepare_features(df, preprocessor):
    """Prepare features for training."""
    print("   • Preparing features...")
    
    # Extract temporal features
    temporal = preprocessor.extract_temporal_features(df['date'])
    
    # Combine with numeric features
    numeric_cols = ['commodity_id', 'market_id', 'arrival', 'min_price', 'max_price', 'modal_price']
    features = df[numeric_cols].copy()
    features = pd.concat([features, temporal], axis=1)
    
    # Fill any NaN values
    features = features.fillna(features.mean())
    
    # Store feature names
    preprocessor.feature_names = features.columns.tolist()
    
    print(f"   ✓ Created {features.shape[1]} features")
    return features.values, df['price'].values


def train_simple_models(X, y, preprocessor):
    """Train simple models without hyperparameter tuning."""
    print("\n🤖 Training Models (Simple Mode - No Hyperparameter Tuning)")
    print("-" * 70)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"   • Train set: {len(X_train)} samples")
    print(f"   • Test set: {len(X_test)} samples")
    
    models = {}
    results = {}
    
    # Random Forest
    print("\n   Training Random Forest...")
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42
    )
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    models['random_forest'] = rf
    results['random_forest'] = {
        'mae': mean_absolute_error(y_test, y_pred_rf),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
        'r2': r2_score(y_test, y_pred_rf),
    }
    print(f"   ✓ Random Forest: MAE=₹{results['random_forest']['mae']:.2f}, R²={results['random_forest']['r2']:.4f}")
    
    # Gradient Boosting
    print("   Training Gradient Boosting...")
    gb = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    models['gradient_boosting'] = gb
    results['gradient_boosting'] = {
        'mae': mean_absolute_error(y_test, y_pred_gb),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
        'r2': r2_score(y_test, y_pred_gb),
    }
    print(f"   ✓ Gradient Boosting: MAE=₹{results['gradient_boosting']['mae']:.2f}, R²={results['gradient_boosting']['r2']:.4f}")
    
    return models, results


def save_models(models, preprocessor, results):
    """Save trained models."""
    print("\n💾 Saving Models")
    print("-" * 70)
    
    model_dir = Path(settings.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save ensemble bundle
    ensemble_data = {
        **models,
        'feature_count': len(preprocessor.feature_names),
        'features': preprocessor.feature_names,
        'timestamp': timestamp,
        'metrics': results,
    }
    
    ensemble_path = model_dir / f"ensemble_{timestamp}.joblib"
    joblib.dump(ensemble_data, ensemble_path)
    print(f"   ✓ Saved ensemble: {ensemble_path.name}")
    
    # Save preprocessor
    preprocessor_path = model_dir / f"preprocessor_{timestamp}.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    print(f"   ✓ Saved preprocessor: {preprocessor_path.name}")
    
    return ensemble_path, preprocessor_path


def main():
    print("\n" + "=" * 70)
    print("AGRITECH: QUICK MODEL TRAINING")
    print("=" * 70 + "\n")
    
    print("📥 STEP 1: Loading Data")
    print("-" * 70)
    df = load_data_from_db(days=90)
    
    if len(df) == 0:
        print("❌ No data found. Please run seed_extended.py first.")
        return
    
    print(f"   • Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   • Commodities: {df['commodity_id'].nunique()}")
    print(f"   • Markets: {df['market_id'].nunique()}")
    
    print("\n📊 STEP 2: Feature Engineering")
    print("-" * 70)
    preprocessor = DataPreprocessor()
    X, y = prepare_features(df, preprocessor)
    print(f"   • Feature matrix: {X.shape}")
    print(f"   • Target values: {len(y)}")
    
    # Train models
    models, results = train_simple_models(X, y, preprocessor)
    
    # Save models
    ensemble_path, preprocessor_path = save_models(models, preprocessor, results)
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   • Trained on {len(df)} market records")
    print(f"   • Features: {X.shape[1]}")
    print(f"   • Models: {list(models.keys())}")
    
    best_model = min(results, key=lambda k: results[k]['mae'])
    print(f"   • Best model: {best_model} (MAE=₹{results[best_model]['mae']:.2f})")
    print(f"   • Ready for predictions!\n")


if __name__ == "__main__":
    main()
