"""ML model training and hyperparameter optimization."""

from typing import Tuple, Dict, List, Optional, Any
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
from loguru import logger

from sklearn.model_selection import cross_val_score, GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error

import xgboost as xgb
import lightgbm as lgb

try:
    from catboost import CatBoostRegressor
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False

from app.config import settings
from app.ml.preprocessor import DataPreprocessor


class ModelTrainer:
    """Train and evaluate ensemble ML models for agricultural price prediction."""

    def __init__(self, preprocessor: DataPreprocessor = None):
        """
        Initialize model trainer.

        Args:
            preprocessor: DataPreprocessor instance for feature engineering
        """
        self.preprocessor = preprocessor or DataPreprocessor()
        self.models: Dict[str, Any] = {}
        self.metrics: Dict[str, Dict[str, float]] = {}
        self.model_dir = Path(settings.model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized ModelTrainer with model directory: {self.model_dir}")

    def train_xgboost(
        self, X_train: np.ndarray, y_train: np.ndarray, cv_splits: int = 5
    ) -> xgb.XGBRegressor:
        """
        Train XGBoost model with hyperparameter tuning.

        Args:
            X_train: Training features
            y_train: Training target
            cv_splits: Number of cross-validation splits

        Returns:
            Trained XGBRegressor model
        """
        logger.info("Training XGBoost model...")

        # Base model
        xgb_model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1,
            tree_method='hist',
        )

        # Hyperparameter grid (simplified for training speed)
        param_grid = {
            'max_depth': [5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1],
            'n_estimators': [100, 200],
        }

        # GridSearchCV with TimeSeriesSplit
        tscv = TimeSeriesSplit(n_splits=cv_splits)
        grid_search = GridSearchCV(
            xgb_model,
            param_grid,
            cv=tscv,
            scoring='r2',
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X_train, y_train)
        logger.info(
            f"XGBoost best params: {grid_search.best_params_}, "
            f"best CV score: {grid_search.best_score_:.4f}"
        )

        self.models['xgboost'] = grid_search.best_estimator_
        return grid_search.best_estimator_

    def train_lightgbm(
        self, X_train: np.ndarray, y_train: np.ndarray, cv_splits: int = 5
    ) -> lgb.LGBMRegressor:
        """
        Train LightGBM model with hyperparameter tuning.

        Args:
            X_train: Training features
            y_train: Training target
            cv_splits: Number of cross-validation splits

        Returns:
            Trained LGBMRegressor model
        """
        logger.info("Training LightGBM model...")

        lgb_model = lgb.LGBMRegressor(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1,
        )

        param_grid = {
            'max_depth': [5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1],
            'n_estimators': [100, 200],
        }

        tscv = TimeSeriesSplit(n_splits=cv_splits)
        grid_search = GridSearchCV(
            lgb_model,
            param_grid,
            cv=tscv,
            scoring='r2',
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X_train, y_train)
        logger.info(
            f"LightGBM best params: {grid_search.best_params_}, "
            f"best CV score: {grid_search.best_score_:.4f}"
        )

        self.models['lightgbm'] = grid_search.best_estimator_
        return grid_search.best_estimator_

    def train_catboost(
        self, X_train: np.ndarray, y_train: np.ndarray, cv_splits: int = 5
    ) -> Optional[Any]:
        """
        Train CatBoost model with hyperparameter tuning.

        Args:
            X_train: Training features
            y_train: Training target
            cv_splits: Number of cross-validation splits

        Returns:
            Trained CatBoostRegressor model or None if not available
        """
        if not HAS_CATBOOST:
            logger.warning("CatBoost not available, skipping")
            return None

        logger.info("Training CatBoost model...")

        catboost_model = CatBoostRegressor(
            iterations=200,
            depth=7,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42,
            verbose=False,
            thread_count=-1,
        )

        param_grid = {
            'depth': [5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1],
            'iterations': [100, 200],
        }

        tscv = TimeSeriesSplit(n_splits=cv_splits)
        grid_search = GridSearchCV(
            catboost_model,
            param_grid,
            cv=tscv,
            scoring='r2',
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X_train, y_train)
        logger.info(
            f"CatBoost best params: {grid_search.best_params_}, "
            f"best CV score: {grid_search.best_score_:.4f}"
        )

        self.models['catboost'] = grid_search.best_estimator_
        return grid_search.best_estimator_

    def train_random_forest(
        self, X_train: np.ndarray, y_train: np.ndarray, cv_splits: int = 5
    ) -> RandomForestRegressor:
        """
        Train Random Forest model with hyperparameter tuning.

        Args:
            X_train: Training features
            y_train: Training target
            cv_splits: Number of cross-validation splits

        Returns:
            Trained RandomForestRegressor model
        """
        logger.info("Training Random Forest model...")

        rf_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

        param_grid = {
            'max_depth': [10, 15, 20],
            'n_estimators': [100, 200],
            'min_samples_split': [3, 5],
        }

        tscv = TimeSeriesSplit(n_splits=cv_splits)
        grid_search = GridSearchCV(
            rf_model,
            param_grid,
            cv=tscv,
            scoring='r2',
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X_train, y_train)
        logger.info(
            f"Random Forest best params: {grid_search.best_params_}, "
            f"best CV score: {grid_search.best_score_:.4f}"
        )

        self.models['random_forest'] = grid_search.best_estimator_
        return grid_search.best_estimator_

    def evaluate_model(
        self, model: Any, X_test: np.ndarray, y_test: np.ndarray, model_name: str
    ) -> Dict[str, float]:
        """
        Evaluate model performance.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target
            model_name: Name of the model

        Returns:
            Dictionary of evaluation metrics
        """
        y_pred = model.predict(X_test)

        metrics = {
            'r2_score': float(r2_score(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'mape': float(mean_absolute_percentage_error(y_test, y_pred)),
        }

        # Add RMSE percentage (normalized by mean actual price)
        mean_y = np.mean(y_test)
        if mean_y > 0:
            metrics['rmse_pct'] = float((metrics['rmse'] / mean_y) * 100)

        # Accuracy approximation (1 - MAPE for regression)
        metrics['accuracy'] = float(max(0, 1 - metrics['mape']))

        self.metrics[model_name] = metrics

        logger.info(
            f"{model_name} Metrics - "
            f"R²: {metrics['r2_score']:.4f}, "
            f"RMSE: {metrics['rmse']:.4f}, "
            f"MAE: {metrics['mae']:.4f}, "
            f"MAPE: {metrics['mape']:.4f}"
        )

        return metrics

    def get_feature_importance(self, model: Any, model_name: str) -> Dict[str, float]:
        """
        Get feature importance from model.

        Args:
            model: Trained model
            model_name: Name of the model

        Returns:
            Dictionary of feature importance scores
        """
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            logger.warning(f"Model {model_name} doesn't support feature importance")
            return {}

        # Normalize importances
        importance_dict = {}
        total_importance = np.sum(importances)

        if total_importance > 0:
            for feature, importance in zip(self.preprocessor.feature_names, importances):
                importance_dict[feature] = float(importance / total_importance)
        else:
            # Fallback to equal importance
            equal_importance = 1.0 / len(self.preprocessor.feature_names)
            importance_dict = {
                feature: equal_importance
                for feature in self.preprocessor.feature_names
            }

        return importance_dict

    def train_ensemble(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        models_to_train: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Train all ensemble models.

        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            models_to_train: List of model names to train (default: all)

        Returns:
            Dictionary with models and metrics
        """
        if models_to_train is None:
            models_to_train = ['xgboost', 'lightgbm', 'catboost', 'random_forest']

        results = {}

        for model_name in models_to_train:
            logger.info(f"\n{'='*50}")
            logger.info(f"Training {model_name.upper()}")
            logger.info(f"{'='*50}")

            if model_name == 'xgboost':
                model = self.train_xgboost(X_train, y_train)
            elif model_name == 'lightgbm':
                model = self.train_lightgbm(X_train, y_train)
            elif model_name == 'catboost':
                model = self.train_catboost(X_train, y_train)
            elif model_name == 'random_forest':
                model = self.train_random_forest(X_train, y_train)
            else:
                logger.warning(f"Unknown model: {model_name}")
                continue

            # Evaluate model
            metrics = self.evaluate_model(model, X_test, y_test, model_name)
            
            # Get feature importance
            importance = self.get_feature_importance(model, model_name)

            results[model_name] = {
                'model': model,
                'metrics': metrics,
                'feature_importance': importance,
            }

        logger.info(f"\n{'='*50}")
        logger.info("Ensemble Training Complete")
        logger.info(f"{'='*50}")

        return results

    def save_model(self, model: Any, model_name: str, version: str = None) -> str:
        """
        Save trained model to disk.

        Args:
            model: Trained model
            model_name: Name of the model
            version: Version string (default: timestamp)

        Returns:
            Path to saved model
        """
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

        model_path = self.model_dir / f"{model_name}_{version}.joblib"
        joblib.dump(model, model_path)

        logger.info(f"Saved {model_name} model to {model_path}")
        return str(model_path)

    def save_all_models(self, version: str = None) -> Dict[str, str]:
        """
        Save all trained models to disk.

        Args:
            version: Version string (default: timestamp)

        Returns:
            Dictionary mapping model names to file paths
        """
        saved_paths = {}

        for model_name, model in self.models.items():
            path = self.save_model(model, model_name, version)
            saved_paths[model_name] = path

        logger.info(f"Saved {len(saved_paths)} models")
        return saved_paths

    def save_preprocessor(self, version: str = None) -> str:
        """
        Save fitted preprocessor to disk.

        Args:
            version: Version string (default: timestamp)

        Returns:
            Path to saved preprocessor
        """
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

        preprocessor_path = self.model_dir / f"preprocessor_{version}.joblib"
        joblib.dump(self.preprocessor, preprocessor_path)

        logger.info(f"Saved preprocessor to {preprocessor_path}")
        return str(preprocessor_path)

    def load_model(self, model_path: str) -> Any:
        """
        Load trained model from disk.

        Args:
            model_path: Path to model file

        Returns:
            Loaded model
        """
        model = joblib.load(model_path)
        logger.info(f"Loaded model from {model_path}")
        return model

    def get_model_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get summary of all trained models.

        Returns:
            Dictionary with model metrics and feature importance
        """
        summary = {}

        for model_name in self.models.keys():
            summary[model_name] = {
                'metrics': self.metrics.get(model_name, {}),
                'feature_importance': self.get_feature_importance(
                    self.models[model_name], model_name
                ),
            }

        return summary
