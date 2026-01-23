"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    predictions,
    market_data,
    inventory,
    alerts,
    model_metrics,
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(predictions.router, tags=["Predictions"])
api_router.include_router(market_data.router, tags=["Market Data"])
api_router.include_router(inventory.router, tags=["Inventory"])
api_router.include_router(alerts.router, tags=["Alerts"])
api_router.include_router(model_metrics.router, tags=["Model Metrics"])
