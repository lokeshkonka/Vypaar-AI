"""Ensemble model management and prediction aggregation."""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from loguru import logger
from pathlib import Path
import joblib
import inspect

from app.config import settings


def _apply_sklearn_compat_shims() -> None:
    """Allow LightGBM to call sklearn validation with force_all_finite across versions."""
    try:
        import sklearn.utils.validation as suv
        import sklearn.utils as su

        original_check_array = suv.check_array
        original_check_x_y = suv.check_X_y

        def check_array_compat(*args, force_all_finite=True, **kwargs):
            kwargs['ensure_all_finite'] = force_all_finite
            return original_check_array(*args, **kwargs)

        def check_x_y_compat(*args, force_all_finite=True, **kwargs):
            kwargs['ensure_all_finite'] = force_all_finite
            return original_check_x_y(*args, **kwargs)

        suv.check_array = check_array_compat  # type: ignore[attr-defined]
        su.check_array = check_array_compat  # type: ignore[attr-defined]
        suv.check_X_y = check_x_y_compat  # type: ignore[attr-defined]
        su.check_X_y = check_x_y_compat  # type: ignore[attr-defined]

        # If LightGBM is already imported, update its cached references too
        try:
            import lightgbm.sklearn as lgb_sklearn  # type: ignore
            lgb_sklearn.check_array = check_array_compat
            lgb_sklearn.check_X_y = check_x_y_compat
        except Exception:
            pass

    except Exception as exc:  # pragma: no cover
        logger.warning(f"Could not apply sklearn compatibility shim: {exc}")


# Apply compatibility shims eagerly at import time to catch early LightGBM imports.
_apply_sklearn_compat_shims()


class EnsembleManager:
    """Manage ensemble of ML models and combine their predictions."""

    def __init__(self):
        """Initialize ensemble manager."""
        _apply_sklearn_compat_shims()
        self.models: Dict[str, Any] = {}
        self.model_weights: Dict[str, float] = {}
        self.ensemble_type = 'weighted_average'  # weighted_average, voting, stacking
        self.preprocessor = None
        self.model_dir = Path(settings.model_dir)
        self.latest_artifact_mtime: Optional[float] = None
        self.latest_artifact_name: Optional[str] = None

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
        """Load latest version of all models from model directory.

        Preference order:
        1. Tuned ensemble artifacts (ensemble_tuned_*.joblib)
        2. Regular ensemble artifacts (ensemble_*.joblib)
        3. Individual model files (random_forest_*.joblib, etc.)
        """
        if not self.model_dir.exists():
            logger.error(f"Model directory not found: {self.model_dir}")
            return

        # Try tuned ensemble first
        tuned_files = list(self.model_dir.glob("ensemble_tuned_*.joblib"))
        loaded_from_ensemble = False
        if tuned_files:
            latest_tuned = max(tuned_files, key=lambda p: p.stat().st_mtime)
            try:
                ensemble_data = joblib.load(str(latest_tuned))
                if isinstance(ensemble_data, dict):
                    for model_name in ['random_forest', 'gradient_boosting', 'xgboost', 'lightgbm', 'catboost']:
                        if model_name in ensemble_data:
                            self.models[model_name] = ensemble_data[model_name]
                    # Persist artifact info & weights if present
                    self.artifact_info = ensemble_data
                    if 'model_weights' in ensemble_data and isinstance(ensemble_data['model_weights'], dict):
                        self.model_weights = ensemble_data['model_weights']
                    self.model_version = str(ensemble_data.get('timestamp', latest_tuned.stem))
                    self.latest_artifact_mtime = latest_tuned.stat().st_mtime
                    self.latest_artifact_name = latest_tuned.name
                    loaded_from_ensemble = True
                    logger.info(f"Loaded tuned ensemble: {latest_tuned.name} with {len(self.models)} models")
            except Exception as e:
                logger.error(f"Failed to load tuned ensemble: {e}")

        # Fallback: regular ensemble
        if not loaded_from_ensemble:
            ensemble_files = list(self.model_dir.glob("ensemble_*.joblib"))
            if ensemble_files:
                latest_ensemble = max(ensemble_files, key=lambda p: p.stat().st_mtime)
                try:
                    ensemble_data = joblib.load(str(latest_ensemble))
                    if isinstance(ensemble_data, dict):
                        for model_name in ['random_forest', 'gradient_boosting', 'xgboost', 'lightgbm', 'catboost']:
                            if model_name in ensemble_data:
                                self.models[model_name] = ensemble_data[model_name]
                        self.artifact_info = ensemble_data
                        if 'model_weights' in ensemble_data and isinstance(ensemble_data['model_weights'], dict):
                            self.model_weights = ensemble_data['model_weights']
                        self.model_version = str(ensemble_data.get('timestamp', latest_ensemble.stem))
                        self.latest_artifact_mtime = latest_ensemble.stat().st_mtime
                        self.latest_artifact_name = latest_ensemble.name
                        loaded_from_ensemble = True
                        logger.info(f"Loaded ensemble: {latest_ensemble.name} with {len(self.models)} models")
                except Exception as e:
                    logger.error(f"Failed to load ensemble: {e}")

        # Fallback: find individual model files
        if not self.models:
            model_types = ['random_forest', 'gradient_boosting', 'xgboost', 'lightgbm', 'catboost']
            model_paths = {}

            for model_type in model_types:
                pattern = f"{model_type}_*.joblib"
                matching_files = list(self.model_dir.glob(pattern))

                if matching_files:
                    latest_model = max(matching_files, key=lambda p: p.stat().st_mtime)
                    model_paths[model_type] = str(latest_model)

            if model_paths:
                for model_name, path in model_paths.items():
                    try:
                        model = joblib.load(path)
                        self.models[model_name] = model
                        logger.info(f"Loaded model: {model_name} from {path}")
                    except Exception as e:
                        logger.error(f"Failed to load {model_name}: {e}")

        # Find latest preprocessor
        preprocessor_files = list(self.model_dir.glob("preprocessor_*.joblib"))
        preprocessor_path = None
        if preprocessor_files:
            preprocessor_path = str(max(preprocessor_files, key=lambda p: p.stat().st_mtime))
            try:
                preprocessor_data = joblib.load(preprocessor_path)
                if isinstance(preprocessor_data, dict):
                    self.preprocessor = preprocessor_data.get('preprocessor', preprocessor_data)
                    self.feature_cols = preprocessor_data.get('feature_cols', None)
                else:
                    self.preprocessor = preprocessor_data
                logger.info(f"Loaded preprocessor from {preprocessor_path}")
            except Exception as e:
                logger.error(f"Failed to load preprocessor: {e}")

        if self.models:
            # If weights not provided by artifact, default to equal
            if not self.model_weights:
                self.set_equal_weights()
            logger.info(f"Loaded {len(self.models)} models for ensemble")
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

    def _get_latest_ensemble_file(self) -> Optional[Path]:
        """Return newest ensemble artifact (tuned preferred)."""
        tuned_files = list(self.model_dir.glob("ensemble_tuned_*.joblib"))
        if tuned_files:
            return max(tuned_files, key=lambda p: p.stat().st_mtime)

        ensemble_files = list(self.model_dir.glob("ensemble_*.joblib"))
        if ensemble_files:
            return max(ensemble_files, key=lambda p: p.stat().st_mtime)

        return None

    def refresh_if_newer(self) -> None:
        """Reload models if a newer ensemble artifact appears on disk."""
        if not self.model_dir.exists():
            return

        latest_file = self._get_latest_ensemble_file()
        if not latest_file:
            return

        latest_mtime = latest_file.stat().st_mtime
        if self.latest_artifact_mtime is None or latest_mtime > self.latest_artifact_mtime:
            logger.info(f"Detected newer ensemble artifact: {latest_file.name}; reloading")
            self.load_latest_models()

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
                    pred_result = model.predict(features)
                    # Handle both scalar and array results
                    prediction = float(pred_result[0]) if isinstance(pred_result, np.ndarray) else float(pred_result)

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
