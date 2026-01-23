"""Ensemble model management and prediction aggregation."""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from loguru import logger
from pathlib import Path
import joblib

from app.config import settings


class EnsembleManager:
    """Manage ensemble of ML models and combine their predictions."""

    def __init__(self):
        """Initialize ensemble manager."""
        self.models: Dict[str, Any] = {}
        self.model_weights: Dict[str, float] = {}
        self.ensemble_type = 'weighted_average'  # weighted_average, voting, stacking
        self.preprocessor = None
        self.model_dir = Path(settings.model_dir)

        logger.info("Initialized EnsembleManager")

    def load_models(
        self, model_paths: Dict[str, str], preprocessor_path: str = None
    ) -> None:
        """
        Load pre-trained models from disk.

        Args:
            model_paths: Dictionary mapping model names to file paths
            preprocessor_path: Path to fitted preprocessor
        """
        for model_name, path in model_paths.items():
            try:
                model = joblib.load(path)
                self.models[model_name] = model
                logger.info(f"Loaded model: {model_name} from {path}")
            except Exception as e:
                logger.error(f"Failed to load {model_name}: {e}")

        # Load preprocessor
        if preprocessor_path:
            try:
                self.preprocessor = joblib.load(preprocessor_path)
                logger.info(f"Loaded preprocessor from {preprocessor_path}")
            except Exception as e:
                logger.error(f"Failed to load preprocessor: {e}")

        logger.info(f"Loaded {len(self.models)} models for ensemble")

    def load_latest_models(self) -> None:
        """Load latest version of all models from model directory."""
        if not self.model_dir.exists():
            logger.error(f"Model directory not found: {self.model_dir}")
            return

        # Find latest models for each type
        model_types = ['xgboost', 'lightgbm', 'catboost', 'random_forest']
        model_paths = {}

        for model_type in model_types:
            # Find all models of this type
            pattern = f"{model_type}_*.joblib"
            matching_files = list(self.model_dir.glob(pattern))

            if matching_files:
                # Sort by modification time and get the latest
                latest_model = max(matching_files, key=lambda p: p.stat().st_mtime)
                model_paths[model_type] = str(latest_model)

        # Find latest preprocessor
        preprocessor_files = list(self.model_dir.glob("preprocessor_*.joblib"))
        preprocessor_path = None
        if preprocessor_files:
            preprocessor_path = str(max(preprocessor_files, key=lambda p: p.stat().st_mtime))

        if model_paths:
            self.load_models(model_paths, preprocessor_path)
        else:
            logger.warning("No trained models found in model directory")

    def set_model_weights(self, weights: Dict[str, float]) -> None:
        """
        Set weights for ensemble models.

        Args:
            weights: Dictionary mapping model names to weights
        """
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        self.model_weights = {
            model: weight / total_weight for model, weight in weights.items()
        }

        logger.info(f"Set ensemble weights: {self.model_weights}")

    def set_equal_weights(self) -> None:
        """Set equal weights for all models."""
        equal_weight = 1.0 / len(self.models) if self.models else 0

        self.model_weights = {model_name: equal_weight for model_name in self.models.keys()}

        logger.info(f"Set equal ensemble weights: {self.model_weights}")

    def set_accuracy_based_weights(self, metrics: Dict[str, Dict[str, float]]) -> None:
        """
        Set weights based on model accuracy.

        Args:
            metrics: Dictionary of model metrics with accuracy scores
        """
        weights = {}

        for model_name, model_metrics in metrics.items():
            accuracy = model_metrics.get('accuracy', 0.5)
            weights[model_name] = accuracy

        self.set_model_weights(weights)
        logger.info("Set accuracy-based ensemble weights")

    def predict_weighted_average(
        self, features: np.ndarray
    ) -> Tuple[float, Dict[str, float], Dict[str, float]]:
        """
        Make predictions using weighted average ensemble.

        Args:
            features: Input features (1D array for single sample)

        Returns:
            Tuple of (ensemble_prediction, individual_predictions, weights)
        """
        if not self.models:
            raise ValueError("No models loaded in ensemble")

        if len(self.model_weights) == 0:
            self.set_equal_weights()

        individual_predictions = {}
        weighted_sum = 0

        for model_name, model in self.models.items():
            try:
                # Handle both 1D and 2D inputs
                if features.ndim == 1:
                    prediction = model.predict(features.reshape(1, -1))[0]
                else:
                    prediction = model.predict(features)

                individual_predictions[model_name] = float(prediction)

                # Add to weighted sum
                weight = self.model_weights.get(model_name, 0)
                weighted_sum += prediction * weight

            except Exception as e:
                logger.error(f"Error getting prediction from {model_name}: {e}")
                individual_predictions[model_name] = None

        ensemble_prediction = weighted_sum

        return ensemble_prediction, individual_predictions, self.model_weights

    def predict_voting(
        self, features: np.ndarray
    ) -> Tuple[float, Dict[str, float], float]:
        """
        Make predictions using voting ensemble (average).

        Args:
            features: Input features

        Returns:
            Tuple of (ensemble_prediction, individual_predictions, variance)
        """
        predictions = []
        individual_predictions = {}

        for model_name, model in self.models.items():
            try:
                if features.ndim == 1:
                    prediction = model.predict(features.reshape(1, -1))[0]
                else:
                    prediction = model.predict(features)

                individual_predictions[model_name] = float(prediction)
                predictions.append(float(prediction))

            except Exception as e:
                logger.error(f"Error getting prediction from {model_name}: {e}")

        if not predictions:
            raise ValueError("No valid predictions from ensemble models")

        ensemble_prediction = np.mean(predictions)
        variance = float(np.var(predictions))

        return ensemble_prediction, individual_predictions, variance

    def predict_with_confidence(
        self, features: np.ndarray
    ) -> Tuple[float, float, Dict[str, float]]:
        """
        Make predictions with confidence interval.

        Args:
            features: Input features

        Returns:
            Tuple of (prediction, confidence, individual_predictions)
        """
        predictions = []
        individual_predictions = {}

        for model_name, model in self.models.items():
            try:
                if features.ndim == 1:
                    prediction = model.predict(features.reshape(1, -1))[0]
                else:
                    prediction = model.predict(features)

                individual_predictions[model_name] = float(prediction)
                predictions.append(float(prediction))

            except Exception as e:
                logger.error(f"Error getting prediction from {model_name}: {e}")

        if not predictions:
            raise ValueError("No valid predictions from ensemble models")

        ensemble_prediction = np.mean(predictions)
        std_prediction = np.std(predictions)

        # Confidence based on agreement (lower std = higher confidence)
        # Using coefficient of variation as inverse of confidence
        cv = std_prediction / (abs(ensemble_prediction) + 1e-6)
        confidence = 1 / (1 + cv)  # Convert to 0-1 range

        return ensemble_prediction, confidence, individual_predictions

    def get_feature_importance_combined(
        self, model_importances: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Combine feature importance from all models.

        Args:
            model_importances: Dictionary mapping model names to feature importance dicts

        Returns:
            Combined feature importance scores
        """
        if not model_importances:
            logger.warning("No model importances provided")
            return {}

        # Get all features
        all_features = set()
        for importance_dict in model_importances.values():
            all_features.update(importance_dict.keys())

        # Combine importances
        combined_importance = {}

        for feature in all_features:
            importances = []

            for model_name, importance_dict in model_importances.items():
                if feature in importance_dict:
                    weight = self.model_weights.get(model_name, 1.0 / len(self.models))
                    importances.append(importance_dict[feature] * weight)

            if importances:
                combined_importance[feature] = np.mean(importances)

        # Normalize
        total = sum(combined_importance.values())
        if total > 0:
            combined_importance = {
                k: v / total for k, v in combined_importance.items()
            }

        return combined_importance

    def batch_predict(
        self, features_list: np.ndarray
    ) -> Tuple[np.ndarray, List[Dict[str, float]], np.ndarray]:
        """
        Make batch predictions on multiple samples.

        Args:
            features_list: 2D array of features (n_samples x n_features)

        Returns:
            Tuple of (ensemble_predictions, individual_predictions_list, confidences)
        """
        ensemble_predictions = []
        individual_predictions_list = []
        confidences = []

        for features in features_list:
            prediction, confidence, individual = self.predict_with_confidence(features)
            ensemble_predictions.append(prediction)
            individual_predictions_list.append(individual)
            confidences.append(confidence)

        return (
            np.array(ensemble_predictions),
            individual_predictions_list,
            np.array(confidences),
        )

    def calculate_prediction_bounds(
        self,
        ensemble_prediction: float,
        confidence: float,
        individual_predictions: Dict[str, float],
        confidence_level: float = 0.95,
    ) -> Tuple[float, float]:
        """
        Calculate prediction confidence bounds.

        Args:
            ensemble_prediction: Ensemble prediction
            confidence: Confidence score (0-1)
            individual_predictions: Individual model predictions
            confidence_level: Confidence level for bounds (default 0.95)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        predictions = [p for p in individual_predictions.values() if p is not None]

        if not predictions:
            # Fallback if no individual predictions
            margin = abs(ensemble_prediction) * 0.1
            return ensemble_prediction - margin, ensemble_prediction + margin

        std_prediction = np.std(predictions)
        
        # Use confidence and standard deviation to set bounds
        # Lower confidence (higher disagreement) = wider bounds
        margin = std_prediction * (2 - confidence) * 1.96  # 1.96 for 95% CI

        lower_bound = ensemble_prediction - margin
        upper_bound = ensemble_prediction + margin

        return lower_bound, upper_bound

    def get_ensemble_status(self) -> Dict[str, Any]:
        """
        Get status of ensemble.

        Returns:
            Dictionary with ensemble information
        """
        status = {
            'num_models': len(self.models),
            'model_names': list(self.models.keys()),
            'ensemble_type': self.ensemble_type,
            'model_weights': self.model_weights,
            'preprocessor_loaded': self.preprocessor is not None,
        }

        return status
