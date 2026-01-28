# Agri-Tech Backend - Project Outline

## Project Overview
FastAPI backend for agricultural market data analysis using ensemble ML models with data scraped from Agmarknet (https://agmarknet.gov.in/home).

## Technology Stack
- **Framework**: FastAPI
- **ML/AI**: scikit-learn, XGBoost, LightGBM, CatBoost
- **Data Processing**: pandas, numpy
- **Web Scraping**: BeautifulSoup4, Selenium, requests
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Testing**: pytest, pytest-cov
- **Logging**: Python logging, loguru
- **API Documentation**: FastAPI auto-generated Swagger/OpenAPI
- **Validation**: pydantic
- **Task Queue**: Celery + Redis (for alerts & background tasks)
- **Notifications**: APScheduler (scheduled alerts)

## Project Structure
```
agritech/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── predictions.py
│   │   │   │   ├── market_data.py
│   │   │   │   ├── inventory.py
│   │   │   │   ├── alerts.py
│   │   │   │   └── health.py
│   │   │   └── router.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic models
│   │   └── database.py         # Database models
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── preprocessor.py     # Data preprocessing
│   │   ├── trainer.py          # Model training
│   │   ├── predictor.py        # Prediction interface
│   │   ├── ensemble.py         # Ensemble model logic
│   │   ├── model_metrics.py    # Model accuracy & performance tracking
│   │   └── models/             # Saved ML models
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── agmarknet_scraper.py
│   │   ├── data_validator.py
│   │   └── utils.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── repositories.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── logging_config.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── inventory_service.py    # Inventory management logic
│   │   ├── alert_service.py        # Alert generation & management
│   │   └── notification_service.py # Alert delivery system
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_api/
│       ├── test_ml/
│       └── test_scraper/
├── data/
│   ├── raw/                    # Raw scraped data
│   ├── processed/              # Processed data
│   └── models/                 # Trained models
├── logs/                       # Application logs
├── notebooks/                  # Jupyter notebooks for exploration
├── scripts/
│   ├── scrape_data.py
│   ├── train_models.py
│   └── evaluate_models.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
└── docker-compose.yml
```

## Implementation Phases

### Phase 1: Project Setup & Configuration
- [x] Create project structure
- [ ] Setup virtual environment
- [ ] Install dependencies
- [ ] Configure logging system
- [ ] Setup configuration management
- [ ] Create .gitignore and environment files

### Phase 2: Data Scraping Module
- [ ] Implement Agmarknet scraper
  - Market prices (commodity-wise)
  - State-wise data
  - Historical trends
  - Market arrivals
- [ ] Data validation and cleaning
- [ ] Store raw data in database
- [ ] Error handling and retry logic
- [ ] Rate limiting and respectful scraping

### Phase 3: Database Layer
- [ ] Design database schema
- [ ] Implement database models
- [ ] Create repositories for data access
- [ ] Setup migrations (if needed)
- [ ] Implement data caching strategies

### Phase 4: Machine Learning Pipeline
- [ ] Data preprocessing and feature engineering
  - Handle missing values
  - Feature scaling/normalization
  - Time-series features
  - Categorical encoding
- [ ] Train individual models:
  - Random Forest
  - XGBoost
  - LightGBM
  - CatBoost
  - Linear models (baseline)
- [ ] Implement ensemble strategies:
  - Voting ensemble
  - Stacking ensemble
  - Weighted average
- [ ] Model evaluation and selection
- [ ] Model serialization and versioning
- [ ] Implement prediction pipeline

### Phase 5: API Development
- [ ] Create FastAPI application
- [ ] Implement endpoints:
  - GET /health - Health check
  - GET /api/v1/markets - List markets
  - GET /api/v1/commodities - List commodities
  - GET /api/v1/market-data - Get market data
  - POST /api/v1/predict - Price predictions (with model metrics)
  - GET /api/v1/trends - Historical trends
  - GET /api/v1/analysis - Market analysis
  - POST /api/v1/inventory/suggestions - Get inventory suggestions
  - GET /api/v1/inventory/optimize - Optimize inventory levels
  - POST /api/v1/alerts/configure - Configure alert rules
  - GET /api/v1/alerts - Get active alerts
  - GET /api/v1/alerts/history - Alert history
  - GET /api/v1/model/metrics - Get model performance metrics
- [ ] Request/Response validation with Pydantic
- [ ] Error handling middleware
- [ ] CORS configuration
- [ ] Rate limiting
- [ ] Response caching
- [ ] Model metadata injection in responses

### Phase 6: Logging & Monitoring
- [ ] Configure structured logging
- [ ] Log all API requests/responses
- [ ] Log ML model predictions
- [ ] Log scraping activities
- [ ] Error tracking and alerting
- [ ] Performance metrics logging

### Phase 7: Testing
- [ ] Unit tests for all modules
- [ ] Integration tests for API
- [ ] Test data scraping logic
- [ ] Test ML pipeline
- [ ] Test ensemble predictions
- [ ] Test inventory suggestion logic
- [ ] Test alert generation and delivery
- [ ] Test model metrics accuracy
- [ ] Performance/load testing
- [ ] Achieve >80% code coverage

### Phase 8: Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Code documentation (docstrings)
- [ ] README with setup instructions
- [ ] Architecture documentation
- [ ] Model documentation
- [ ] Deployment guide

### Phase 9: Optimization & Production Ready
- [ ] Code optimization
- [ ] Database query optimization
- [ ] Model serving optimization
- [ ] Add caching layers
- [ ] Docker containerization
- [ ] CI/CD pipeline setup

## Key Features

### Data Scraping
- Multi-threaded scraping for efficiency
- Automatic retry on failures
- Data validation and cleaning
- Historical data collection
- Real-time data updates

### Inventory Management
- **Smart Inventory Suggestions**: ML-based recommendations for optimal stock levels
- **Demand Forecasting**: Predict future commodity requirements
- **Stock Optimization**: Minimize waste while ensuring availability
- **Seasonal Adjustments**: Account for seasonal demand patterns
- **Multi-commodity Analysis**: Cross-commodity inventory planning

### Alert System
- **Price Alerts**: Notify when prices exceed/drop below thresholds
- **Inventory Alerts**: Low stock, overstock, and expiry warnings
- **Market Volatility Alerts**: Sudden price fluctuations
- **Trend Alerts**: Significant trend changes
- **Custom Rules**: User-configurable alert conditions
- **Alert Channels**: In-app, email, webhook support
- **Alert Priority Levels**: Critical, high, medium, low
- **Smart Throttling**: Prevent alert fatigue

### Model Performance Tracking
- **Real-time Metrics**: Accuracy, precision, recall, F1-score, RMSE, MAE, R²
- **Per-model Performance**: Individual model metrics
- **Ensemble Performance**: Combined model accuracy
- **Confidence Scores**: Prediction confidence levels
- **Feature Importance**: Which features drive predictions
- **Model Versioning**: Track performance across model versions
- **Drift Detection**: Monitor model degradation over time

### Machine Learning Models
**Target Variables:**
- Price prediction (daily/weekly/monthly)
- Price trend classification
- Market volatility prediction
- Arrival quantity forecasting
- Demand forecasting (for inventory)
- Stock optimization levels
- Anomaly detection (price spikes/drops)

**Ensemble Models:**
1. **Voting Ensemble**: Majority vote from multiple classifiers
2. **Stacking Ensemble**: Meta-learner trained on base model predictions
3. **Weighted Average**: Custom weights based on model performance

**Features:**
- Historical prices
- Market arrivals
- Seasonal patterns
- State/region information
- Commodity categories
- Weather data (if available)
- Festival/holiday indicators
- Day of week / month patterns
- Market capacity metrics
- Supply chain disruptions
- Historical demand patterns
- Inventory turnover rates
- Commodity shelf life
- Storage capacity constraints

### API Endpoints

#### 1. Health Check
```
GET /health
Response: System status, model status, database status
```

#### 2. Market Data
```
GET /api/v1/markets?state={state}
GET /api/v1/commodities?category={category}
GET /api/v1/market-data?market={market}&commodity={commodity}&date={date}
```

#### 3. Predictions (with Model Metrics)
```
POST /api/v1/predict
Body: {
  "market": "Delhi",
  "commodity": "Wheat",
  "date": "2026-01-30",
  "features": {...}
}
Response: {
  "predicted_price": 2500.0,
  "confidence_interval": [2400, 2600],
  "model_confidence": 0.85,
  "models_used": ["xgboost", "lightgbm", "random_forest"],
  "model_metrics": {
    "ensemble_accuracy": 0.92,
    "rmse": 85.3,
    "mae": 62.1,
    "r2_score": 0.89,
    "individual_models": {
      "xgboost": {"accuracy": 0.91, "weight": 0.35},
      "lightgbm": {"accuracy": 0.90, "weight": 0.35},
      "random_forest": {"accuracy": 0.88, "weight": 0.30}
    },
    "feature_importance": {
      "historical_price": 0.35,
      "season": 0.22,
      "market_arrival": 0.18,
      "state": 0.15,
      "day_of_week": 0.10
    },
    "model_version": "v2.3.1",
    "trained_on": "2026-01-15",
    "training_samples": 50000
  },
  "prediction_metadata": {
    "timestamp": "2026-01-21T10:30:00Z",
    "processing_time_ms": 145,
    "data_freshness": "2 hours ago"
  }
}
```

#### 4. Trends & Analysis
```
GET /api/v1/trends?commodity={commodity}&period={period}
GET /api/v1/analysis/volatility?market={market}
GET /api/v1/analysis/seasonal?commodity={commodity}
```

#### 5. Inventory Suggestions
```
POST /api/v1/inventory/suggestions
Body: {
  "commodity": "Wheat",
  "current_stock": 1000,
  "location": "Delhi",
  "forecast_days": 30
}
Response: {
  "recommendation": {
    "action": "RESTOCK",
    "suggested_quantity": 500,
    "optimal_stock_level": 1500,
    "urgency": "HIGH",
    "estimated_stockout_date": "2026-02-05"
  },
  "forecast": {
    "predicted_demand_30d": 1200,
    "predicted_price_trend": "INCREASING",
    "price_increase_percentage": 8.5
  },
  "reasoning": [
    "Current stock will last only 14 days at predicted consumption rate",
    "Price expected to increase by 8.5% in next 2 weeks",
    "High demand period approaching (festival season)"
  ],
  "model_metrics": {
    "demand_forecast_accuracy": 0.88,
    "price_forecast_accuracy": 0.85
  }
}
```

```
GET /api/v1/inventory/optimize?commodities=Wheat,Rice&location=Delhi
Response: {
  "optimized_inventory": [
    {
      "commodity": "Wheat",
      "current_stock": 1000,
      "optimal_stock": 1500,
      "adjustment": +500,
      "cost_savings": 15000,
      "waste_reduction": "12%"
    },
    {
      "commodity": "Rice",
      "current_stock": 2000,
      "optimal_stock": 1800,
      "adjustment": -200,
      "cost_savings": 8000,
      "waste_reduction": "8%"
    }
  ],
  "total_cost_savings": 23000,
  "model_confidence": 0.87
}
```

#### 6. Alert Management
```
POST /api/v1/alerts/configure
Body: {
  "alert_type": "PRICE_THRESHOLD",
  "commodity": "Wheat",
  "market": "Delhi",
  "conditions": {
    "price_above": 2800,
    "price_below": 2200
  },
  "priority": "HIGH",
  "channels": ["in_app", "email"]
}
Response: {
  "alert_id": "alert_12345",
  "status": "ACTIVE",
  "created_at": "2026-01-21T10:30:00Z"
}
```

```
GET /api/v1/alerts?status=active&priority=high
Response: {
  "alerts": [
    {
      "alert_id": "alert_67890",
      "type": "INVENTORY_LOW",
      "commodity": "Rice",
      "message": "Rice inventory below threshold (200kg remaining)",
      "priority": "HIGH",
      "triggered_at": "2026-01-21T09:15:00Z",
      "recommendation": "Restock 500kg within 3 days",
      "status": "ACTIVE"
    },
    {
      "alert_id": "alert_67891",
      "type": "PRICE_VOLATILITY",
      "commodity": "Wheat",
      "market": "Mumbai",
      "message": "Unusual price spike detected (+15% in 24 hours)",
      "priority": "HIGH",
      "triggered_at": "2026-01-21T08:00:00Z",
      "current_price": 2900,
      "previous_price": 2520,
      "status": "ACTIVE"
    }
  ],
  "count": 2,
  "model_metrics": {
    "anomaly_detection_accuracy": 0.93
  }
}
```

```
GET /api/v1/alerts/history?days=7
Response: {
  "alerts": [...],
  "statistics": {
    "total_alerts": 45,
    "critical": 5,
    "high": 12,
    "medium": 20,
    "low": 8,
    "false_positive_rate": 0.04
  }
}
```

#### 7. Model Metrics
```
GET /api/v1/model/metrics?model=ensemble
Response: {
  "model_name": "ensemble",
  "version": "v2.3.1",
  "performance_metrics": {
    "accuracy": 0.92,
    "rmse": 85.3,
    "mae": 62.1,
    "r2_score": 0.89,
    "mape": 4.2
  },
  "component_models": [
    {
      "name": "xgboost",
      "accuracy": 0.91,
      "weight": 0.35,
      "status": "ACTIVE"
    },
    {
      "name": "lightgbm",
      "accuracy": 0.90,
      "weight": 0.35,
      "status": "ACTIVE"
    },
    {
      "name": "random_forest",
      "accuracy": 0.88,
      "weight": 0.30,
      "status": "ACTIVE"
    }
  ],
  "training_info": {
    "last_trained": "2026-01-15T00:00:00Z",
    "training_samples": 50000,
    "validation_samples": 10000,
    "test_samples": 5000,
    "training_duration_minutes": 45
  },
  "feature_importance": {
    "historical_price": 0.35,
    "season": 0.22,
    "market_arrival": 0.18,
    "state": 0.15,
    "day_of_week": 0.10
  },
  "drift_detection": {
    "status": "STABLE",
    "last_checked": "2026-01-21T00:00:00Z",
    "accuracy_change": -0.01
  },
  "prediction_stats_7d": {
    "total_predictions": 1234,
    "avg_confidence": 0.87,
    "avg_processing_time_ms": 152
  }
}
```

### Logging Strategy
- **Application Logs**: All API requests, errors, warnings
- **ML Logs**: Training metrics, predictions, model performance
- **Scraping Logs**: Success/failure, data quality metrics
- **Format**: JSON structured logs with timestamps, levels, context
- **Rotation**: Daily rotation with 30-day retention

### Testing Strategy
- **Unit Tests**: Individual functions and methods
- **Integration Tests**: API endpoints, database operations
- **End-to-End Tests**: Complete workflows
- **Performance Tests**: Response times, concurrent requests
- **ML Tests**: Model accuracy, prediction validity

## Performance Targets
- API response time: < 200ms (without ML prediction)
- Prediction response time: < 2s
- Scraping: Complete daily update in < 30 minutes
- Model accuracy: > 85% (R² score for regression)
- API uptime: 99.9%
- Test coverage: > 80%

## Data Sources from Agmarknet
1. Daily market prices for commodities
2. Market arrivals (quantity)
3. State-wise market data
4. Commodity categories
5. Historical price trends
6. Market-wise commodity availability

## Timeline Estimate
- **Phase 1**: 1 day
- **Phase 2**: 3 days
- **Phase 3**: 2 days
- **Phase 4**: 5 days
- **Phase 5**: 3 days
- **Phase 6**: 1 day
- **Phase 7**: 3 days
- **Phase 8**: 2 days
- **Phase 9**: 2 days

**Total**: ~22 days (working systematically)

## Next Steps
1. Review and approve this outline
2. Setup development environment
3. Begin Phase 1: Project Setup
4. Proceed sequentially through each phase
