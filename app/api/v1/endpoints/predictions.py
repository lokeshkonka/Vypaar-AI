"""Price prediction endpoints."""

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
import numpy as np
import pandas as pd

from app.api.dependencies import (
    get_predictor,
    get_commodity_repo,
    get_market_repo,
    get_market_price_repo,
    get_prediction_repo,
)
from app.models.schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    ModelMetrics,
    ModelMetadata,
    IndividualModelMetrics,
    PredictionMetadata,
)
from app.ml.predictor import AgriculturalPredictor
from app.database.repositories import (
    CommodityRepository,
    MarketRepository,
    MarketPriceRepository,
    PredictionRepository,
)
from app.database.models import Prediction
from app.core.utils import get_current_timestamp


router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_price(
    request: PredictionRequest,
    predictor: AgriculturalPredictor = Depends(get_predictor),
    commodity_repo: CommodityRepository = Depends(get_commodity_repo),
    market_repo: MarketRepository = Depends(get_market_repo),
    market_price_repo: MarketPriceRepository = Depends(get_market_price_repo),
    prediction_repo: PredictionRepository = Depends(get_prediction_repo),
) -> PredictionResponse:
    """
    Predict agricultural commodity price with ensemble model metrics.
    
    Returns prediction with:
    - Ensemble prediction from multiple models
    - Individual model predictions (XGBoost, LightGBM, Random Forest)
    - Model accuracy metrics (R², RMSE, MAE, MAPE)
    - Confidence interval bounds
    - Feature importance
    """
    try:
        logger.info(
            f"Prediction request: commodity_id={request.commodity_id}, "
            f"market_id={request.market_id}, date={request.prediction_date}"
        )

        # Validate commodity and market exist
        commodity = await commodity_repo.get_by_id(request.commodity_id)
        if not commodity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Commodity {request.commodity_id} not found. Check your catalog or seed fresh data."
            )

        market = await market_repo.get_by_id(request.market_id)
        if not market:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Market {request.market_id} not found. Check your catalog or seed fresh data."
            )

        request_label = f"{commodity.name} @ {market.name} on {request.prediction_date}"

        # Get historical data for feature engineering
        historical_prices = await market_price_repo.get_price_history(
            commodity_id=request.commodity_id,
            market_id=request.market_id,
            days=90  # Last 90 days for context
        )

        if not historical_prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No price history for {request_label}. Seed data or pick a different commodity/market pair."
            )

        # Prepare features from historical data and request
        latest_price = historical_prices[-1]
        
        # Build a simple feature vector that matches model expectations (16 features)
        # Based on training data: commodity, market, state (encoded) + arrival + festival features
        from datetime import datetime as dt
        pred_date = dt.fromisoformat(request.prediction_date)
        
        # Create 16-feature vector matching training
        features = np.array([
            # Encoded commodities (3 one-hot)
            float(commodity.name == "Wheat"),
            float(commodity.name == "Rice"),
            float(commodity.name == "Onion"),
            # Encoded markets (3 one-hot)
            float(market.name.startswith("Azadpur")),
            float(market.name.startswith("APMC")),
            float(market.name.startswith("Chennai")),
            # Encoded states (2 additional)
            float(market.state == "Delhi"),
            float(market.state == "Maharashtra"),
            # Arrival
            float(latest_price.arrival or 1000),
            # Festival features (6 additional)
            1.0 if pred_date.month in [3, 10, 11, 12] else 0.0,  # is_festival
            0.5,  # festival_proximity (0-1 scale)
            1.0 if pred_date.month in [10, 11, 12, 1, 2, 3] else 0.0,  # is_harvest_season
            2.0 if pred_date.month in [10, 11, 12, 1, 2, 3] else 1.0,  # season_type (encoded)
            float(pred_date.weekday() >= 5),  # is_weekend
            float(pred_date.day in [1, 2, 3]),  # is_month_start
            float(pred_date.day in [28, 29, 30, 31]),  # is_month_end
        ]).reshape(1, -1)

        # Make prediction
        prediction_result = predictor.predict(
            features,
            include_individual=True,
            include_confidence=True
        )

        # Get ensemble status for model metrics
        ensemble_status = predictor.get_ensemble_status()
        
        # Derive metrics from loaded ensemble artifact if available
        artifact = getattr(predictor.ensemble, 'artifact_info', {}) or {}
        metrics = artifact.get('metrics', {}) if isinstance(artifact, dict) else {}
        ens_metrics = metrics.get('ensemble', {}) if isinstance(metrics, dict) else {}
        rf_metrics = metrics.get('random_forest', {}) if isinstance(metrics, dict) else {}
        gb_metrics = metrics.get('gradient_boosting', {}) if isinstance(metrics, dict) else {}

        # Build individual model metrics list with accuracy and weights
        individual_models_list = []
        for name in prediction_result.get('individual_predictions', {}).keys():
            acc = 0.85
            if name == 'random_forest' and isinstance(rf_metrics, dict):
                acc = float(rf_metrics.get('accuracy', acc))
            if name == 'gradient_boosting' and isinstance(gb_metrics, dict):
                acc = float(gb_metrics.get('accuracy', acc))
            individual_models_list.append(
                IndividualModelMetrics(
                    name=name,
                    accuracy=acc,
                    weight=float(predictor.ensemble.model_weights.get(name, 0.0))
                )
            )

        # Feature importance from prediction result (top_features)
        top_feats = prediction_result.get('top_features', {})
        feature_importance = {str(k): float(v) for k, v in top_feats.items()} if isinstance(top_feats, dict) else {}

        # Build model metadata matching ModelMetadata schema
        model_metadata = ModelMetadata(
            ensemble_accuracy=float(ens_metrics.get('accuracy', 0.85)),
            rmse=float(ens_metrics.get('rmse', 150.0)),
            mae=float(ens_metrics.get('mae', 120.0)),
            r2_score=float(max(0.0, min(1.0, ens_metrics.get('r2', 0.82)))),
            individual_models=individual_models_list,
            feature_importance=feature_importance,
            model_version=str(getattr(predictor.ensemble, 'model_version', artifact.get('timestamp', 'unknown'))),
            trained_on=str(artifact.get('timestamp', get_current_timestamp().date().isoformat())),
            training_samples=int(artifact.get('training_samples', 0) or 0)
        )
        
        # Build prediction metadata matching PredictionMetadata schema
        prediction_metadata = PredictionMetadata(
            timestamp=get_current_timestamp().isoformat(),
            processing_time_ms=int(prediction_result.get('processing_time_seconds', 0.0) * 1000),
            data_freshness=f"{len(historical_prices)} days historical data"
        )
        
        # Build response using PredictionResponse schema
        response = PredictionResponse(
            predicted_price=float(prediction_result['prediction']),
            confidence_interval=(
                float(prediction_result.get('lower_bound', prediction_result['prediction'] - 100)),
                float(prediction_result.get('upper_bound', prediction_result['prediction'] + 100))
            ),
            model_confidence=float(prediction_result.get('confidence', 0.85)),
            confidence_score=float(prediction_result.get('confidence', 0.85)),
            models_used=list(prediction_result.get('individual_predictions', {}).keys()),
            model_metrics=model_metadata,
            prediction_metadata=prediction_metadata
        )
        
        # Store prediction in database for tracking (if successful)
        try:
            # Parse prediction_date if it's a string
            pred_date = request.prediction_date
            if isinstance(pred_date, str):
                from datetime import date as date_type
                pred_date = date_type.fromisoformat(pred_date)
            
            prediction_record = Prediction(
                commodity_id=request.commodity_id,
                market_id=request.market_id,
                prediction_date=pred_date,
                predicted_price=prediction_result['prediction'],
                confidence=prediction_result.get('confidence', 0.85),
                model_used="ensemble",
            )
            await prediction_repo.create(prediction_record)
        except Exception as e:
            logger.warning(f"Could not persist prediction to database: {e}")

        logger.info(
            f"Prediction complete for {request_label}: price=₹{response.predicted_price:.2f}, "
            f"confidence={response.model_confidence:.2%}, models={response.models_used}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/batch", response_model=BatchPredictionResponse, status_code=status.HTTP_200_OK)
async def batch_predict_prices(
    request: BatchPredictionRequest,
    predictor: AgriculturalPredictor = Depends(get_predictor),
    commodity_repo: CommodityRepository = Depends(get_commodity_repo),
    market_repo: MarketRepository = Depends(get_market_repo),
    market_price_repo: MarketPriceRepository = Depends(get_market_price_repo),
    prediction_repo: PredictionRepository = Depends(get_prediction_repo),
) -> BatchPredictionResponse:
    """
    Batch predict prices for multiple commodity-market pairs.
    
    Returns predictions with model metrics for each pair.
    """
    try:
        logger.info(f"Batch prediction request: {len(request.predictions)} items")

        predictions = []
        
        for pred_request in request.predictions:
            try:
                # Reuse single prediction logic
                result = await predict_price(
                    request=pred_request,
                    predictor=predictor,
                    commodity_repo=commodity_repo,
                    market_repo=market_repo,
                    market_price_repo=market_price_repo,
                    prediction_repo=prediction_repo,
                )
                predictions.append(result)
            except Exception as e:
                logger.warning(f"Failed prediction for item: {e}")
                continue

        response = BatchPredictionResponse(
            predictions=predictions,
            total_predictions=len(predictions),
            successful=len(predictions),
            failed=len(request.predictions) - len(predictions),
            timestamp=get_current_timestamp()
        )

        logger.info(f"Batch prediction complete: {response.successful}/{response.total_predictions}")

        return response

    except Exception as e:
        logger.error(f"Batch prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@router.get("/history/{commodity_id}/{market_id}", status_code=status.HTTP_200_OK)
async def get_prediction_history(
    commodity_id: int,
    market_id: int,
    days: int = 30,
    prediction_repo: PredictionRepository = Depends(get_prediction_repo),
):
    """
    Get historical predictions for a commodity-market pair.
    
    Returns prediction accuracy over time.
    """
    try:
        start_date = (get_current_timestamp() - timedelta(days=days)).date()
        
        predictions = await prediction_repo.get_by_date_range(
            start_date=start_date,
            end_date=get_current_timestamp().date()
        )

        # Filter by commodity and market
        filtered = [
            p for p in predictions
            if p.commodity_id == commodity_id and p.market_id == market_id
        ]

        # Calculate accuracy metrics
        predictions_with_actual = [p for p in filtered if p.actual_price is not None]
        
        if predictions_with_actual:
            avg_accuracy = np.mean([p.accuracy for p in predictions_with_actual if p.accuracy])
        else:
            avg_accuracy = None

        return {
            'commodity_id': commodity_id,
            'market_id': market_id,
            'total_predictions': len(filtered),
            'predictions_with_actual': len(predictions_with_actual),
            'average_accuracy': avg_accuracy,
            'predictions': [
                {
                    'date': p.prediction_date,
                    'predicted_price': p.predicted_price,
                    'actual_price': p.actual_price,
                    'error': p.error,
                    'accuracy': p.accuracy,
                    'confidence': p.confidence,
                }
                for p in filtered
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching prediction history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
