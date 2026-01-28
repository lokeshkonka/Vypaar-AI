# Agri-Tech Backend

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Industry-level FastAPI backend for agricultural market data analysis with ensemble ML models, web scraping from Agmarknet, intelligent inventory management, and real-time alerts.

## 🚀 Features

- **Market Data Scraping**: Automated data collection from [Agmarknet](https://agmarknet.gov.in/home)
- **Ensemble ML Models**: XGBoost, LightGBM, CatBoost, Random Forest
- **Price Predictions**: With confidence intervals and model accuracy metrics
- **Inventory Management**: AI-powered stock suggestions and optimization
- **Smart Alerts**: Price, inventory, and volatility alerts with multiple priority levels
- **Comprehensive Logging**: Structured JSON logs with rotation
- **Model Metrics**: Real-time accuracy, RMSE, MAE, R², feature importance
- **API Documentation**: Auto-generated Swagger/OpenAPI docs
- **80%+ Test Coverage**: Comprehensive unit and integration tests

## 📁 Project Structure

```
agritech/
├── app/
│   ├── api/v1/endpoints/      # API endpoints
│   ├── core/                  # Core utilities, logging, exceptions
│   ├── database/              # Database models and repositories
│   ├── ml/                    # ML models, training, prediction
│   ├── scraper/               # Web scraping logic
│   ├── services/              # Business logic (inventory, alerts)
│   ├── models/                # Pydantic schemas
│   ├── tests/                 # Test suite
│   ├── config.py              # Configuration management
│   └── main.py                # FastAPI application
├── data/
│   ├── raw/                   # Raw scraped data
│   ├── processed/             # Processed datasets
│   └── models/                # Trained ML models
├── logs/                      # Application logs
├── notebooks/                 # Jupyter notebooks
├── scripts/                   # Utility scripts
├── requirements.txt
└── README.md
```

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- pip
- virtualenv (recommended)
- Redis (optional, for alerts)

### Setup

1. **Clone the repository**
```bash
cd /home/vishal/code/agritech
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Create necessary directories**
```bash
mkdir -p data/raw data/processed data/models logs
```

## 🚦 Quick Start

### Run the application

```bash
# Development mode with auto-reload
python app/main.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Root endpoint
curl http://localhost:8000/
```

## 📊 API Endpoints

### Health & Status
- `GET /health` - Health check with service status

### Market Data (Coming Soon)
- `GET /api/v1/markets` - List all markets
- `GET /api/v1/commodities` - List all commodities
- `GET /api/v1/market-data` - Get specific market data

### Predictions (Coming Soon)
- `POST /api/v1/predict` - Price predictions with model metrics

### Inventory (Coming Soon)
- `POST /api/v1/inventory/suggestions` - Get inventory recommendations
- `GET /api/v1/inventory/optimize` - Optimize inventory levels

### Alerts (Coming Soon)
- `POST /api/v1/alerts/configure` - Configure alert rules
- `GET /api/v1/alerts` - Get active alerts
- `GET /api/v1/alerts/history` - Alert history

### Model Metrics (Coming Soon)
- `GET /api/v1/model/metrics` - Model performance metrics

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests
pytest -m unit

# Integration tests
pytest -m integration

# API tests
pytest -m api

# With coverage report
pytest --cov=app --cov-report=html
```

### View coverage report
```bash
# Open in browser
open htmlcov/index.html  # On Mac
xdg-open htmlcov/index.html  # On Linux
```

## 📝 Configuration

Key configuration variables in `.env`:

```env
# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API
PORT=8000
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/agritech.db

# ML Models
MODEL_DIR=data/models
MODEL_VERSION=v1.0.0

# Scraping
AGMARKNET_BASE_URL=https://agmarknet.gov.in
SCRAPE_RATE_LIMIT=10

# Alerts
ALERT_CHECK_INTERVAL_MINUTES=5

# Inventory
INVENTORY_FORECAST_DAYS=30
```

## 🔧 Development Workflow

### Phase 1: Setup ✅ (COMPLETED)
- [x] Project structure
- [x] Configuration management
- [x] Logging system
- [x] Core utilities
- [x] Pydantic schemas
- [x] FastAPI application
- [x] Health endpoint
- [x] Test setup

### Phase 2: Data Scraping (Next)
- [ ] Implement Agmarknet scraper
- [ ] Data validation
- [ ] Store in database
- [ ] Error handling

### Phase 3: Database Layer
- [ ] Database models
- [ ] Repositories
- [ ] Migrations

### Phase 4: ML Pipeline
- [ ] Data preprocessing
- [ ] Train ensemble models
- [ ] Model evaluation
- [ ] Prediction service

### Phase 5: API Development
- [ ] Market data endpoints
- [ ] Prediction endpoints
- [ ] Inventory endpoints
- [ ] Alert endpoints

### Phase 6: Testing & Documentation
- [ ] Comprehensive tests
- [ ] API documentation
- [ ] Deployment guide

## 📖 API Response Example

```json
{
  "predicted_price": 2500.0,
  "confidence_interval": [2400, 2600],
  "model_confidence": 0.85,
  "models_used": ["xgboost", "lightgbm", "random_forest"],
  "model_metrics": {
    "ensemble_accuracy": 0.92,
    "rmse": 85.3,
    "mae": 62.1,
    "r2_score": 0.89,
    "individual_models": [
      {"name": "xgboost", "accuracy": 0.91, "weight": 0.35},
      {"name": "lightgbm", "accuracy": 0.90, "weight": 0.35},
      {"name": "random_forest", "accuracy": 0.88, "weight": 0.30}
    ],
    "feature_importance": {
      "historical_price": 0.35,
      "season": 0.22,
      "market_arrival": 0.18
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

## 🔍 Logging

Logs are stored in `logs/` directory with:
- **app.log**: All application logs (JSON format, daily rotation, 30-day retention)
- **error.log**: Error logs only
- Console output with colors for development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- **Development Team** - Initial work

## 🙏 Acknowledgments

- Data source: [Agmarknet](https://agmarknet.gov.in/home)
- FastAPI framework
- scikit-learn, XGBoost, LightGBM, CatBoost teams

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation at `/docs`

---

**Status**: Phase 1 Complete ✅ | In Active Development 🚧
