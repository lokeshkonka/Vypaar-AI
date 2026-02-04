#!/usr/bin/env python3
"""
Verify that preprocessor generates exactly 29 features
"""

import sys
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, '/home/vishal/code/Vypaar-AI/backend')

from app.ml.preprocessor import DataPreprocessor

def test_feature_generation():
    preprocessor = DataPreprocessor()
    
    sample_data = pd.DataFrame({
        'date': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(100)],
        'commodity': ['Wheat'] * 100,
        'market': ['Delhi'] * 100,
        'commodity_id': [1] * 100,
        'market_id': [1] * 100,
        'price': [2000 + i * 10 for i in range(100)],
        'arrival': [500 + i * 5 for i in range(100)],
    })
    
    features = preprocessor.prepare_prediction_data(
        sample_data,
        date_col='date',
        categorical_cols=['commodity', 'market']
    )
    
    feature_count = features.shape[1]
    print(f"✅ Generated {feature_count} features")
    print(f"   Expected: 29 features")
    print(f"   Status: {'PASS' if feature_count == 29 else 'FAIL'}")
    
    if feature_count != 29:
        print(f"\n   Difference: {feature_count - 29} features")
        print(f"   Need to {'add' if feature_count < 29 else 'remove'} {abs(feature_count - 29)} features")
    
    return feature_count == 29

if __name__ == "__main__":
    success = test_feature_generation()
    sys.exit(0 if success else 1)
