"""Dependency injection for API endpoints."""

from typing import AsyncGenerator, Generator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from loguru import logger

from app.database.connection import get_async_session
from app.database.repositories import (
    CommodityRepository,
    MarketRepository,
    MarketPriceRepository,
    AlertRepository,
    InventoryRepository,
    PredictionMetricsRepository,
    PredictionRepository,
    DiscussionRepository,
    WatchlistRepository,
    MarketTrendAnalysisRepository,
)
from app.ml.predictor import AgriculturalPredictor


# Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in get_async_session():
        yield session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Alias for async database session dependency."""
    async for session in get_async_session():
        yield session


async def get_current_user(request: Request) -> dict:
    """Get current user from Authorization header.

    This is a lightweight placeholder for Clerk integration.
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else None
    if not token:
        return {}
    return {"user_id": token, "token": token}


# Repository dependencies
async def get_commodity_repo(db: AsyncSession = Depends(get_db)) -> CommodityRepository:
    """Get commodity repository."""
    return CommodityRepository(db)


async def get_market_repo(db: AsyncSession = Depends(get_db)) -> MarketRepository:
    """Get market repository."""
    return MarketRepository(db)


async def get_market_price_repo(db: AsyncSession = Depends(get_db)) -> MarketPriceRepository:
    """Get market price repository."""
    return MarketPriceRepository(db)


async def get_alert_repo(db: AsyncSession = Depends(get_db)) -> AlertRepository:
    """Get alert repository."""
    return AlertRepository(db)


async def get_inventory_repo(db: AsyncSession = Depends(get_db)) -> InventoryRepository:
    """Get inventory repository."""
    return InventoryRepository(db)


async def get_prediction_metrics_repo(
    db: AsyncSession = Depends(get_db)
) -> PredictionMetricsRepository:
    """Get prediction metrics repository."""
    return PredictionMetricsRepository(db)


async def get_prediction_repo(db: AsyncSession = Depends(get_db)) -> PredictionRepository:
    """Get prediction repository."""
    return PredictionRepository(db)


async def get_discussion_repo(db: AsyncSession = Depends(get_db)) -> DiscussionRepository:
    """Get discussion repository."""
    return DiscussionRepository(db)


async def get_watchlist_repo(db: AsyncSession = Depends(get_db)) -> WatchlistRepository:
    """Get watchlist repository."""
    return WatchlistRepository(db)


async def get_market_trend_analysis_repo(
    db: AsyncSession = Depends(get_db)
) -> MarketTrendAnalysisRepository:
    """Get market trend analysis repository."""
    return MarketTrendAnalysisRepository(db)


# ML Predictor dependency (singleton)
_predictor_instance = None


@lru_cache()
def get_predictor() -> AgriculturalPredictor:
    """
    Get ML predictor instance (singleton).
    
    Returns:
        AgriculturalPredictor: Predictor instance
    """
    global _predictor_instance
    
    if _predictor_instance is None:
        logger.info("Initializing AgriculturalPredictor singleton")
        _predictor_instance = AgriculturalPredictor()
        
        # Try to load latest models
        try:
            _predictor_instance.load_latest_models()
            logger.info("Loaded latest ML models")
        except Exception as e:
            logger.warning(f"Could not load ML models: {e}")
    
    return _predictor_instance


def reset_predictor() -> None:
    """Reset predictor instance (for testing or retraining)."""
    global _predictor_instance
    _predictor_instance = None
    get_predictor.cache_clear()
    logger.info("Predictor instance reset")
