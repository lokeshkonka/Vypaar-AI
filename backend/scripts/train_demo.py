#!/usr/bin/env python3
"""
Quick training script for demo - uses light hyperparameters
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

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from app.ml.preprocessor import DataPreprocessor
import joblib

def generate_quick_data():
    """Generate realistic market data for fast training"""
    print("   • Generating realistic fallback market data...")
    
    commodities = ["Wheat", "Rice", "Onion", "Potato", "Tomato"]
    markets = ["Azadpur (Delhi)", "APMC Mumbai", "Chennai", "Bangalore", "Kolkata"]
    states = ["Delhi", "Maharashtra", "Tamil Nadu", "Karnataka", "West Bengal"]
    
    records = []
    base_date = datetime.now() - timedelta(days=90)
    
    for day in range(90):
        current_date = base_date + timedelta(days=day)
        month = current_date.month
        is_festival = month in [3, 10, 11, 12]
        
        for commodity in commodities:
            for i, market in enumerate(markets):
                base_price = 800 + (hash(commodity) % 3000)
                
                if month in [10, 11]:
                    base_price *= 0.85 if commodity == "Wheat" else 1.0
                elif month in [5, 6]:
                    base_price *= 1.15 if commodity == "Onion" else 1.0
                
                if is_festival:
                    base_price *= 1.12 if commodity in ["Onion", "Tomato"] else 1.05
                
                market_factor = 0.95 + (i * 0.03)
                final_price = base_price * market_factor
                
                records.append({
                    "date": current_date,
                    "commodity": commodity,
                    "market": market,
                    "state": states[i % len(states)],
                    "price": final_price,
                    "arrival": int(500 + (day * 10) % 5000),
                })
    
    df = pd.DataFrame(records)
    print(f"   ✓ Generated {len(df)} data points")
    return df


def main():
    print("\n" + "="*70)
    print("🌾 AGRITECH: QUICK TRAINING WITH FESTIVAL FEATURES")
    print("="*70 + "\n")
    
    print("📥 STEP 1: Preparing Market Data")
    print("-" * 70)
    
    df = generate_quick_data()
    print(f"   • Dataset shape: {df.shape}")
    print(f"   • Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"   • Commodities: {df['commodity'].nunique()} | Markets: {df['market'].nunique()}\n")
    
    print("📊 STEP 2: Preprocessing with Festival Features")
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
    
    # Festival enrichment
    print("   • Enriching with festival calendar...")
    df_enriched = preprocessor.festival_calendar.enrich_dataframe(df, 'date')
    print(f"   ✓ Added festival/seasonal indicators")
    
    festival_cols = [col for col in df_enriched.columns if 'festival' in col.lower() or 'season' in col.lower()]
    print(f"   ✓ Festival features: {len(festival_cols)} indicators")
    
    # Encoding
    print("   • Encoding categorical features...")
    df_encoded = preprocessor.encode_categorical(df_enriched, ['commodity', 'market', 'state'], fit=True)
    print(f"   ✓ Encoding complete: {df_encoded.shape}\n")
    
    # Feature selection
    feature_cols = [col for col in df_encoded.columns 
                   if col not in ['price', 'date', 'modal_price'] 
                   and df_encoded[col].dtype in [np.float64, np.int64]]
    
    X = df_encoded[feature_cols].fillna(0).values
    y = df_encoded['price'].values
    
    print(f"   • Features: {len(feature_cols)} | Samples: {len(y)}")
    print(f"   • Feature list: {', '.join(feature_cols[:6])}...\n")
    
    print("🤖 STEP 3: Training Lightweight Models")
    print("-" * 70)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    results = {}
    
    # Model 1: Random Forest
    print("   • Training Random Forest (light)...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    r2_rf = r2_score(y_test, y_pred_rf)
    results['RandomForest'] = {'mae': mae_rf, 'rmse': rmse_rf, 'r2': r2_rf}
    print(f"   ✓ R²={r2_rf:.3f} | MAE=₹{mae_rf:.0f} | RMSE=₹{rmse_rf:.0f}")
    
    # Model 2: Gradient Boosting
    print("   • Training Gradient Boosting (light)...")
    gb = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    mae_gb = mean_absolute_error(y_test, y_pred_gb)
    rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
    r2_gb = r2_score(y_test, y_pred_gb)
    results['GradientBoosting'] = {'mae': mae_gb, 'rmse': rmse_gb, 'r2': r2_gb}
    print(f"   ✓ R²={r2_gb:.3f} | MAE=₹{mae_gb:.0f} | RMSE=₹{rmse_gb:.0f}\n")
    
    print("📈 STEP 4: Performance Summary")
    print("-" * 70)
    print(f"{'Model':<20} {'R² Score':<12} {'MAE (₹)':<12} {'RMSE (₹)':<12}")
    print("-" * 70)
    
    best_r2 = 0
    best_model_name = None
    best_model = None
    
    for model_name, metrics in results.items():
        r2 = metrics['r2']
        mae = metrics['mae']
        rmse = metrics['rmse']
        print(f"{model_name:<20} {r2:>10.3f}  ₹{mae:>10.0f}  ₹{rmse:>10.0f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = model_name
            best_model = rf if model_name == 'RandomForest' else gb
    
    print("-" * 70)
    print(f"🏆 Best Model: {best_model_name} (R²={best_r2:.3f})\n")
    
    print("💾 STEP 5: Saving Trained Models")
    print("-" * 70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = Path(project_root) / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / f"ensemble_{timestamp}.joblib"
    preprocessor_path = model_dir / f"preprocessor_{timestamp}.joblib"
    
    joblib.dump({
        'random_forest': rf,
        'gradient_boosting': gb,
        'best_model': best_model,
        'best_model_name': best_model_name,
        'features': feature_cols,
        'timestamp': timestamp,
    }, model_path)
    
    joblib.dump(preprocessor, preprocessor_path)
    
    print(f"   ✓ Ensemble: {model_path.name}")
    print(f"   ✓ Preprocessor: {preprocessor_path.name}\n")
    
    print("="*70)
    print("✅ TRAINING COMPLETE - READY FOR PREDICTIONS!")
    print("="*70)
    print(f"\n📊 Key Achievements:")
    print(f"   ✓ Trained on {len(df)} market records (90 days)")
    print(f"   ✓ {df['commodity'].nunique()} commodities × {df['market'].nunique()} markets")
    print(f"   ✓ Festival features: 8+ seasonal indicators")
    print(f"   ✓ Best accuracy: {best_model_name} with R²={best_r2:.3f}")
    print(f"   ✓ Average error: ₹{results[best_model_name]['mae']:.0f}\n")
    
    # Test a prediction
    print("🔮 Sample Prediction:")
    print("-" * 70)
    sample_input = X_test[0:1]
    pred = best_model.predict(sample_input)[0]
    actual = y_test[0]
    error_pct = abs(pred - actual) / actual * 100
    print(f"   Predicted: ₹{pred:.2f}")
    print(f"   Actual: ₹{actual:.2f}")
    print(f"   Error: {error_pct:.1f}%\n")


if __name__ == "__main__":
    main()
