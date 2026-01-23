"""Tests for data preprocessor."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.ml.preprocessor import DataPreprocessor


class TestDataPreprocessor:
    """Test DataPreprocessor class."""
    
    def test_init(self):
        """Test preprocessor initialization."""
        preprocessor = DataPreprocessor(scaler_type="standard")
        assert preprocessor.scaler_type == "standard"
        assert len(preprocessor.feature_names) == 0
    
    def test_extract_temporal_features(self):
        """Test temporal feature extraction."""
        preprocessor = DataPreprocessor()
        dates = pd.Series([datetime.now() - timedelta(days=i) for i in range(10)])
        
        features = preprocessor.extract_temporal_features(dates)
        
        assert "day_of_week" in features.columns
        assert "month" in features.columns
        assert "season" in features.columns
        assert "month_sin" in features.columns
        assert "month_cos" in features.columns
        assert len(features) == 10
    
    def test_detect_outliers_iqr(self):
        """Test outlier detection using IQR method."""
        preprocessor = DataPreprocessor()
        data = np.array([1, 2, 3, 4, 5, 100])  # 100 is an outlier
        
        outliers = preprocessor.detect_outliers(data, method="iqr")
        
        assert outliers[-1] == True  # Last element is outlier
        assert sum(outliers) >= 1
    
    def test_handle_outliers_clip(self):
        """Test outlier handling with clipping."""
        preprocessor = DataPreprocessor()
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 100.0])
        
        result = preprocessor.handle_outliers(data, strategy="clip")
        
        assert result[-1] < 100.0  # Outlier should be clipped
        assert all(result >= 0)
    
    def test_scale_features(self):
        """Test feature scaling."""
        preprocessor = DataPreprocessor()
        data = np.array([100, 200, 300, 400, 500])
        
        scaled = preprocessor.scale_features(data, "test_feature", fit=True)
        
        assert scaled.mean() == pytest.approx(0, abs=1e-10)
        assert len(scaled) == len(data)
    
    def test_prepare_training_data(self):
        """Test training data preparation."""
        preprocessor = DataPreprocessor()
        
        # Create sample data
        df = pd.DataFrame({
            'date': [datetime.now() - timedelta(days=i) for i in range(10)],
            'price': [2500 + i*10 for i in range(10)],
            'arrival': [1000 + i*50 for i in range(10)],
            'commodity_id': [1] * 10,
            'market_id': [1] * 10,
        })
        
        features, target = preprocessor.prepare_training_data(
            df,
            target_col='price',
            date_col='date',
            numeric_cols=['arrival', 'commodity_id', 'market_id'],
        )
        
        assert features.shape[0] == 10
        assert target.shape[0] == 10
        assert len(preprocessor.feature_names) > 0


class TestFeatureEngineering:
    """Test feature engineering methods."""
    
    def test_seasonal_features(self):
        """Test seasonal feature extraction."""
        preprocessor = DataPreprocessor()
        
        # Test different months
        dates = pd.Series([
            datetime(2026, 1, 15),  # Rabi
            datetime(2026, 7, 15),  # Kharif
            datetime(2026, 4, 15),  # Summer
        ])
        
        features = preprocessor.extract_temporal_features(dates)
        
        assert features['season'].iloc[0] == 1  # Rabi
        assert features['season'].iloc[1] == 2  # Kharif
        assert features['season'].iloc[2] == 3  # Summer
    
    def test_cyclical_encoding(self):
        """Test cyclical encoding of temporal features."""
        preprocessor = DataPreprocessor()
        dates = pd.Series([datetime(2026, 6, 15)])
        
        features = preprocessor.extract_temporal_features(dates)
        
        # Check cyclical features exist
        assert 'month_sin' in features.columns
        assert 'month_cos' in features.columns
        assert 'day_sin' in features.columns
        assert 'day_cos' in features.columns
        
        # Check values are in valid range [-1, 1]
        assert -1 <= features['month_sin'].iloc[0] <= 1
        assert -1 <= features['month_cos'].iloc[0] <= 1
