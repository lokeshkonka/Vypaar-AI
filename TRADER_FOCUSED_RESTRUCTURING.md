# Vypaar-AI: Trader-Focused Restructuring Plan

## Executive Summary
Transform Vypaar-AI into a professional agricultural commodity trading platform focused on long-lasting commodities with advanced analytics and daily data updates.

## 1. Commodity Selection (Long Shelf-Life Focus)

### Primary Commodities
**Grains:**
- Wheat (Gehu)
- Rice (Chawal)
- Maize (Makka)
- Barley (Jau)

**Pulses:**
- Chickpea (Chana)
- Lentil (Masoor)
- Pigeon Pea (Arhar/Tur)
- Green Gram (Moong)
- Black Gram (Urad)

**Oilseeds:**
- Mustard (Sarson)
- Groundnut (Moongfali)
- Soybean
- Sunflower

**Spices:**
- Turmeric (Haldi)
- Chili Dry (Mirch)
- Coriander (Dhaniya)
- Cumin (Jeera)

**Other:**
- Cotton (Kapas)
- Jute (Pat)

### Removed Commodities
- All perishable vegetables (Tomato, Potato, Onion, etc.)
- Short shelf-life fruits

## 2. Data Requirements

### Historical Data
- **Duration:** Minimum 6 months, target 12 months
- **Frequency:** Daily prices
- **Sources:** 
  - AgMarkNet (primary)
  - NCDEX/MCX for futures data
  - Government agricultural statistics

### Data Points Per Record
- Date
- Commodity name
- Market name
- State
- Minimum price
- Maximum price
- Modal price (most common)
- Arrival quantity
- Price unit

### Data Quality
- Remove outliers (prices >3 standard deviations)
- Handle missing data with forward fill
- Validate price consistency
- Cross-reference with multiple sources

## 3. Daily Data Scraping Schedule

### Implementation
```python
# Daily Schedule
- Time: 6:00 AM IST (after market close, before user access)
- Frequency: Once per day
- Retry logic: 3 attempts with exponential backoff
- Notification: Alert on failure

# Tasks
1. Scrape previous day data from AgMarkNet
2. Validate and clean data
3. Store in database
4. Update model predictions
5. Calculate technical indicators
6. Generate alerts for significant price movements
```

### Automation
- Use APScheduler for Python scheduling
- Systemd service for Linux deployment
- Cron job as backup
- Docker container with health checks

## 4. Machine Learning Models

### Model Architecture

**Primary Model: Ensemble of:**
1. **LSTM (Long Short-Term Memory)**
   - Handles time series patterns
   - 3 layers with dropout
   - Lookback window: 90 days

2. **Random Forest**
   - Captures non-linear relationships
   - 200 trees
   - Max depth: 15

3. **Gradient Boosting**
   - Fine-tunes predictions
   - Learning rate: 0.05
   - 150 estimators

4. **XGBoost**
   - High performance gradient boosting
   - Handles missing data well
   - Feature importance analysis

### Features (Input Variables)

**Price Features:**
- Historical prices (7, 14, 30, 60, 90 days)
- Price moving averages (7, 14, 30, 60 days)
- Price volatility (standard deviation)
- Price momentum
- Rate of change

**Technical Indicators:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Support and resistance levels
- Volume-weighted average price

**Temporal Features:**
- Day of week
- Month
- Season
- Is festival period
- Is harvest season
- Days to major festivals

**Market Features:**
- Arrival volume trends
- Market spread (max - min price)
- Price correlation with other markets
- Regional price differences

**External Factors:**
- Weather data (rainfall, temperature)
- Government policy indicators
- Import/export data
- Storage capacity utilization

### Training Strategy
- **Training data:** 80% of historical data
- **Validation:** 10%
- **Testing:** 10%
- **Retraining frequency:** Weekly
- **Incremental learning:** Add new data daily
- **Cross-validation:** Time-series split

### Performance Metrics
- MAPE (Mean Absolute Percentage Error) < 5%
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- Directional accuracy (up/down prediction) > 70%
- Profit potential in backtesting

## 5. Trader-Specific Features

### Dashboard
**Real-Time Overview:**
- Current prices of top 10 commodities
- Daily percentage change
- Market sentiment indicator
- Top gainers and losers
- Total market volume

**Watchlist:**
- Custom commodity tracking
- Price alerts
- Technical indicator signals
- News feed related to commodities

### Trading Analytics

**Price Prediction:**
- 7-day forecast with confidence intervals
- 14-day forecast
- 30-day forecast
- Prediction accuracy display

**Technical Analysis:**
- Interactive price charts (Candlestick, Line)
- Overlay technical indicators
- Drawing tools for support/resistance
- Pattern recognition (Head & Shoulders, Triangles)

**Buy/Sell Signals:**
- AI-generated recommendations
- Signal strength (Strong Buy, Buy, Hold, Sell, Strong Sell)
- Risk level (Low, Medium, High)
- Historical accuracy of signals
- Optimal entry and exit points

**Risk Management:**
- Portfolio volatility calculator
- Value at Risk (VaR) analysis
- Maximum drawdown metrics
- Correlation matrix
- Diversification score

**Market Comparison:**
- Compare prices across markets
- Arbitrage opportunities
- Best buying markets
- Best selling markets
- Transportation cost calculator

**Seasonal Insights:**
- Historical price patterns by season
- Harvest calendar
- Festival impact analysis
- Sowing and harvesting periods
- Weather impact predictions

### Advanced Analytics

**Market Depth:**
- Price distribution across markets
- Arrival quantity trends
- Supply-demand indicators
- Inventory levels (where available)

**News & Sentiment:**
- Aggregated agricultural news
- Government policy updates
- Weather forecasts
- International market trends
- Sentiment analysis from news

**Performance Tracking:**
- Trade journal (manual entry)
- Profit/Loss tracking
- Win rate calculation
- Best performing commodities
- Strategy backtesting

### Alerts & Notifications
- Price threshold alerts
- Technical indicator signals
- News alerts
- Weather alerts
- Market opening/closing reminders

## 6. Database Schema Updates

### Tables

**commodities_daily_prices**
```sql
CREATE TABLE commodities_daily_prices (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    commodity_id INTEGER NOT NULL,
    market_id INTEGER NOT NULL,
    min_price REAL,
    max_price REAL,
    modal_price REAL,
    arrival_quantity REAL,
    price_change REAL,
    price_change_percent REAL,
    volume_change_percent REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (commodity_id) REFERENCES commodities(id),
    FOREIGN KEY (market_id) REFERENCES markets(id),
    UNIQUE(date, commodity_id, market_id)
);
```

**technical_indicators**
```sql
CREATE TABLE technical_indicators (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    commodity_id INTEGER NOT NULL,
    market_id INTEGER NOT NULL,
    rsi_14 REAL,
    macd REAL,
    macd_signal REAL,
    bb_upper REAL,
    bb_middle REAL,
    bb_lower REAL,
    sma_7 REAL,
    sma_14 REAL,
    sma_30 REAL,
    ema_12 REAL,
    ema_26 REAL,
    volatility REAL,
    FOREIGN KEY (commodity_id) REFERENCES commodities(id),
    FOREIGN KEY (market_id) REFERENCES markets(id)
);
```

**trading_signals**
```sql
CREATE TABLE trading_signals (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    commodity_id INTEGER NOT NULL,
    market_id INTEGER NOT NULL,
    signal_type TEXT, -- BUY, SELL, HOLD
    signal_strength REAL, -- 0 to 100
    confidence REAL, -- 0 to 1
    target_price REAL,
    stop_loss REAL,
    reason TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (commodity_id) REFERENCES commodities(id),
    FOREIGN KEY (market_id) REFERENCES markets(id)
);
```

**user_watchlist**
```sql
CREATE TABLE user_watchlist (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    commodity_id INTEGER NOT NULL,
    market_id INTEGER,
    alert_on_price BOOLEAN DEFAULT FALSE,
    alert_price_threshold REAL,
    alert_on_signal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    FOREIGN KEY (commodity_id) REFERENCES commodities(id),
    FOREIGN KEY (market_id) REFERENCES markets(id)
);
```

**scraping_logs**
```sql
CREATE TABLE scraping_logs (
    id INTEGER PRIMARY KEY,
    scrape_date DATE NOT NULL,
    status TEXT, -- SUCCESS, FAILED, PARTIAL
    records_scraped INTEGER,
    records_failed INTEGER,
    duration_seconds REAL,
    error_message TEXT,
    created_at TIMESTAMP
);
```

## 7. API Endpoints

### Data Endpoints
```
GET /api/v1/commodities - List all commodities (filtered for long-life)
GET /api/v1/markets - List all markets
GET /api/v1/prices/current - Current prices
GET /api/v1/prices/historical - Historical price data
GET /api/v1/prices/comparison - Compare prices across markets
```

### Analytics Endpoints
```
GET /api/v1/predictions/{commodity}/{market} - Price forecasts
GET /api/v1/technical-indicators/{commodity}/{market} - Technical analysis
GET /api/v1/signals/{commodity}/{market} - Trading signals
GET /api/v1/seasonal-analysis/{commodity} - Seasonal patterns
GET /api/v1/risk-analysis - Portfolio risk metrics
```

### User Endpoints
```
GET /api/v1/watchlist - User watchlist
POST /api/v1/watchlist - Add to watchlist
DELETE /api/v1/watchlist/{id} - Remove from watchlist
GET /api/v1/alerts - User alerts
POST /api/v1/alerts - Create alert
```

## 8. Frontend Components

### New Pages
1. **Trader Dashboard** - Overview with key metrics
2. **Market Analysis** - Deep dive into specific commodities
3. **Technical Charts** - Interactive charting tool
4. **Signals** - AI-generated buy/sell signals
5. **Watchlist** - Personal tracking list
6. **Portfolio** - Trade tracking (future)
7. **Market News** - Aggregated news feed
8. **Education** - Trading tutorials

### Updated Components
- Price cards with trend indicators
- Real-time price updates (websocket)
- Advanced filtering and search
- Export data functionality
- Mobile-responsive design
- Dark mode optimization

## 9. Implementation Roadmap

### Phase 1: Data Foundation (Week 1-2)
- [ ] Update commodity list (remove perishables)
- [ ] Scrape 6 months historical data
- [ ] Set up daily automated scraping
- [ ] Update database schema
- [ ] Implement data validation

### Phase 2: Model Enhancement (Week 3-4)
- [ ] Retrain models with 6-month data
- [ ] Add technical indicators
- [ ] Implement ensemble models
- [ ] Create prediction API
- [ ] Generate trading signals

### Phase 3: Frontend Development (Week 5-6)
- [ ] Redesign dashboard for traders
- [ ] Create technical charts component
- [ ] Build signals page
- [ ] Implement watchlist
- [ ] Add alerts system

### Phase 4: Testing & Optimization (Week 7)
- [ ] Load testing
- [ ] Model accuracy validation
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Bug fixes

### Phase 5: Deployment (Week 8)
- [ ] Production deployment
- [ ] Monitor scraping jobs
- [ ] User feedback collection
- [ ] Documentation
- [ ] Marketing materials

## 10. Quality Assurance

### Data Quality
- Daily validation checks
- Price anomaly detection
- Source verification
- Data completeness monitoring

### Model Quality
- Weekly performance review
- A/B testing of model versions
- Prediction accuracy tracking
- Continuous improvement

### Code Quality
- Unit tests (>80% coverage)
- Integration tests
- End-to-end tests
- Code review process
- Type checking (TypeScript, Python type hints)

## 11. Monitoring & Maintenance

### System Monitoring
- Scraping job status
- API response times
- Database performance
- Error rates
- User activity

### Alerts
- Scraping failures
- Model performance degradation
- API downtime
- Database issues
- Security incidents

### Backup Strategy
- Daily database backups
- Model version control
- Configuration backups
- Disaster recovery plan

## 12. Security Considerations

- API rate limiting
- Input validation
- SQL injection prevention
- XSS protection
- CORS configuration
- User data encryption
- Secure authentication (Clerk)
- Regular security audits

## 13. Performance Targets

- API response time: <500ms
- Page load time: <2s
- Model prediction time: <1s
- Daily scraping completion: <30 minutes
- Database query time: <100ms
- 99.9% uptime

## 14. Success Metrics

- Model prediction accuracy: >95%
- User engagement: Daily active users
- Data freshness: Updated within 24 hours
- API availability: 99.9%
- User satisfaction: >4.5/5 rating
- Feature adoption: >60% use core features

## 15. Future Enhancements

- Mobile app (React Native)
- Real-time price updates (WebSocket)
- Portfolio management system
- Automated trading (with user approval)
- Collaborative features (discussions, tips)
- Premium features (advanced analytics)
- Integration with commodity exchanges
- WhatsApp/SMS alerts
- API for third-party integration
- Machine learning model marketplace

---

## Immediate Action Items

1. **Stop scraping perishable vegetables**
2. **Scrape 6 months data for selected commodities**
3. **Set up daily scraping cron job**
4. **Retrain models with larger dataset**
5. **Update frontend to show trader-focused metrics**
6. **Add technical indicators to backend**
7. **Create trading signals generation system**
8. **Test with sample traders for feedback**

## Technology Stack

**Backend:**
- Python 3.14
- FastAPI
- SQLAlchemy
- scikit-learn, TensorFlow
- APScheduler
- pandas, numpy

**Frontend:**
- React 18
- TypeScript
- TailwindCSS
- Recharts
- React Query
- Zustand

**Infrastructure:**
- PostgreSQL/SQLite
- Docker
- Nginx
- Linux (systemd)

**DevOps:**
- Git version control
- CI/CD pipeline
- Automated testing
- Logging (Loguru)
- Monitoring (Prometheus/Grafana)
