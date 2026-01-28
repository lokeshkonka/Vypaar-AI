#!/usr/bin/env python3
"""
Complete retraining and seeding script for full API integration
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import warnings
warnings.filterwarnings('ignore')

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from app.ml.preprocessor import DataPreprocessor
from app.database.connection import init_sync_db, get_sync_session
from app.database.models import Base, Commodity, Market, MarketPrice
from sqlalchemy.orm import Session
import joblib


def generate_training_data():
    """Generate 90 days of realistic market data"""
    print("   • Generating training dataset (90 days)...")
    
    commodities = ["Wheat", "Rice", "Onion", "Potato", "Tomato", "Cabbage"]
    markets = ["Azadpur (Delhi)", "APMC Mumbai", "Chennai Central", "Bangalore City"]
    states = ["Delhi", "Maharashtra", "Tamil Nadu", "Karnataka"]
    
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
    print(f"   ✓ Generated {len(df)} training records")
    return df


def seed_database():
    """Seed database with commodities and markets"""
    print("\n📦 SEEDING DATABASE")
    print("-" * 70)
    
    init_sync_db()
    session = next(get_sync_session())
    
    try:
        # Check if already seeded
        existing_commodities = session.query(Commodity).count()
        if existing_commodities > 0:
            print(f"   ✓ Database already seeded with {existing_commodities} commodities")
            return
        
        print("   • Adding commodities...")
        commodities_data = [
            ("Wheat", "Cereals", "kg"),
            ("Rice", "Cereals", "kg"),
            ("Onion", "Vegetables", "kg"),
            ("Potato", "Vegetables", "kg"),
            ("Tomato", "Vegetables", "kg"),
            ("Cabbage", "Vegetables", "kg"),
        ]
        
        commodities = []
        for name, category, unit in commodities_data:
            comm = Commodity(name=name, category=category, unit=unit)
            session.add(comm)
            commodities.append(comm)
        
        session.flush()
        print(f"   ✓ Added {len(commodities)} commodities")
        
        print("   • Adding markets...")
        markets_data = [
            ("Azadpur (Delhi)", "Delhi"),
            ("APMC Mumbai", "Maharashtra"),
            ("Chennai Central", "Tamil Nadu"),
            ("Bangalore City", "Karnataka"),
        ]
        
        markets = []
        for name, state in markets_data:
            market = Market(name=name, state=state, location="Primary")
            session.add(market)
            markets.append(market)
        
        session.flush()
        print(f"   ✓ Added {len(markets)} markets")
        
        # Add some market prices
        print("   • Seeding initial market prices...")
        base_date = datetime.now() - timedelta(days=7)
        
        price_count = 0
        for day_offset in range(7):
            date = base_date + timedelta(days=day_offset)
            for commodity in commodities:
                for market in markets:
                    price = MarketPrice(
                        commodity_id=commodity.id,
                        market_id=market.id,
                        date=date.date(),
                        price=2000 + np.random.randint(-500, 500),
                        min_price=1800,
                        max_price=2200,
                        modal_price=2000,
                        arrival=int(1000 + np.random.randint(0, 4000)),
                    )
                    session.add(price)
                    price_count += 1
        
        session.commit()
        print(f"   ✓ Added {price_count} market prices\n")
        
    finally:
        session.close()


def train_and_export_models():
    """Train models with proper preprocessing and export"""
    print("🤖 TRAINING MODELS")
    print("-" * 70)
    
    # Generate training data
    df = generate_training_data()
    
    # Preprocess
    print("   • Preprocessing with festival features...")
    preprocessor = DataPreprocessor()
    
    # Temporal features
    temporal_df = pd.DataFrame({
        'day': df['date'].dt.day,
        'month': df['date'].dt.month,
        'dayofweek': df['date'].dt.dayofweek,
        'quarter': df['date'].dt.quarter,
    })
    
    # Festival enrichment
    df_enriched = preprocessor.festival_calendar.enrich_dataframe(df, 'date')
    
    # Encoding
    df_encoded = preprocessor.encode_categorical(
        df_enriched, ['commodity', 'market', 'state'], fit=True
    )
    
    # Get features
    feature_cols = [col for col in df_encoded.columns 
                   if col not in ['price', 'date', 'modal_price'] 
                   and df_encoded[col].dtype in [np.float64, np.int64]]
    
    X = df_encoded[feature_cols].fillna(0).values
    y = df_encoded['price'].values
    
    print(f"   ✓ Feature set: {len(feature_cols)} features")
    print(f"   ✓ Feature names: {', '.join(feature_cols[:8])}...")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"   ✓ Training set: {len(X_train)} samples | Test set: {len(X_test)} samples\n")
    
    # Train models
    print("   • Training Random Forest...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    r2_rf = r2_score(y_test, y_pred_rf)
    print(f"   ✓ R²={r2_rf:.3f} | MAE=₹{mae_rf:.0f} | RMSE=₹{rmse_rf:.0f}")
    
    print("   • Training Gradient Boosting...")
    gb = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    mae_gb = mean_absolute_error(y_test, y_pred_gb)
    rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
    r2_gb = r2_score(y_test, y_pred_gb)
    print(f"   ✓ R²={r2_gb:.3f} | MAE=₹{mae_gb:.0f} | RMSE=₹{rmse_gb:.0f}\n")
    
    # Select best model
    best_r2 = max(r2_rf, r2_gb)
    best_model = rf if r2_rf >= r2_gb else gb
    best_name = "RandomForest" if r2_rf >= r2_gb else "GradientBoosting"
    
    print(f"📊 PERFORMANCE SUMMARY")
    print("-" * 70)
    print(f"{'Model':<20} {'R² Score':<12} {'MAE (₹)':<12} {'RMSE (₹)':<12}")
    print("-" * 70)
    print(f"{'RandomForest':<20} {r2_rf:>10.3f}  ₹{mae_rf:>10.0f}  ₹{rmse_rf:>10.0f}")
    print(f"{'GradientBoosting':<20} {r2_gb:>10.3f}  ₹{mae_gb:>10.0f}  ₹{rmse_gb:>10.0f}")
    print("-" * 70)
    print(f"🏆 Best Model: {best_name} (R²={best_r2:.3f})\n")
    
    # Save models
    print("💾 SAVING MODELS")
    print("-" * 70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = Path(project_root) / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual models
    rf_path = model_dir / f"random_forest_{timestamp}.joblib"
    gb_path = model_dir / f"gradient_boosting_{timestamp}.joblib"
    
    joblib.dump(rf, rf_path)
    joblib.dump(gb, gb_path)
    
    print(f"   ✓ RandomForest: {rf_path.name}")
    print(f"   ✓ GradientBoosting: {gb_path.name}")
    
    # Save ensemble
    ensemble_data = {
        'random_forest': rf,
        'gradient_boosting': gb,
        'best_model': best_model,
        'best_model_name': best_name,
        'features': feature_cols,
        'feature_count': len(feature_cols),
        'timestamp': timestamp,
        'metrics': {
            'random_forest': {'r2': r2_rf, 'mae': mae_rf, 'rmse': rmse_rf},
            'gradient_boosting': {'r2': r2_gb, 'mae': mae_gb, 'rmse': rmse_gb},
        }
    }
    
    ensemble_path = model_dir / f"ensemble_{timestamp}.joblib"
    joblib.dump(ensemble_data, ensemble_path)
    print(f"   ✓ Ensemble: {ensemble_path.name}")
    
    # Save preprocessor with feature list
    preprocessor_data = {
        'preprocessor': preprocessor,
        'feature_cols': feature_cols,
        'feature_count': len(feature_cols),
        'timestamp': timestamp,
    }
    
    preprocessor_path = model_dir / f"preprocessor_{timestamp}.joblib"
    joblib.dump(preprocessor_data, preprocessor_path)
    print(f"   ✓ Preprocessor: {preprocessor_path.name}\n")
    
    return {
        'models': {
            'random_forest': str(rf_path),
            'gradient_boosting': str(gb_path),
        },
        'ensemble': str(ensemble_path),
        'preprocessor': str(preprocessor_path),
        'feature_cols': feature_cols,
        'feature_count': len(feature_cols),
    }


def main():
    print("\n" + "="*70)
    print("🌾 AGRITECH: COMPLETE RETRAINING & SEEDING PIPELINE")
    print("="*70 + "\n")
    
    try:
        # Seed database
        seed_database()
        
        # Train and export models
        result = train_and_export_models()
        
        print("="*70)
        print("✅ COMPLETE: MODELS TRAINED & SEEDED!")
        print("="*70)
        print(f"\n📝 Summary:")
        print(f"   ✓ Database seeded with commodities, markets, prices")
        print(f"   ✓ Models trained on 90-day festival-enriched data")
        print(f"   ✓ Feature set: {result['feature_count']} features")
        print(f"   ✓ All models saved to data/models/")
        print(f"\n🚀 Ready to test API predictions!\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
