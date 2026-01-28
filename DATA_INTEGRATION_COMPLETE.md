# Data Integration Complete - Frontend & Backend Mapping

## 🗄️ Backend Database Content

### Available Data
- **Commodities**: 4 items (Tomato, Wheat, Rice, Potato)
- **Markets**: 4 items (Vashi, Azadpur Mandi, Azadpur, Mumbai Dadar)
- **Market Prices**: 28+ records (historical commodity prices)
- **Inventory**: 1+ records (current stock levels with optimal stock)

### Database Repositories
```
CommodityRepository    → Fetches commodities list
MarketRepository       → Fetches markets list
MarketPriceRepository  → Fetches historical price data
InventoryRepository    → Fetches current stock levels
PredictionMetricsRepository → Stores model metrics
```

---

## 🔗 Backend Endpoints & Response Data

### 1. GET `/api/commodities`
**Response:**
```json
[
  { "id": 1, "name": "Tomato" },
  { "id": 2, "name": "Wheat" },
  { "id": 3, "name": "Rice" },
  { "id": 4, "name": "Potato" }
]
```
**Used by:** ForecastContext, ProductSelector

---

### 2. GET `/api/markets`
**Response:**
```json
[
  { "id": 1, "name": "Vashi", "state": "Maharashtra", "city": "Mumbai" },
  { "id": 2, "name": "Azadpur Mandi", "state": "Delhi", "city": "Delhi" },
  { "id": 3, "name": "Azadpur", "state": "Delhi", "city": "North Delhi" },
  { "id": 4, "name": "Mumbai (Dadar)", "state": "Maharashtra", "city": "Mumbai" }
]
```
**Used by:** ForecastContext, MarketSelector

---

### 3. GET `/api/product-analysis`
**Response:**
```json
{
  "selectorData": {
    "market": "Vashi",
    "product": "Tomato",
    "forecastRange": "Next 7 Days"
  },
  "stockMetrics": {
    "predictedDemand": 1320,
    "stockNeeded": 2000,
    "overstockRisk": 0,
    "understockRisk": 40
  },
  "demandGraphData": [
    { "day": "Mon", "actual": 500, "forecast": 525 },
    { "day": "Tue", "actual": 491, "forecast": 515 }
  ],
  "impactData": {
    "festival": [],
    "weather": []
  },
  "recommendationTable": [
    { "product": "Wheat", "current": 1200, "suggested": 2000, "buffer": 800, "risk": "High" }
  ]
}
```
**Used by:** ContextAnalysis, ProductAnalysis components

---

### 4. GET `/api/ai/insights`
**Response:**
```json
[
  {
    "title": "Insight Title",
    "description": "Detailed insight description",
    "type": "price_trend|demand_forecast|supply_alert"
  }
]
```
**Used by:** InsightContext, Insights dashboard

---

### 5. GET `/api/model/accuracy`
**Response:**
```json
{
  "metrics": {
    "overall": 85,
    "precision": 0.88,
    "recall": 0.82,
    "f1Score": 0.85
  },
  "graphData": [
    { "day": "Mon", "predicted": 450, "actual": 480 },
    { "day": "Tue", "predicted": 520, "actual": 510 }
  ]
}
```
**Used by:** ModelContext, ModelAccuracy components

---

### 6. GET `/api/inventory/dashboard`
**Response:**
```json
[
  {
    "id": "1_1",
    "market": "Vashi",
    "product": "Wheat",
    "category": "Grains",
    "current": 1200,
    "optimal": 2000,
    "risk": "high"
  }
]
```
**Used by:** InventoryContext, Inventory dashboard

---

### 7. POST `/users/init`
**Response:**
```json
{
  "status": "success",
  "message": "User initialized",
  "timestamp": "2026-01-28T12:23:16.627136+00:00"
}
```
**Used by:** UserSync component

---

### 8. POST `/api/forecast`
**Request:**
```json
{
  "state": "Maharashtra",
  "city": "Mumbai",
  "market": "Vashi",
  "category": "Vegetables",
  "product": "Tomato",
  "forecastRange": 7
}
```
**Used by:** GenerateForecastCTA

---

## 🎯 Frontend Context Mapping

### ForecastContext
```typescript
ForecastSelection {
  state?: string;
  city?: string;
  market?: string;
  category?: string;
  product?: string;
  forecastRange?: "7" | "14";
}

ForecastContextType {
  markets: Market[]                    // from /api/markets
  commodities: Commodity[]             // from /api/commodities
  categories: string[]                 // computed: ["Vegetables", "Grains"]
  forecastRanges: [{ label, value }]  // static: 7, 14 days
}
```

### ContextAnalysis
```typescript
AnalysisContextValue {
  selectorData: SelectorData           // from /api/product-analysis
  stockMetrics: StockMetrics           // from /api/product-analysis
  demandGraphData: DemandGraphPoint[]  // from /api/product-analysis
  impactData: ImpactData               // from /api/product-analysis
  recommendationTable: RecommendationRow[] // from /api/product-analysis
}
```

### InsightContext
```typescript
InsightContextValue {
  insights: InsightItem[]              // from /api/ai/insights
  isLoading: boolean
}
```

### ModelContext
```typescript
ModelContextValue {
  metrics: ModelAccuracyMetrics        // from /api/model/accuracy
  graphData: ModelGraphPoint[]         // from /api/model/accuracy
  isLoading: boolean
}
```

### InventoryContext
```typescript
InventoryContextValue {
  inventory: InventoryRow[]            // filtered from /api/inventory/dashboard
  allInventory: InventoryRow[]         // from /api/inventory/dashboard
  filters: InventoryFilters
  isUpdating: boolean
  isLoading: boolean
}
```

---

## 🔄 Data Flow Diagram

```
Backend Database
    ↓
app/api/frontend.py endpoints
    ↓
Frontend useEffect() fetches
    ↓
Context providers setState()
    ↓
Components useContext()
    ↓
Components render with data
```

---

## ✅ Commodity Category Mapping

Static mapping in ForecastContext:
```typescript
{
  "Tomato": "Vegetables",
  "Potato": "Vegetables",
  "Wheat": "Grains",
  "Rice": "Grains"
}
```

---

## 🔑 Key Features

✅ **Real-time Data**: All contexts fetch from backend on mount
✅ **Error Handling**: Graceful fallbacks with empty arrays
✅ **Loading States**: isLoading flags in contexts
✅ **Type Safety**: Full TypeScript interfaces
✅ **Market Filtering**: State → City → Market hierarchy
✅ **Category Filtering**: Automatic category extraction
✅ **Inventory Filtering**: Filter by market, category, product
✅ **Backend Integration**: All endpoints returning real data

---

## 📋 Checklist

- [x] ForecastContext fetches markets & commodities
- [x] ContextAnalysis fetches product analysis data
- [x] InsightContext fetches insights
- [x] ModelContext fetches model accuracy
- [x] InventoryContext fetches inventory data
- [x] Removed all hardcoded dummy data
- [x] Removed marketType selector (simplified to State→City→Market)
- [x] All contexts have error handling
- [x] All contexts have loading states
- [x] Type safety maintained across all data

---

## 🚀 Next Steps

1. Frontend tests to verify all data flows correctly
2. Monitor console for any API errors
3. Test filtering and selection across components
4. Verify all dashboard pages load without errors
5. Performance testing with production data

