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


class BuySellSignal(str, Enum):
    """Buy/Sell signal type."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalStrength(str, Enum):
    """Signal strength intensity."""

    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"


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
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    models_used: list[str]
    model_metrics: ModelMetadata
    prediction_metadata: PredictionMetadata
    
    def model_dump(self, **kwargs):
        """Include confidence_score as alias for backward compatibility."""
        data = super().model_dump(**kwargs)
        data['confidence_score'] = data.get('model_confidence')
        return data


# Frontend bridge schemas
class ForecastPoint(BaseSchema):
    """Single forecast point for a day."""

    date: str
    predicted_price: float
    lower_bound: float
    upper_bound: float
    confidence: float


class ForecastRequest(BaseSchema):
    """Forecast request coming from the UI selector."""

    state: Optional[str] = None
    city: Optional[str] = None
    market_type: Optional[str] = Field(default=None, alias="marketType")
    market: str
    category: Optional[str] = None
    product: str
    forecast_range: int = Field(default=14, ge=1, le=30, alias="forecastRange")


class ForecastResponse(BaseSchema):
    """Forecast response aligned with dashboard expectations."""

    product: str
    market: str
    state: Optional[str] = None
    range_days: int = Field(alias="rangeDays")
    trend: str
    average_price: float = Field(alias="averagePrice")
    forecasts: list[ForecastPoint]
    model_accuracy: float = Field(alias="modelAccuracy")
    notes: list[str]


class InsightItemResponse(BaseSchema):
    """Actionable insight for the insights dashboard."""

    id: str
    title: str
    reason: str
    priority: str
    confidence: int
    time_horizon: str = Field(alias="timeHorizon")


class ModelAccuracySummary(BaseSchema):
    """Compact accuracy summary for UI cards."""

    forecastAccuracy: float
    improvement: float
    mae: float
    maeTraditional: float
    mape: float
    mapeTraditional: float
    aiAccuracy: float
    traditionalAccuracy: float


class InventoryDashboardItem(BaseSchema):
    """Inventory row used by the frontend dashboard."""

    id: int
    market: str
    category: Optional[str] = None
    product: str
    current: float
    suggested: float
    risk: str


class InventoryUpdateRequest(BaseSchema):
    """Request to update inventory items."""

    items: List[dict]


class InventoryUpdateResponse(BaseSchema):
    """Response after updating inventory."""

    status: str
    message: str
    timestamp: str
    items_updated: int


# Product Analysis Schemas
class SelectorData(BaseSchema):
    """Selector data for product analysis."""
    market: str
    product: str
    forecastRange: str


class StockMetrics(BaseSchema):
    """Stock metrics for product analysis."""
    predictedDemand: int
    stockNeeded: int
    overstockRisk: int
    understockRisk: int


class DemandGraphPoint(BaseSchema):
    """Demand graph point for product analysis."""
    day: str
    actual: int
    forecast: int


class ImpactItem(BaseSchema):
    """Impact item for product analysis."""
    title: str
    subtitle: Optional[str] = None
    delta: Optional[str] = None
    positive: Optional[bool] = None


class ImpactData(BaseSchema):
    """Impact data for product analysis."""
    festival: list["ImpactItem"]
    weather: list["ImpactItem"]


class RecommendationRow(BaseSchema):
    """Recommendation row for product analysis."""
    product: str
    current: int
    suggested: int
    buffer: int
    risk: str


class ProductAnalysisResponse(BaseSchema):
    """Product analysis response."""
    selectorData: SelectorData
    stockMetrics: StockMetrics
    demandGraphData: list[DemandGraphPoint]
    impactData: ImpactData
    recommendationTable: list[RecommendationRow]


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


class InventorySuggestionDetailedResponse(BaseSchema):
    """Inventory suggestion response (detailed variant)."""

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


class ModelMetricsDetailedResponse(BaseSchema):
    """Comprehensive model metrics response (detailed shape)."""

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


# Buy/Sell Alert Schemas
class BuySellAlertRequest(BaseSchema):
    """Buy/Sell alert creation request."""
    
    commodity_id: int = Field(..., description="Commodity ID")
    market_id: int = Field(..., description="Market ID")
    buy_threshold: float = Field(..., ge=0, description="Price threshold for BUY signal")
    sell_threshold: float = Field(..., ge=0, description="Price threshold for SELL signal")
    priority: AlertPriority = Field(default=AlertPriority.MEDIUM)
    notification_channels: Optional[list[str]] = Field(default=["in_app"])
    message: Optional[str] = None
    enabled: bool = Field(default=True)


class BuySellAlertResponse(BaseSchema):
    """Buy/Sell alert response."""
    
    id: int
    commodity_id: int
    commodity_name: Optional[str] = None
    market_id: int
    market_name: Optional[str] = None
    buy_threshold: float
    sell_threshold: float
    current_price: Optional[float] = None
    signal: Optional[BuySellSignal] = None
    signal_strength: Optional[SignalStrength] = None
    priority: str
    enabled: bool
    notification_channels: list[str]
    message: Optional[str] = None
    triggered_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class BuySellAlertUpdateRequest(BaseSchema):
    """Update request for buy/sell alerts."""
    
    buy_threshold: Optional[float] = None
    sell_threshold: Optional[float] = None
    priority: Optional[AlertPriority] = None
    enabled: Optional[bool] = None
    notification_channels: Optional[list[str]] = None
    message: Optional[str] = None


class BuySellSignalResponse(BaseSchema):
    """Buy/Sell signal response with analysis."""
    
    commodity_id: int
    commodity_name: str
    market_id: int
    market_name: str
    current_price: float
    buy_threshold: float
    sell_threshold: float
    signal: BuySellSignal
    signal_strength: SignalStrength
    confidence: float = Field(..., ge=0, le=1)
    reasoning: list[str]
    price_trend: TrendDirection
    days_to_buy_signal: Optional[int] = None
    days_to_sell_signal: Optional[int] = None
    timestamp: datetime


class BuySellAlertListResponse(BaseSchema):
    """List of buy/sell alerts."""
    
    alerts: list[BuySellAlertResponse]
    total: int
    active: int
    triggered: int


class BuySellAlertHistoryResponse(BaseSchema):
    """Buy/Sell alert history."""
    
    alert_id: int
    commodity_name: str
    market_name: str
    signals: list[BuySellSignalResponse]
    total_buys: int
    total_sells: int
    success_rate: float = Field(..., ge=0, le=1)
    profit_loss: Optional[float] = None


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


# Discussion schemas
class DiscussionCreate(BaseSchema):
    """Create discussion request."""
    
    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=10, max_length=5000)
    commodity: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    avatar_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list, max_length=10)


class DiscussionUpdate(BaseSchema):
    """Update discussion request."""
    
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    tags: Optional[list[str]] = None


class DiscussionResponse(BaseSchema):
    """Discussion response."""
    
    id: int
    title: str
    content: str
    commodity: str
    author: str
    avatar_url: Optional[str] = None
    likes_count: int
    replies_count: int
    views_count: int
    is_pinned: bool
    tags: list[str]
    status: str
    created_at: datetime
    updated_at: datetime


class DiscussionListResponse(BaseSchema):
    """List of discussions."""
    
    discussions: list[DiscussionResponse]
    total: int
    page: int
    page_size: int


# Watchlist schemas
class WatchlistCreate(BaseSchema):
    """Create watchlist entry."""
    
    user_id: str
    commodity_id: int
    market_id: Optional[int] = None
    notes: Optional[str] = None
    alert_on_price_change: bool = False
    price_change_threshold: Optional[float] = Field(None, ge=0.1, le=100)


class WatchlistUpdate(BaseSchema):
    """Update watchlist entry."""
    
    notes: Optional[str] = None
    alert_on_price_change: Optional[bool] = None
    price_change_threshold: Optional[float] = Field(None, ge=0.1, le=100)


class WatchlistResponse(BaseSchema):
    """Watchlist entry response."""
    
    id: int
    user_id: str
    commodity_id: int
    commodity_name: Optional[str] = None
    market_id: Optional[int] = None
    market_name: Optional[str] = None
    current_price: Optional[float] = None
    notes: Optional[str] = None
    alert_on_price_change: bool
    price_change_threshold: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class WatchlistListResponse(BaseSchema):
    """List of watchlist entries."""
    
    watchlist: list[WatchlistResponse]
    total: int


# Market trend analysis schemas
class MarketTrendAnalysisResponse(BaseSchema):
    """Market trend analysis response."""
    
    id: int
    commodity_id: int
    commodity_name: str
    market_id: int
    market_name: str
    analysis_date: str
    period_days: int
    avg_price: float
    min_price: float
    max_price: float
    price_volatility: float
    trend_direction: str  # INCREASING, DECREASING, STABLE
    trend_strength: float  # 0-1
    momentum: float
    total_volume: Optional[float] = None
    avg_daily_volume: Optional[float] = None
    price_range: dict = Field(default_factory=dict)
    trend_label: str = ""


class MarketTrendComparisonResponse(BaseSchema):
    """Compare trends across different periods."""
    
    commodity_id: int
    commodity_name: str
    market_id: int
    market_name: str
    trends_7d: Optional[MarketTrendAnalysisResponse] = None
    trends_14d: Optional[MarketTrendAnalysisResponse] = None
    trends_30d: Optional[MarketTrendAnalysisResponse] = None
    trend_change: str  # Comparison result
    recommendation: str
