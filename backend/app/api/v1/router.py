"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    predictions,
    market_data,
    inventory,
    alerts,
    buysell_alerts,
    model_metrics,
    scheduler,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(predictions.router, tags=["Predictions"])
api_router.include_router(market_data.router, tags=["Market Data"])
api_router.include_router(inventory.router, tags=["Inventory"])
api_router.include_router(alerts.router, tags=["Alerts"])
api_router.include_router(buysell_alerts.router, tags=["Buy/Sell Alerts"])
api_router.include_router(model_metrics.router, tags=["Model Metrics"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["Scheduler"])
