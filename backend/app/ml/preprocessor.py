"""Data preprocessing and feature engineering for agricultural ML models."""

from typing import Tuple, List, Dict, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from loguru import logger

from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer

from app.core.utils import get_current_timestamp
from app.core.festival_calendar import FestivalCalendar


class DataPreprocessor:

    def __init__(self, scaler_type: str = "standard"):
        
        self.scaler_type = scaler_type
        self.scalers: Dict[str, StandardScaler] = {}
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.imputer = SimpleImputer(strategy="median")
        self.feature_names: List[str] = []
        self.categorical_features: List[str] = []
        self.numeric_features: List[str] = []
        self.festival_calendar = FestivalCalendar()

        logger.info(f"Preprocessor ready with {scaler_type} scaling and festival integration")

    def _get_scaler(self, scaler_type: str) -> Any:
        if scaler_type == "standard":
            return StandardScaler()
        elif scaler_type == "minmax":
            return MinMaxScaler()
        elif scaler_type == "robust":
            return RobustScaler()
        else:
            return StandardScaler()

    def extract_temporal_features(self, date_col: pd.Series) -> pd.DataFrame:
        
        features = pd.DataFrame()
        dates = pd.to_datetime(date_col)
        
        features['day_of_week'] = dates.dt.dayofweek
        features['day_of_month'] = dates.dt.day
        features['month'] = dates.dt.month
        features['quarter'] = dates.dt.quarter
        features['week_of_year'] = dates.dt.isocalendar().week
        features['day_of_year'] = dates.dt.dayofyear
        
        def get_season(month: int) -> int:
            if month in [10, 11, 12, 1, 2, 3]:
                return 1
            elif month in [6, 7, 8, 9]:
                return 2
            else:
                return 3
        
        features['season'] = dates.dt.month.map(get_season)
        
        features['month_sin'] = np.sin(2 * np.pi * dates.dt.month / 12)
        features['month_cos'] = np.cos(2 * np.pi * dates.dt.month / 12)
        features['day_sin'] = np.sin(2 * np.pi * dates.dt.day / 31)
        features['day_cos'] = np.cos(2 * np.pi * dates.dt.day / 31)
        
        festival_features = dates.apply(
            lambda d: pd.Series(self.festival_calendar.get_enhanced_features(d))
        )
        
        for col in festival_features.columns:
            features[col] = festival_features[col]
        
        return features

    def extract_lag_features(
        self, data: pd.DataFrame, col: str, lags: List[int] = None
    ) -> pd.DataFrame:
        """
        Extract lag features from time series.

        Args:
            data: DataFrame with time series data
            col: Column name to create lag features from
            lags: List of lag periods (default: [1, 7, 30])

        Returns:
            DataFrame with lag features
        """
        if lags is None:
            lags = [1, 7, 30]

        features = pd.DataFrame()
        
        for lag in lags:
            features[f'{col}_lag_{lag}'] = data[col].shift(lag)

        # Rolling statistics
        for window in [7, 30]:
            features[f'{col}_rolling_mean_{window}'] = (
                data[col].rolling(window=window).mean()
            )
            features[f'{col}_rolling_std_{window}'] = (
                data[col].rolling(window=window).std()
            )
            features[f'{col}_rolling_min_{window}'] = (
                data[col].rolling(window=window).min()
            )
            features[f'{col}_rolling_max_{window}'] = (
                data[col].rolling(window=window).max()
            )

        # Exponential weighted average
        features[f'{col}_ewm_mean'] = data[col].ewm(span=7).mean()

        return features

    def detect_outliers(
        self, data: np.ndarray, method: str = "iqr", threshold: float = 1.5
    ) -> np.ndarray:
        """
        Detect outliers using IQR or Z-score method.

        Args:
            data: Input array
            method: 'iqr' or 'zscore'
            threshold: IQR multiplier (1.5) or z-score threshold (3)

        Returns:
            Boolean mask of outliers
        """
        if method == "iqr":
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            return (data < lower) | (data > upper)
        else:  # zscore
            z_scores = np.abs((data - np.mean(data)) / np.std(data))
            return z_scores > threshold

    def handle_outliers(
        self, data: np.ndarray, method: str = "iqr", strategy: str = "clip"
    ) -> np.ndarray:
        """
        Handle outliers in data.

        Args:
            data: Input array
            method: Outlier detection method
            strategy: 'remove', 'clip', or 'median'

        Returns:
            Processed array
        """
        outlier_mask = self.detect_outliers(data, method)
        
        if strategy == "remove":
            return data[~outlier_mask]
        elif strategy == "clip":
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            return np.clip(data, lower, upper)
        else:  # median
            median = np.median(data[~outlier_mask])
            data[outlier_mask] = median
            return data

    def encode_categorical(
        self, data: pd.DataFrame, categorical_cols: List[str], fit: bool = True
    ) -> pd.DataFrame:
        """
        Encode categorical variables.

        Args:
            data: DataFrame with categorical columns
            categorical_cols: List of categorical column names
            fit: Whether to fit encoders or use existing ones

        Returns:
            DataFrame with encoded categorical features
        """
        data_encoded = data.copy()
        
        for col in categorical_cols:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                data_encoded[col] = self.label_encoders[col].fit_transform(
                    data_encoded[col].astype(str)
                )
            else:
                if col in self.label_encoders:
                    data_encoded[col] = self.label_encoders[col].transform(
                        data_encoded[col].astype(str)
                    )

        return data_encoded

    def scale_features(
        self, data: np.ndarray, feature_name: str, fit: bool = True
    ) -> np.ndarray:
        """
        Scale numerical features.

        Args:
            data: Input array (1D or 2D)
            feature_name: Name for scaler storage
            fit: Whether to fit scaler or use existing one

        Returns:
            Scaled array
        """
        try:
            # Convert to 2D if needed
            data_2d = data.reshape(-1, 1) if data.ndim == 1 else data
            
            # Handle case where all values are the same (std = 0)
            if data_2d.std() == 0:
                logger.debug(f"Feature {feature_name} has zero variance, returning as-is")
                return data_2d.flatten() if data.ndim == 1 else data_2d
            
            if fit:
                self.scalers[feature_name] = self._get_scaler(self.scaler_type)
                scaled = self.scalers[feature_name].fit_transform(data_2d)
            else:
                if feature_name in self.scalers:
                    scaled = self.scalers[feature_name].transform(data_2d)
                else:
                    logger.debug(f"Scaler for {feature_name} not found, using input data")
                    scaled = data_2d

            return scaled.flatten() if data.ndim == 1 else scaled
        except Exception as e:
            logger.warning(f"Error scaling {feature_name}: {e}, returning input data")
            return data

    def prepare_training_data(
        self,
        data: pd.DataFrame,
        target_col: str,
        date_col: str,
        categorical_cols: List[str] = None,
        numeric_cols: List[str] = None,
        handle_missing: bool = True,
        handle_outliers_: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for model training.
        
        Uses the same 16 standard features as prepare_prediction_data for consistency:
        - commodity_id, market_id, arrival
        - day_of_week, month, season, week_of_year, quarter
        - is_festival, festival_effect, holiday_proximity, monsoon_factor, harvest_season
        - price, month_sin, month_cos

        Args:
            data: Input DataFrame
            target_col: Target column name
            date_col: Date column name
            categorical_cols: List of categorical columns (ignored, using standard features)
            numeric_cols: List of numeric columns (ignored, using standard features)
            handle_missing: Whether to handle missing values
            handle_outliers_: Whether to handle outliers

        Returns:
            Tuple of (features, target) as numpy arrays
        """
        data_processed = data.copy()

        # Handle missing values for key columns
        key_numeric_cols = ['price', 'arrival', 'commodity_id', 'market_id', 'min_price', 'max_price', 'modal_price']
        cols_to_impute = [c for c in key_numeric_cols if c in data_processed.columns]
        if handle_missing and cols_to_impute:
            for col in cols_to_impute:
                if data_processed[col].isnull().any():
                    data_processed[col] = data_processed[col].fillna(data_processed[col].median())
            logger.info(f"Handled missing values in {len(cols_to_impute)} columns")

        # Extract temporal features (includes festival indicators)
        temporal_features = self.extract_temporal_features(data_processed[date_col])

        # Build features dataframe with standard 16 features
        features = pd.DataFrame()
        
        # Add numeric columns that exist
        for col in ['commodity_id', 'market_id', 'arrival']:
            if col in data_processed.columns:
                features[col] = data_processed[col].values
            else:
                features[col] = 0.0
        
        # Add price column (will be used as a lagged feature, not the target)
        # Use modal_price or min_price as proxy for historical price info
        if 'modal_price' in data_processed.columns:
            features['price'] = data_processed['modal_price'].values
        elif 'min_price' in data_processed.columns:
            features['price'] = data_processed['min_price'].values
        else:
            features['price'] = 0.0
        
        # Add temporal/festival features
        features = pd.concat([features.reset_index(drop=True), temporal_features.reset_index(drop=True)], axis=1)
        
        # Define standard 16 features for model compatibility (same as prepare_prediction_data)
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
            'price',             # 12
            'week_of_year',      # 13
            'quarter',           # 14
            'month_sin',         # 15
            'month_cos',         # 16
        ]
        
        # Fill missing features with defaults
        for col in standard_features:
            if col not in features.columns:
                features[col] = 0.0
        
        # Select only standard features in order
        features = features[standard_features].copy()
        
        # Handle outliers on numeric features
        if handle_outliers_:
            for col in ['arrival', 'price']:
                if col in features.columns:
                    features[col] = self.handle_outliers(features[col].values, strategy="clip")
        
        # Scale numeric features
        for col in ['arrival', 'price']:
            if col in features.columns:
                features[col] = self.scale_features(features[col].values, col, fit=True)

        # Store feature names for later use
        self.feature_names = standard_features
        self.numeric_features = ['commodity_id', 'market_id', 'arrival', 'price']
        self.categorical_features = []

        # Extract target
        target = data_processed[target_col].values

        # Convert features to numeric dtype
        features = features.apply(pd.to_numeric, errors="coerce")

        # Remove rows with NaN in features or target
        valid_idx = ~(pd.isna(features).any(axis=1) | pd.isna(target))
        features = features.to_numpy()[valid_idx]
        target = target[valid_idx]

        logger.info(
            f"Prepared training data: {features.shape[0]} samples, {features.shape[1]} features"
        )

        return features, target

    def prepare_prediction_data(
        self, data: pd.DataFrame, date_col: str, categorical_cols: List[str] = None
    ) -> np.ndarray:
        """
        Prepare data for prediction (uses fitted preprocessor).
        
        Generates features matching the training data (29 features):
        - numeric: commodity_id, market_id, arrival, min_price, max_price, modal_price
        - temporal: day_of_week, day_of_month, month, quarter, week_of_year, day_of_year, season
        - cyclical: month_sin, month_cos, day_sin, day_cos
        - festival: is_festival, festival_effect, holiday_proximity, etc.

        Args:
            data: Input DataFrame (must contain commodity_id, market_id, arrival, date columns)
            date_col: Date column name
            categorical_cols: List of categorical columns

        Returns:
            Processed features as numpy array
        """
        data_processed = data.copy()

        # Extract temporal features (includes festival indicators)
        temporal_features = self.extract_temporal_features(data_processed[date_col])

        # Build features dataframe with proper columns
        features = pd.DataFrame()
        
        # Add numeric columns that exist (matching training data)
        numeric_cols = ['commodity_id', 'market_id', 'arrival', 'min_price', 'max_price', 'modal_price']
        for col in numeric_cols:
            if col in data_processed.columns:
                features[col] = data_processed[col]
            else:
                # Derive from price if available
                if col == 'min_price' and 'price' in data_processed.columns:
                    features[col] = data_processed['price'] * 0.9
                elif col == 'max_price' and 'price' in data_processed.columns:
                    features[col] = data_processed['price'] * 1.1
                elif col == 'modal_price' and 'price' in data_processed.columns:
                    features[col] = data_processed['price']
                else:
                    features[col] = 0.0
        
        # Add temporal/festival features
        features = pd.concat([features, temporal_features], axis=1)
        
        # Handle missing values
        features = features.fillna(features.mean(numeric_only=True))
        features = features.fillna(0.0)
        
        # Update feature names for consistency
        self.feature_names = features.columns.tolist()
        
        features_array = features.values

        logger.info(f"Prepared prediction data: shape={features_array.shape}, features={len(self.feature_names)}")

        return features_array

    def get_feature_importance_baseline(self, features: np.ndarray) -> Dict[str, float]:
        """
        Get baseline feature importance using variance.

        Args:
            features: Feature array

        Returns:
            Dictionary of feature importance scores
        """
        feature_variance = np.var(features, axis=0)
        total_variance = np.sum(feature_variance)
        
        # Handle zero variance case (e.g., single sample)
        if total_variance == 0:
            n_features = len(self.feature_names)
            return {name: 1.0 / n_features for name in self.feature_names}
        
        importance = {
            name: float(variance / total_variance)
            for name, variance in zip(self.feature_names, feature_variance)
        }
        
        return importance
