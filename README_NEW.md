# Vypaar-AI - Agricultural Market Intelligence Platform

Full-stack agricultural market data analysis platform with ML-powered price predictions, inventory management, and AI-driven insights.

## 🏗️ Project Structure

```
Vypaar-AI/
├── backend/           # FastAPI backend server
├── frontend/          # React + Vite frontend
├── data/             # Data storage (raw, processed, models)
├── logs/             # Application logs
└── test_integration.sh  # API integration test script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv ../.venv
source ../.venv/bin/activate  # On Windows: ..\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p ../data/{raw,processed,models} ../logs

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run server
python run.py
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your backend URL and Clerk key

# Run development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### 3. Test Integration

```bash
# Make sure backend is running
cd /path/to/Vypaar-AI
chmod +x test_integration.sh
./test_integration.sh
```

## 📚 Documentation

- [Backend README](backend/README.md) - Backend setup and API documentation
- [Frontend README](frontend/README.md) - Frontend setup and components
- [Integration Test Report](INTEGRATION_TEST_REPORT.md) - Complete integration details
- [API Documentation](API_DOCUMENTATION.md) - Detailed API reference

## 🔌 API Endpoints

All endpoints are prefixed with backend URL (default: `http://localhost:8000`)

### Frontend Integration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/forecast` | POST | Generate price forecast for product |
| `/api/ai/insights` | GET | Get AI-generated market insights |
| `/api/model/accuracy` | GET | Get ML model performance metrics |
| `/api/product-analysis` | GET | Get product analysis dashboard data |
| `/api/inventory/dashboard` | GET | Get inventory management data |

### Core API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check and system status |
| `/api/v1/predictions` | POST | General price prediction |
| `/api/v1/market-data` | GET | Get market data |
| `/api/v1/inventory` | GET/POST | Inventory management |
| `/api/v1/alerts` | GET/POST | Alert management |
| `/api/v1/model-metrics` | GET | Model performance metrics |

## 🎯 Features

### Backend
- ✅ REST API with FastAPI
- ✅ ML ensemble models (XGBoost, LightGBM, Random Forest)
- ✅ Price predictions with confidence intervals
- ✅ AI-powered market insights
- ✅ Inventory optimization
- ✅ Web scraping from Agmarknet
- ✅ Automated data collection and training
- ✅ Comprehensive logging
- ✅ Database with SQLAlchemy + Alembic migrations
- ✅ 80%+ test coverage

### Frontend
- ✅ Modern React with TypeScript
- ✅ TailwindCSS for styling
- ✅ Clerk authentication
- ✅ Interactive dashboards
- ✅ Real-time charts (Recharts)
- ✅ Responsive design
- ✅ Context-based state management
- ✅ Smooth animations (Framer Motion)

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Database**: SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- **ML**: Scikit-learn, XGBoost, LightGBM
- **Scraping**: BeautifulSoup4, Requests
- **Async**: Asyncio, Aiosqlite
- **Logging**: Loguru
- **Task Scheduling**: APScheduler

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: TailwindCSS 4
- **Routing**: React Router 7
- **Auth**: Clerk
- **Charts**: Recharts
- **Animations**: Framer Motion

## 📦 Environment Variables

### Backend (.env)
```env
# Application
APP_NAME=Vypaar-AI Backend
DEBUG=true
ENVIRONMENT=development

# API
API_V1_PREFIX=/api/v1
PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Database
DATABASE_URL=sqlite+aiosqlite:///../data/agritech.db

# Redis (Optional)
REDIS_ENABLED=false
```

### Frontend (.env)
```env
# Clerk Authentication
VITE_CLERK_PUBLISHABLE_KEY=your_key_here

# Backend API
VITE_BACKEND_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app --cov-report=html
```

### Integration Tests
```bash
./test_integration.sh
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 Development Workflow

1. **Start Backend**
   ```bash
   cd backend && python run.py
   ```

2. **Start Frontend**
   ```bash
   cd frontend && npm run dev
   ```

3. **Make Changes**
   - Backend: FastAPI auto-reloads on file changes
   - Frontend: Vite HMR for instant updates

4. **Test**
   ```bash
   ./test_integration.sh
   ```

## 🚢 Deployment

### Backend
```bash
# Production setup
cd backend
pip install -r requirements.txt
python -m app.database.init_db  # Initialize database
python scripts/train_models.py   # Train ML models

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
# Serve dist/ folder with nginx or similar
```

## 📊 Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🔧 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (3.11+ required)
- Verify virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is not in use: `lsof -i :8000`

### Frontend won't start
- Check Node.js version: `node --version` (18+ required)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check port 5173 is not in use: `lsof -i :5173`

### API connection errors
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check CORS settings in backend `.env`
- Verify `VITE_BACKEND_URL` in frontend `.env`

## 📄 License

MIT License - see LICENSE file for details

## 👥 Contributors

- Development Team

## 🙏 Acknowledgments

- Agmarknet for agricultural market data
- FastAPI and React communities
- All open-source library contributors

---

**Status**: ✅ Production Ready

For detailed setup instructions, see individual README files in `backend/` and `frontend/` directories.
