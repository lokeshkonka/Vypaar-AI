"""CLI tool for training ML models."""

import argparse
import sys
from pathlib import Path
from typing import Tuple, Dict, Any
from loguru import logger
import numpy as np
import pandas as pd
import joblib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database.connection import init_sync_db, get_sync_session
from app.database.models import Commodity, Market, MarketPrice
from app.database.repositories import (
    MarketPriceRepository,
    PredictionMetricsRepository,
)
from app.ml.preprocessor import DataPreprocessor
from app.ml.trainer import ModelTrainer
from app.ml.ensemble import EnsembleManager
from app.ml.predictor import AgriculturalPredictor


def load_training_data(
    commodity_id: int = None, market_id: int = None, days: int = 365
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Load training data from database.

    Args:
        commodity_id: Optional commodity ID to filter
        market_id: Optional market ID to filter
        days: Number of days of historical data

    Returns:
        Tuple of (features, target, metadata_df)
    """
    logger.info(f"Loading training data (last {days} days)...")

    # Initialize database
    init_sync_db()
    session = next(get_sync_session())

    try:
        # Query market prices
        query = session.query(MarketPrice)

        if commodity_id:
            query = query.filter(MarketPrice.commodity_id == commodity_id)

        if market_id:
            query = query.filter(MarketPrice.market_id == market_id)

        # Filter by date range
        from datetime import datetime, timedelta

        start_date = datetime.now().date() - timedelta(days=days)
        query = query.filter(MarketPrice.date >= start_date)

        # Order by date
        prices = query.order_by(MarketPrice.date).all()

        logger.info(f"Loaded {len(prices)} price records")

        # Convert to DataFrame
        data_list = []
        for price in prices:
            data_list.append(
                {
                    'date': price.date,
                    'commodity_id': price.commodity_id,
                    'market_id': price.market_id,
                    'price': price.price,
                    'min_price': price.min_price,
                    'max_price': price.max_price,
                    'modal_price': price.modal_price,
                    'arrival': price.arrival or 0,
                }
            )

        df = pd.DataFrame(data_list)

        if len(df) == 0:
            logger.error("No training data available")
            return None, None, None

        # Create features
        preprocessor = DataPreprocessor()
        features, target = preprocessor.prepare_training_data(
            df,
            target_col='price',
            date_col='date',
            numeric_cols=['min_price', 'max_price', 'modal_price', 'arrival', 'commodity_id', 'market_id'],
        )

        return features, target, df

    finally:
        session.close()


def train_models(
    commodity_id: int = None,
    market_id: int = None,
    models: list = None,
    test_size: float = 0.2,
    retrain: bool = False,
) -> Dict[str, Any]:
    """
    Train ensemble models.

    Args:
        commodity_id: Optional commodity ID
        market_id: Optional market ID
        models: List of models to train
        test_size: Fraction of data for testing
        retrain: Whether to retrain existing models

    Returns:
        Dictionary with training results
    """
    if models is None:
        models = ['xgboost', 'lightgbm', 'catboost', 'random_forest']

    # Load data
    X, y, df = load_training_data(commodity_id, market_id)

    if X is None:
        logger.error("Failed to load training data")
        return None

    logger.info(f"Training data shape: {X.shape}")

    # Train-test split (time-based)
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    logger.info(
        f"Train set: {X_train.shape[0]} samples, Test set: {X_test.shape[0]} samples"
    )

    # Initialize trainer
    preprocessor = DataPreprocessor()
    trainer = ModelTrainer(preprocessor)

    # Train ensemble
    results = trainer.train_ensemble(
        X_train, y_train, X_test, y_test, models_to_train=models
    )

    # Save models
    version = None
    saved_paths = trainer.save_all_models(version)
    preprocessor_path = trainer.save_preprocessor(version)

    logger.info(f"Saved {len(saved_paths)} models")
    logger.info(f"Saved preprocessor to {preprocessor_path}")

    return {
        'results': results,
        'saved_paths': saved_paths,
        'preprocessor_path': preprocessor_path,
        'metrics': trainer.metrics,
    }


def evaluate_predictions(
    commodity_id: int = None, market_id: int = None, days: int = 30
) -> Dict[str, Any]:
    """
    Evaluate model predictions.

    Args:
        commodity_id: Optional commodity ID
        market_id: Optional market ID
        days: Number of recent days to evaluate

    Returns:
        Evaluation results
    """
    logger.info("Evaluating predictions...")

    # Load predictor
    predictor = AgriculturalPredictor()
    predictor.load_latest_models()

    if not predictor.ensemble.models:
        logger.error("No trained models found")
        return None

    # Load evaluation data
    X, y, df = load_training_data(commodity_id, market_id, days=days)

    if X is None:
        logger.error("Failed to load evaluation data")
        return None

    # Make predictions
    predictions_result = predictor.batch_predict(X, include_individual=True)

    # Calculate metrics
    y_pred = np.array([p['prediction'] for p in predictions_result])
    metrics = predictor.evaluate_predictions(y, y_pred)

    logger.info(f"Evaluation metrics: {metrics}")

    return {
        'metrics': metrics,
        'predictions': predictions_result,
        'num_samples': len(y),
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Train ML models for agricultural price prediction")

    parser.add_argument(
        '--action',
        choices=['train', 'evaluate', 'predict'],
        default='train',
        help='Action to perform',
    )
    parser.add_argument('--model', help='Specific model to train (xgboost, lightgbm, catboost, random_forest)')
    parser.add_argument('--commodity', type=int, help='Commodity ID to train on')
    parser.add_argument('--market', type=int, help='Market ID to train on')
    parser.add_argument('--days', type=int, default=365, help='Days of historical data to use')
    parser.add_argument('--test-size', type=float, default=0.2, help='Fraction of data for testing')
    parser.add_argument('--retrain', action='store_true', help='Retrain existing models')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logger.enable('app')
    else:
        logger.disable('app')

    logger.info(f"Starting {args.action} action")
    logger.info(f"Settings: commodity={args.commodity}, market={args.market}, days={args.days}")

    try:
        if args.action == 'train':
            models = [args.model] if args.model else None
            result = train_models(
                commodity_id=args.commodity,
                market_id=args.market,
                models=models,
                test_size=args.test_size,
                retrain=args.retrain,
            )

            if result:
                logger.info("Training completed successfully")
                logger.info(f"Results: {result['metrics']}")
                print("\n✅ Training completed successfully!")
                print(f"Saved models: {list(result['saved_paths'].keys())}")

        elif args.action == 'evaluate':
            result = evaluate_predictions(
                commodity_id=args.commodity, market_id=args.market, days=args.days
            )

            if result:
                logger.info("Evaluation completed successfully")
                print("\n✅ Evaluation completed successfully!")
                print(f"Metrics: {result['metrics']}")

        elif args.action == 'predict':
            predictor = AgriculturalPredictor()
            predictor.load_latest_models()

            print("\n✅ Predictor loaded successfully!")
            print(f"Ensemble status: {predictor.get_ensemble_status()}")

    except Exception as e:
        logger.error(f"Error during {args.action}: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
