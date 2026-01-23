"""FastAPI main application."""

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app import __version__
from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import AgriTechException
from app.core.logging_config import setup_logging
from app.core.utils import get_current_timestamp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Industry-level Agricultural Market Data Analysis API with ML predictions",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = time.time()
    
    # Process request first
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log after processing (non-blocking)
    try:
        logger.opt(lazy=True).info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )
    except Exception:
        pass  # Don't let logging errors break requests
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = settings.app_version
    
    return response


# Exception handlers
@app.exception_handler(AgriTechException)
async def agritech_exception_handler(request: Request, exc: AgriTechException):
    """Handle custom application exceptions."""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "url": str(request.url),
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "timestamp": get_current_timestamp().isoformat(),
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(
        f"Validation error",
        extra={
            "errors": exc.errors(),
            "url": str(request.url),
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": {"errors": exc.errors()},
            "timestamp": get_current_timestamp().isoformat(),
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(
        f"Unexpected error: {str(exc)}",
        extra={
            "url": str(request.url),
            "exception_type": type(exc).__name__,
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"error": str(exc)} if settings.debug else {},
            "timestamp": get_current_timestamp().isoformat(),
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "timestamp": get_current_timestamp().isoformat(),
    }


# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
