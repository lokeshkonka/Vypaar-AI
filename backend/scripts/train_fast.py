#!/usr/bin/env python3

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from app.ml.preprocessor import DataPreprocessor
from app.ml.trainer import ModelTrainer
from app.scraper.agmarknet_scraper import AgmarknetScraper

logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, format="<level>{message}</level>")

def generate_quick_data():

    print("   • Generating realistic fallback market data...")
    
    commodities = ["Wheat", "Rice", "Onion", "Potato", "Tomato", "Cabbage", "Cauliflower", "Soyabean"]
    markets = ["Azadpur (Delhi)", "APMC Mumbai", "Chennai", "Bangalore", "Kolkata", "Lucknow"]
    states = ["Delhi", "Maharashtra", "Tamil Nadu", "Karnataka", "West Bengal", "Uttar Pradesh"]
    
    records = []
    base_date = datetime.now() - timedelta(days=90)
    
    for day in range(90):
        current_date = base_date + timedelta(days=day)
        
        month = current_date.month
        is_festival = month in [3, 10, 11, 12]
        
        for commodity in commodities:
            for i, market in enumerate(markets):
                base_price = np.random.uniform(800, 4000)
                
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
                    "min_price": final_price * 0.92,
                    "max_price": final_price * 1.08,
                    "modal_price": final_price,
                    "arrival": int(np.random.uniform(500, 5000)),
                })
    
    df = pd.DataFrame(records)
    print(f"    Generated {len(df)} data points")
    return df

def main():
    print("\n" + "="*70)
    print("AGRITECH: QUICK TRAINING WITH FESTIVAL FEATURES (FAST MODE)")
    print("="*70 + "\n")
    
    print(" STEP 1: Preparing Market Data")
    print("-" * 70)
    
    df = generate_quick_data()
    print(f"   • Dataset shape: {df.shape}")
    print(f"   • Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"   • Commodities: {df['commodity'].nunique()}")
    print(f"   • Markets: {df['market'].nunique()}\n")
    
    print(" STEP 2: Preprocessing with Festival Features")
    print("-" * 70)
    
    preprocessor = DataPreprocessor()
    
    print("   • Extracting temporal features...")
    temporal_features = preprocessor.extract_temporal_features(df['date'])
    print(f"    Generated {temporal_features.shape[1]} temporal features")
    
    print("   • Enriching with festival calendar...")
    df_enriched = preprocessor.festival_calendar.enrich_dataframe(df, 'date')
    print(f"    Added festival/seasonal indicators")
    
    festival_cols = [col for col in df_enriched.columns if 'festival' in col.lower() or 'season' in col.lower()]
    print(f"    Festival features: {', '.join(festival_cols[:3])}")
    
    categorical_cols = ['commodity', 'market', 'state']
    print(f"   • Encoding {len(categorical_cols)} categorical features...")
    df_encoded = preprocessor.encode_categorical(df_enriched, categorical_cols, fit=True)
    print(f"    Dataset after encoding: {df_encoded.shape}\n")
    
    feature_cols = [col for col in df_encoded.columns 
                   if col not in ['price', 'date', 'min_price', 'max_price', 'modal_price', 'arrival']
                   and df_encoded[col].dtype in [np.float64, np.int64]]
    
    X = df_encoded[feature_cols].fillna(0).values
    y = df_encoded['price'].values
    
    print(f"   • Feature matrix: {X.shape}")
    print(f"   • Target values: {len(y)}")
    print(f"   • Feature names ({len(feature_cols)}): {', '.join(feature_cols[:8])}\n")
    
    print(" STEP 3: Training Ensemble Models")
    print("-" * 70)
    
    trainer = ModelTrainer(preprocessor)
    results = trainer.train_all_models(X, y)
    
    print("\n STEP 4: Model Performance Summary")
    print("-" * 70)
    print(f"{'Model':<18} {'Accuracy':<12} {'MAE (₹)':<12} {'RMSE (₹)':<12}")
    print("-" * 70)
    
    best_accuracy = 0
    best_model = None
    
    for model_name, result in results.items():
        metrics = result.get('metrics', {})
        accuracy = metrics.get('accuracy', 0)
        mae = metrics.get('mae', 0)
        rmse = metrics.get('rmse', 0)
        print(f"{model_name:<18} {accuracy:>10.2%}  ₹{mae:>10.2f}  ₹{rmse:>10.2f}")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model_name
    
    print("-" * 70)
    print(f" Best Model: {best_model} with {best_accuracy:.2%} accuracy\n")
    
    print(" STEP 5: Saving Trained Models")
    print("-" * 70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_paths = trainer.save_all_models(version=timestamp)
    preprocessor_path = trainer.save_preprocessor(version=timestamp)
    
    print(f"    Models saved with version: {timestamp}")
    for model_name, path in model_paths.items():
        if path:
            print(f"     • {model_name}: {Path(path).name}")
    print(f"    Preprocessor: {Path(preprocessor_path).name}\n")
    
    print("="*70)
    print(" TRAINING COMPLETE!")
    print("="*70)
    print(f"\n Summary:")
    print(f"   • Trained on {len(df)} market records (90 days)")
    print(f"   • Commodities: {df['commodity'].nunique()}, Markets: {df['market'].nunique()}")
    print(f"   • Festival features: {'yes' if festival_cols else 'no'}")
    print(f"   • Best model: {best_model} ({best_accuracy:.2%})")
    print(f"   • Ready for predictions!\n")

if __name__ == "__main__":
    main()
