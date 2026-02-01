#!/usr/bin/env python3
"""
Simple training script - no grid search, single process, for quick model generation
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from app.ml.preprocessor import DataPreprocessor
import joblib


def generate_quick_data():
    """Generate realistic market data for fast training"""
    print("   • Generating realistic market data...")
    
    commodities = ["Wheat", "Rice", "Potato"]
    markets = ["Azadpur", "Mumbai (Dadar)"]
    
    records = []
    base_date = datetime.now() - timedelta(days=90)
    
    for day in range(90):
        current_date = base_date + timedelta(days=day)
        month = current_date.month
        
        for commodity in commodities:
            for market in markets:
                # Base prices vary by commodity
                base_prices = {"Wheat": 2400, "Rice": 3200, "Potato": 1800}
                base_price = base_prices.get(commodity, 2000)
                
                # Seasonal variation
                if month in [10, 11]:
                    base_price *= 0.85 if commodity == "Wheat" else 1.0
                
                # Random day-to-day noise
                noise = np.random.uniform(0.9, 1.1)
                final_price = base_price * noise
                
                records.append({
                    "date": current_date,
                    "commodity": commodity,
                    "market": market,
                    "price": final_price,
                    "arrival": int(500 + np.random.uniform(0, 5000)),
                })
    
    df = pd.DataFrame(records)
    print(f"   ✓ Generated {len(df)} data points")
    return df


def main():
    print("\n" + "="*70)
    print("🌾 AGRITECH: SIMPLE TRAINING (No Grid Search)")
    print("="*70 + "\n")
    
    print("📥 STEP 1: Preparing Market Data")
    print("-" * 70)
    
    df = generate_quick_data()
    print(f"   • Dataset shape: {df.shape}")
    print(f"   • Date range: {df['date'].min().date()} to {df['date'].max().date()}\n")
    
    print("📊 STEP 2: Preprocessing")
    print("-" * 70)
    
    preprocessor = DataPreprocessor()
    
    # Temporal features
    print("   • Extracting temporal features...")
    temporal_df = pd.DataFrame({
        'day': df['date'].dt.day,
        'month': df['date'].dt.month,
        'dayofweek': df['date'].dt.dayofweek,
        'quarter': df['date'].dt.quarter,
    })
    print(f"   ✓ Generated temporal features")
    
    # Encoding
    print("   • Encoding categorical features...")
    df_encoded = preprocessor.encode_categorical(df, ['commodity', 'market'], fit=True)
    print(f"   ✓ Encoding complete: {df_encoded.shape}\n")
    
    # Feature selection
    feature_cols = [col for col in df_encoded.columns 
                   if col not in ['price', 'date'] 
                   and df_encoded[col].dtype in [np.float64, np.int64]]
    
    X = df_encoded[feature_cols].fillna(0).values
    y = df_encoded['price'].values
    
    print(f"   • Features: {len(feature_cols)} | Samples: {len(y)}")
    print(f"   • Feature list: {', '.join(feature_cols[:4])}...\n")
    
    print("🤖 STEP 3: Training Simple Models (no grid search)")
    print("-" * 70)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {}
    results = {}
    
    # Model 1: Random Forest (simple)
    print("   • Training Random Forest...")
    rf = RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    r2_rf = r2_score(y_test, y_pred_rf)
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    models['random_forest'] = rf
    results['RandomForest'] = {'r2': r2_rf, 'mae': mae_rf}
    print(f"   ✓ R²={r2_rf:.3f} | MAE=₹{mae_rf:.0f}")
    
    # Model 2: Gradient Boosting (simple)
    print("   • Training Gradient Boosting...")
    gb = GradientBoostingRegressor(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    r2_gb = r2_score(y_test, y_pred_gb)
    mae_gb = mean_absolute_error(y_test, y_pred_gb)
    models['gradient_boosting'] = gb
    results['GradientBoosting'] = {'r2': r2_gb, 'mae': mae_gb}
    print(f"   ✓ R²={r2_gb:.3f} | MAE=₹{mae_gb:.0f}")
    
    # Model 3: Ridge Regression (simple)
    print("   • Training Ridge Regression...")
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train, y_train)
    y_pred_ridge = ridge.predict(X_test)
    r2_ridge = r2_score(y_test, y_pred_ridge)
    mae_ridge = mean_absolute_error(y_test, y_pred_ridge)
    models['ridge'] = ridge
    results['Ridge'] = {'r2': r2_ridge, 'mae': mae_ridge}
    print(f"   ✓ R²={r2_ridge:.3f} | MAE=₹{mae_ridge:.0f}\n")
    
    print("📈 STEP 4: Performance Summary")
    print("-" * 70)
    print(f"{'Model':<20} {'R² Score':<12} {'MAE (₹)':<12}")
    print("-" * 70)
    
    best_r2 = 0
    best_model_name = None
    
    for model_name, metrics in results.items():
        r2 = metrics['r2']
        mae = metrics['mae']
        print(f"{model_name:<20} {r2:>10.3f}  ₹{mae:>10.0f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = model_name
    
    print("-" * 70)
    print(f"🏆 Best Model: {best_model_name} (R²={best_r2:.3f})\n")
    
    print("💾 STEP 5: Saving Trained Models")
    print("-" * 70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = Path(project_root) / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save ensemble artifact
    model_path = model_dir / f"ensemble_{timestamp}.joblib"
    joblib.dump({
        'random_forest': models['random_forest'],
        'gradient_boosting': models['gradient_boosting'],
        'ridge': models['ridge'],
        'features': feature_cols,
        'timestamp': timestamp,
        'model_weights': {
            'random_forest': 0.4,
            'gradient_boosting': 0.4,
            'ridge': 0.2,
        }
    }, model_path)
    
    # Save preprocessor artifact
    preprocessor_path = model_dir / f"preprocessor_{timestamp}.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    
    print(f"   ✓ Ensemble artifact: {model_path.name}")
    print(f"   ✓ Preprocessor artifact: {preprocessor_path.name}\n")
    
    print("="*70)
    print("✅ TRAINING COMPLETE - READY FOR PREDICTIONS!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   • Trained on {len(df)} market records (90 days)")
    print(f"   • Best model: {best_model_name} (R²={best_r2:.3f})")
    print(f"   • Models ready in: {model_dir}\n")


if __name__ == "__main__":
    main()
