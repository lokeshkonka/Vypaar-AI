# Vypaar-AI Backend

Industry-level FastAPI backend for agricultural market data analysis with ensemble ML models, web scraping from Agmarknet, intelligent inventory management, and real-time predictions.

## 🚀 Quick Start

### Installation

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Create necessary directories**
```bash
mkdir -p ../data/raw ../data/processed ../data/models
```

### Run the application

```bash
# Using the run script
python run.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Core utilities, logging, exceptions
│   ├── database/         # Database models and repositories
│   ├── ml/               # ML models, training, prediction
│   ├── scraper/          # Web scraping logic
│   ├── services/         # Business logic
│   ├── models/           # Pydantic schemas
│   ├── config.py         # Configuration management
│   └── main.py           # FastAPI application
├── scripts/              # Utility scripts
├── tests/                # Test suite
├── run.py                # Entry point
└── requirements.txt      # Dependencies
```

## 🔌 Frontend Integration

The backend provides the following API endpoints for frontend integration:

### Forecast API
- **POST** `/api/forecast` - Generate price forecast
  ```json
  {
    "state": "Maharashtra",
    "city": "Mumbai",
    "market": "Vashi",
    "category": "Vegetables",
    "product": "Tomato",
    "forecast_range": 7
  }
  ```

### Insights API
- **GET** `/api/ai/insights` - Get AI-generated market insights

### Model Accuracy API
- **GET** `/api/model/accuracy` - Get model performance metrics

### Inventory API
- **GET** `/api/inventory/dashboard` - Get inventory dashboard data

### Health Check
- **GET** `/api/v1/health` - Health check endpoint

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## 📊 Environment Variables

Key environment variables (see `.env.example`):

- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed CORS origins (include frontend URL)
- `DEBUG` - Debug mode (true/false)
- `API_V1_PREFIX` - API version prefix

## 🔧 Development

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Training Models

```bash
# Quick training
python scripts/train_fast.py

# Full training with history
python scripts/train_with_history.py
```

### Data Scraping

```bash
python scripts/scrape_data.py
```
