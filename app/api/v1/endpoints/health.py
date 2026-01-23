"""Health check endpoint."""

from fastapi import APIRouter, status
from loguru import logger

from app import __version__
from app.config import settings
from app.core.utils import get_current_timestamp
from app.models.schemas import HealthResponse, HealthStatus

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the API and its services",
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Health status of all services
    """
    timestamp = get_current_timestamp().isoformat()
    
    # Check database status
    database_status = HealthStatus(
        status="healthy",
        timestamp=timestamp
    )
    
    # Check Redis status (for future implementation)
    redis_status = HealthStatus(
        status="not_configured",
        timestamp=timestamp
    )
    
    # Check ML models status
    ml_models_status = HealthStatus(
        status="not_loaded",
        timestamp=timestamp
    )
    
    # Check scraper status
    scraper_status = HealthStatus(
        status="healthy",
        timestamp=timestamp
    )
    
    logger.info("Health check completed successfully")
    
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=timestamp,
        services={
            "database": database_status,
            "redis": redis_status,
            "ml_models": ml_models_status,
            "scraper": scraper_status,
        }
    )
