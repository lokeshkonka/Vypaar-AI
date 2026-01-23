"""Model performance metrics endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from app.api.dependencies import (
    get_prediction_metrics_repo,
    get_predictor,
)
from app.models.schemas import ModelMetricsResponse
from app.database.repositories import PredictionMetricsRepository
from app.ml.predictor import AgriculturalPredictor
from app.core.utils import get_current_timestamp


router = APIRouter(prefix="/model", tags=["model-metrics"])


@router.get("/metrics", response_model=List[ModelMetricsResponse])
async def get_model_metrics(
    model_name: Optional[str] = None,
    latest_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    metrics_repo: PredictionMetricsRepository = Depends(get_prediction_metrics_repo),
) -> List[ModelMetricsResponse]:
    """
    Get model performance metrics.
    
    Returns accuracy, RMSE, MAE, R², MAPE for individual models and ensemble.
    
    Args:
        model_name: Filter by model name (xgboost, lightgbm, random_forest, ensemble)
        latest_only: Return only latest metrics per model
        skip: Pagination offset
        limit: Maximum results
    """
    try:
        if model_name and latest_only:
            # Get latest metrics for specific model
            metrics = await metrics_repo.get_latest_metrics(model_name=model_name)
            metrics = [metrics] if metrics else []
        elif model_name:
            # Get all metrics for specific model
            metrics = await metrics_repo.get_by_model(model_name=model_name)
        else:
            # Get all metrics
            metrics = await metrics_repo.get_all(skip=skip, limit=limit)

        # If latest_only and no specific model, get latest for each model
        if latest_only and not model_name:
            model_names = set(m.model_name for m in metrics)
            latest_metrics = []
            for name in model_names:
                latest = await metrics_repo.get_latest_metrics(model_name=name)
                if latest:
                    latest_metrics.append(latest)
            metrics = latest_metrics

        return [
            ModelMetricsResponse(
                id=m.id,
                model_name=m.model_name,
                model_version=m.model_version,
                accuracy=m.accuracy,
                rmse=m.rmse,
                mae=m.mae,
                r2_score=m.r2_score,
                mape=m.mape,
                precision=m.precision,
                recall=m.recall,
                f1_score=m.f1_score,
                feature_importance=m.feature_importance,
                training_samples=m.training_samples,
                test_samples=m.test_samples,
                training_date=m.training_date,
                hyperparameters=m.hyperparameters,
                cross_validation_scores=m.cross_validation_scores,
                created_at=m.created_at,
            )
            for m in metrics
        ]

    except Exception as e:
        logger.error(f"Error getting model metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/metrics/{model_name}/latest", response_model=ModelMetricsResponse)
async def get_latest_model_metrics(
    model_name: str,
    metrics_repo: PredictionMetricsRepository = Depends(get_prediction_metrics_repo),
) -> ModelMetricsResponse:
    """Get latest metrics for a specific model."""
    try:
        metrics = await metrics_repo.get_latest_metrics(model_name=model_name)
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No metrics found for model {model_name}"
            )

        return ModelMetricsResponse(
            id=metrics.id,
            model_name=metrics.model_name,
            model_version=metrics.model_version,
            accuracy=metrics.accuracy,
            rmse=metrics.rmse,
            mae=metrics.mae,
            r2_score=metrics.r2_score,
            mape=metrics.mape,
            precision=metrics.precision,
            recall=metrics.recall,
            f1_score=metrics.f1_score,
            feature_importance=metrics.feature_importance,
            training_samples=metrics.training_samples,
            test_samples=metrics.test_samples,
            training_date=metrics.training_date,
            hyperparameters=metrics.hyperparameters,
            cross_validation_scores=metrics.cross_validation_scores,
            created_at=metrics.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest model metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_model_status(
    predictor: AgriculturalPredictor = Depends(get_predictor),
):
    """
    Get current status of loaded ML models.
    
    Returns information about:
    - Loaded models
    - Model weights
    - Ensemble configuration
    - Prediction statistics
    """
    try:
        ensemble_status = predictor.get_ensemble_status()
        prediction_stats = predictor.get_prediction_statistics()

        return {
            'ensemble_status': ensemble_status,
            'prediction_statistics': prediction_stats,
            'timestamp': get_current_timestamp(),
        }

    except Exception as e:
        logger.error(f"Error getting model status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
