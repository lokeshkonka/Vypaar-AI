#!/usr/bin/env python3

import sys
from pathlib import Path
import pandas as pd
import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from app.scraper.agmarknet_scraper import AgmarknetScraper
from app.ml.preprocessor import DataPreprocessor
from app.ml.trainer import ModelTrainer
from app.ml.ensemble import EnsembleManager
from datetime import datetime

logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, format="<level>{message}</level>")

def main():
    print("\n" + "="*70)
    print("AGRITECH: COMPREHENSIVE MODEL TRAINING WITH FESTIVAL FEATURES")
    print("="*70 + "\n")
    
    print(" STEP 1: Collecting Historical Market Data")
    print("-" * 70)
    
    scraper = AgmarknetScraper()
    
    print("   • Fetching recent data (7 days)...")
    recent_data = scraper.scrape_market_prices(days_back=7)
    print(f"    Collected {len(recent_data)} recent price records")
    
    print("   • Fetching historical data (90 days)...")
    historical_data = scraper.scrape_historical_data(days_back=90)
    print(f"    Collected {len(historical_data)} historical records")
    
    all_data = recent_data + historical_data
    print(f"    Total dataset: {len(all_data)} records\n")
    
    print(" STEP 2: Preprocessing with Festival Features")
    print("-" * 70)
    
    df = pd.DataFrame(all_data)
    print(f"   • Dataset shape: {df.shape}")
    print(f"   • Date range: {df['date'].min()} to {df['date'].max()}")
    
    df = df.dropna(subset=['commodity', 'market', 'price'])
    print(f"   • After cleaning: {df.shape}")
    
    preprocessor = DataPreprocessor()
    
    print("   • Extracting temporal features...")
    temporal_features = preprocessor.extract_temporal_features(df['date'])
    print(f"    Generated {temporal_features.shape[1]} temporal features")
    
    print("   • Enriching with festival calendar...")
    df_enriched = preprocessor.festival_calendar.enrich_dataframe(df, 'date')
    print(f"    Added festival/event indicators")
    
    categorical_cols = ['commodity', 'market', 'state']
    print(f"   • Encoding {len(categorical_cols)} categorical features...")
    df_encoded = preprocessor.encode_categorical(df_enriched, categorical_cols, fit=True)
    
    feature_cols = [col for col in df_encoded.columns if col not in ['price', 'date', 'min_price', 'max_price', 'modal_price', 'arrival']]
    feature_cols = [col for col in feature_cols if df_encoded[col].dtype in [np.float64, np.int64]]
    
    X = df_encoded[feature_cols].values
    y = df_encoded['price'].values
    
    print(f"    Feature matrix: {X.shape}")
    print(f"    Target values: {len(y)}")
    print(f"    Top features: {', '.join(feature_cols[:5])}\n")
    
    print(" STEP 3: Training Ensemble Models")
    print("-" * 70)
    
    trainer = ModelTrainer(preprocessor)
    
    results = trainer.train_all_models(X, y)
    
    print("\n STEP 4: Model Performance Summary")
    print("-" * 70)
    print(f"{'Model':<15} {'Accuracy':<12} {'MAE':<12} {'RMSE':<12}")
    print("-" * 70)
    
    for model_name, result in results.items():
        metrics = result.get('metrics', {})
        accuracy = metrics.get('accuracy', 0)
        mae = metrics.get('mae', 0)
        rmse = metrics.get('rmse', 0)
        print(f"{model_name:<15} {accuracy:>10.2%}  ₹{mae:>10.2f}  ₹{rmse:>10.2f}")
    
    print("-" * 70 + "\n")
    
    print(" STEP 5: Saving Trained Models")
    print("-" * 70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_paths = trainer.save_all_models(version=timestamp)
    preprocessor_path = trainer.save_preprocessor(version=timestamp)
    
    print(f"    Models saved with version: {timestamp}")
    for model_name, path in model_paths.items():
        print(f"     - {model_name}: {path}")
    print(f"    Preprocessor: {preprocessor_path}\n")
    
    print(" MODEL TRAINING COMPLETE!")
    print("="*70 + "\n")
    
    print(" Key Insights:")
    print(f"   • Trained on {len(all_data)} market records across 90 days")
    print(f"   • Festival features integrated: {[k for k in df_enriched.columns if 'festival' in k or 'season' in k]}")
    print(f"   • Models use {len(feature_cols)} engineered features")
    print(f"   • Best model ready for production predictions\n")

if __name__ == "__main__":
    main()
