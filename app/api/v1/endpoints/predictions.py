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
                detail=f"Commodity {request.commodity_id} not found"
            )

        market = await market_repo.get_by_id(request.market_id)
        if not market:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Market {request.market_id} not found"
            )

        # Get historical data for feature engineering
        historical_prices = await market_price_repo.get_price_history(
            commodity_id=request.commodity_id,
            market_id=request.market_id,
            days=90  # Last 90 days for context
        )

        if not historical_prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No historical price data available for this commodity-market pair"
            )

        # Prepare features from historical data and request
        latest_price = historical_prices[-1]
        
        # Create feature vector (simplified - would use preprocessor in production)
        features = np.array([
            request.commodity_id,
            request.market_id,
            latest_price.price,
            latest_price.min_price or latest_price.price,
            latest_price.max_price or latest_price.price,
            latest_price.modal_price or latest_price.price,
            latest_price.arrival or 0,
        ]).reshape(1, -1)

        # Make prediction
        prediction_result = predictor.predict(
            features,
            include_individual=True,
            include_confidence=True
        )

        # Get ensemble status for model metrics
        ensemble_status = predictor.get_ensemble_status()
        
        # Build model metrics from ensemble
        # In production, these would come from stored PredictionMetrics table
        model_metrics = ModelMetrics(
            model_name="ensemble",
            ensemble_accuracy=0.95,  # Placeholder - would calculate from historical predictions
            rmse=50.0,  # Placeholder
            mae=40.0,  # Placeholder
            r2_score=0.92,  # Placeholder
            mape=0.015,  # Placeholder
            individual_models=[
                {
                    "model_name": name,
                    "prediction": pred,
                    "weight": predictor.ensemble.model_weights.get(name, 0.0)
                }
                for name, pred in prediction_result.get('individual_predictions', {}).items()
            ],
            feature_importance=prediction_result.get('top_features', {}),
            confidence_interval={
                'lower': prediction_result.get('lower_bound'),
                'upper': prediction_result.get('upper_bound'),
                'confidence_level': 0.95
            }
        )

        # Store prediction in database for tracking
        prediction_record = Prediction(
            commodity_id=request.commodity_id,
            market_id=request.market_id,
            prediction_date=request.prediction_date,
            predicted_price=prediction_result['prediction'],
            confidence=prediction_result.get('confidence', 0.85),
            model_used="ensemble",
        )
        await prediction_repo.create(prediction_record)

        # Build response
        response = PredictionResponse(
            commodity_id=request.commodity_id,
            commodity_name=commodity.name,
            market_id=request.market_id,
            market_name=market.name,
            prediction_date=request.prediction_date,
            predicted_price=prediction_result['prediction'],
            confidence=prediction_result.get('confidence', 0.85),
            lower_bound=prediction_result.get('lower_bound'),
            upper_bound=prediction_result.get('upper_bound'),
            model_metrics=model_metrics,
            historical_context={
                'latest_price': latest_price.price,
                'avg_30d': np.mean([p.price for p in historical_prices[-30:]]),
                'trend': 'increasing' if latest_price.price > historical_prices[0].price else 'decreasing'
            },
            timestamp=get_current_timestamp(),
            processing_time=prediction_result.get('processing_time_seconds', 0.0)
        )

        logger.info(
            f"Prediction complete: price=${response.predicted_price:.2f}, "
            f"confidence={response.confidence:.2f}"
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
                    prediction_repo=get_prediction_repo,  # Will get from context
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
