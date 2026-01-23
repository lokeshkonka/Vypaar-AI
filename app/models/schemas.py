"""Pydantic schemas for request/response models."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# Enums
class AlertType(str, Enum):
    """Alert type enumeration."""

    PRICE_THRESHOLD = "PRICE_THRESHOLD"
    INVENTORY_LOW = "INVENTORY_LOW"
    INVENTORY_OVERSTOCK = "INVENTORY_OVERSTOCK"
    PRICE_VOLATILITY = "PRICE_VOLATILITY"
    TREND_CHANGE = "TREND_CHANGE"
    EXPIRY_WARNING = "EXPIRY_WARNING"


class AlertPriority(str, Enum):
    """Alert priority enumeration."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertStatus(str, Enum):
    """Alert status enumeration."""

    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class InventoryAction(str, Enum):
    """Inventory action enumeration."""

    RESTOCK = "RESTOCK"
    REDUCE = "REDUCE"
    MAINTAIN = "MAINTAIN"
    URGENT_RESTOCK = "URGENT_RESTOCK"


class TrendDirection(str, Enum):
    """Price trend direction."""

    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:
        from_attributes = True
        populate_by_name = True


# Model Metrics Schemas
class ModelMetrics(BaseSchema):
    """Model performance metrics."""

    accuracy: float = Field(..., ge=0, le=1, description="Model accuracy")
    rmse: float = Field(..., ge=0, description="Root Mean Square Error")
    mae: float = Field(..., ge=0, description="Mean Absolute Error")
    r2_score: float = Field(..., ge=0, le=1, description="R² score")
    mape: Optional[float] = Field(None, ge=0, description="Mean Absolute Percentage Error")


class IndividualModelMetrics(BaseSchema):
    """Metrics for individual model in ensemble."""

    name: str
    accuracy: float = Field(..., ge=0, le=1)
    weight: float = Field(..., ge=0, le=1)
    status: str = "ACTIVE"


class FeatureImportance(BaseSchema):
    """Feature importance scores."""

    historical_price: float = 0.0
    season: float = 0.0
    market_arrival: float = 0.0
    state: float = 0.0
    day_of_week: float = 0.0


class ModelMetadata(BaseSchema):
    """Comprehensive model metadata."""

    ensemble_accuracy: float
    rmse: float
    mae: float
    r2_score: float
    individual_models: list[IndividualModelMetrics]
    feature_importance: dict[str, float]
    model_version: str
    trained_on: str
    training_samples: int


class PredictionMetadata(BaseSchema):
    """Metadata about the prediction."""

    timestamp: str
    processing_time_ms: int
    data_freshness: str


# Health Check Schemas
class HealthStatus(BaseSchema):
    """Health check status."""

    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Check timestamp")


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str = "healthy"
    version: str
    timestamp: str
    services: dict[str, HealthStatus]


# Market Data Schemas
class MarketRequest(BaseSchema):
    """Request for market data."""

    state: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)


class CommodityRequest(BaseSchema):
    """Request for commodity data."""

    category: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)


class MarketDataRequest(BaseSchema):
    """Request for specific market data."""

    market: str
    commodity: str
    date: Optional[str] = None


class MarketDataResponse(BaseSchema):
    """Market data response."""

    market: str
    commodity: str
    price: float
    arrival: Optional[float] = None
    date: str
    state: Optional[str] = None


# Prediction Schemas
class PredictionRequest(BaseSchema):
    """Price prediction request."""

    commodity_id: int = Field(..., description="Commodity ID")
    market_id: int = Field(..., description="Market ID")
    prediction_date: str = Field(..., description="Prediction date (YYYY-MM-DD)")
    features: Optional[dict[str, Any]] = Field(default=None, description="Additional features")


class PredictionResponse(BaseSchema):
    """Price prediction response with comprehensive metrics."""

    predicted_price: float
    confidence_interval: tuple[float, float]
    model_confidence: float = Field(..., ge=0, le=1)
    models_used: list[str]
    model_metrics: ModelMetadata
    prediction_metadata: PredictionMetadata


# Inventory Schemas
class InventorySuggestionRequest(BaseSchema):
    """Request for inventory suggestions."""

    commodity_id: int
    market_id: int
    forecast_days: int = Field(default=30, ge=1, le=90)
    current_stock: Optional[float] = Field(default=None, ge=0)


class InventoryRecommendation(BaseSchema):
    """Inventory recommendation details."""

    action: InventoryAction
    suggested_quantity: float
    optimal_stock_level: float
    urgency: AlertPriority
    estimated_stockout_date: Optional[str] = None


class InventoryForecast(BaseSchema):
    """Inventory demand and price forecast."""

    predicted_demand_30d: float
    predicted_price_trend: TrendDirection
    price_increase_percentage: float


class InventorySuggestionResponse(BaseSchema):
    """Inventory suggestion response."""

    recommendation: InventoryRecommendation
    forecast: InventoryForecast
    reasoning: list[str]
    model_metrics: ModelMetrics


class InventoryOptimization(BaseSchema):
    """Optimized inventory for a commodity."""

    commodity: str
    current_stock: float
    optimal_stock: float
    adjustment: float
    cost_savings: float
    waste_reduction: str


class InventoryOptimizationResponse(BaseSchema):
    """Inventory optimization response."""

    optimized_inventory: list[InventoryOptimization]
    total_cost_savings: float
    model_confidence: float


# Alert Schemas
class AlertConditions(BaseSchema):
    """Alert trigger conditions."""

    price_above: Optional[float] = None
    price_below: Optional[float] = None
    inventory_below: Optional[float] = None
    inventory_above: Optional[float] = None
    volatility_threshold: Optional[float] = None


class AlertConfigRequest(BaseSchema):
    """Request to configure an alert."""

    alert_type: AlertType
    commodity: str
    market: Optional[str] = None
    conditions: AlertConditions
    priority: AlertPriority = AlertPriority.MEDIUM
    channels: list[str] = Field(default=["in_app"])


class AlertConfigResponse(BaseSchema):
    """Alert configuration response."""

    alert_id: str
    status: str
    created_at: str


class Alert(BaseSchema):
    """Alert details."""

    alert_id: str
    type: AlertType
    commodity: str
    market: Optional[str] = None
    message: str
    priority: AlertPriority
    triggered_at: str
    status: AlertStatus
    recommendation: Optional[str] = None
    current_price: Optional[float] = None
    previous_price: Optional[float] = None


class AlertListResponse(BaseSchema):
    """List of alerts with metrics."""

    alerts: list[Alert]
    count: int
    model_metrics: Optional[ModelMetrics] = None


class AlertStatistics(BaseSchema):
    """Alert statistics."""

    total_alerts: int
    critical: int
    high: int
    medium: int
    low: int
    false_positive_rate: float


class AlertHistoryResponse(BaseSchema):
    """Alert history response."""

    alerts: list[Alert]
    statistics: AlertStatistics


# Model Metrics Endpoint Schemas
class DriftDetection(BaseSchema):
    """Model drift detection status."""

    status: str
    last_checked: str
    accuracy_change: float


class PredictionStats(BaseSchema):
    """Prediction statistics."""

    total_predictions: int
    avg_confidence: float
    avg_processing_time_ms: int


class TrainingInfo(BaseSchema):
    """Model training information."""

    last_trained: str
    training_samples: int
    validation_samples: int
    test_samples: int
    training_duration_minutes: int


class ModelMetricsResponse(BaseSchema):
    """Comprehensive model metrics response."""

    model_name: str
    version: str
    performance_metrics: ModelMetrics
    component_models: list[IndividualModelMetrics]
    training_info: TrainingInfo
    feature_importance: dict[str, float]
    drift_detection: DriftDetection
    prediction_stats_7d: PredictionStats


# Trends & Analysis Schemas
class TrendRequest(BaseSchema):
    """Request for trend data."""

    commodity: str
    period: str = Field(default="30d", pattern=r"^\d+[dwmy]$")


class TrendDataPoint(BaseSchema):
    """Single trend data point."""

    date: str
    value: float


class TrendResponse(BaseSchema):
    """Trend response."""

    commodity: str
    period: str
    data: list[TrendDataPoint]
    trend_direction: TrendDirection
    change_percentage: float


class VolatilityResponse(BaseSchema):
    """Market volatility response."""

    market: str
    volatility_index: float
    risk_level: str
    recent_changes: list[dict[str, Any]]


class SeasonalAnalysisResponse(BaseSchema):
    """Seasonal analysis response."""

    commodity: str
    seasonal_patterns: dict[str, float]
    peak_season: str
    low_season: str
    recommendations: list[str]


# Error Response Schema
class ErrorResponse(BaseSchema):
    """Error response."""

    error: str
    message: str
    details: Optional[dict[str, Any]] = None
    timestamp: str


# Additional Request/Response Schemas
class BatchPredictionRequest(BaseSchema):
    """Batch prediction request."""
    
    predictions: list[PredictionRequest]


class BatchPredictionResponse(BaseSchema):
    """Batch prediction response."""
    
    predictions: list[PredictionResponse]
    total_predictions: int
    successful: int
    failed: int
    timestamp: datetime


class CommodityResponse(BaseSchema):
    """Commodity response."""
    
    id: int
    name: str
    category: str
    unit: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class MarketResponse(BaseSchema):
    """Market response."""
    
    id: int
    name: str
    state: str
    district: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class MarketPriceResponse(BaseSchema):
    """Market price response."""
    
    id: int
    commodity_id: int
    commodity_name: str
    market_id: int
    market_name: str
    date: Any  # date type
    price: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    modal_price: Optional[float] = None
    arrival: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class MarketDataListResponse(BaseSchema):
    """Market data list response with pagination."""
    
    data: list[MarketPriceResponse]
    total: int
    skip: int
    limit: int
    timestamp: datetime


class InventoryResponse(BaseSchema):
    """Inventory response."""
    
    id: int
    commodity_id: int
    commodity_name: str
    market_id: int
    market_name: str
    current_stock: float
    optimal_stock: Optional[float] = None
    min_stock: Optional[float] = None
    max_stock: Optional[float] = None
    reorder_point: Optional[float] = None
    last_restocked_at: Optional[datetime] = None
    forecast_demand: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class InventorySuggestionResponse(BaseSchema):
    """Inventory AI suggestion response."""
    
    commodity_id: int
    commodity_name: str
    market_id: int
    market_name: str
    current_stock: float
    optimal_stock: float
    safety_stock: float
    reorder_point: float
    reorder_quantity: float
    needs_reorder: bool
    forecast_demand: float
    forecast_days: int
    days_until_stockout: int
    priority: str
    confidence: float
    reasoning: list[str]
    timestamp: datetime


class InventoryUpdateRequest(BaseSchema):
    """Inventory update request."""
    
    current_stock: Optional[float] = None
    optimal_stock: Optional[float] = None
    reorder_point: Optional[float] = None


class AlertRequest(BaseSchema):
    """Alert creation request."""
    
    alert_type: str
    commodity_id: Optional[int] = None
    market_id: Optional[int] = None
    priority: str
    conditions: dict[str, Any]
    notification_channels: Optional[list[str]] = None
    message: Optional[str] = None


class AlertResponse(BaseSchema):
    """Alert response."""
    
    id: int
    alert_type: str
    commodity_id: Optional[int] = None
    market_id: Optional[int] = None
    priority: str
    status: str
    conditions: dict[str, Any]
    notification_channels: list[str]
    message: Optional[str] = None
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AlertUpdateRequest(BaseSchema):
    """Alert update request."""
    
    status: Optional[str] = None
    priority: Optional[str] = None
    conditions: Optional[dict[str, Any]] = None
    notification_channels: Optional[list[str]] = None


class ModelMetricsResponse(BaseSchema):
    """Model metrics response."""
    
    id: int
    model_name: str
    model_version: str
    accuracy: float
    rmse: float
    mae: float
    r2_score: float
    mape: float
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    feature_importance: Optional[dict[str, Any]] = None
    training_samples: Optional[int] = None
    test_samples: Optional[int] = None
    training_date: Optional[datetime] = None
    hyperparameters: Optional[dict[str, Any]] = None
    cross_validation_scores: Optional[list[float]] = None
    created_at: datetime
