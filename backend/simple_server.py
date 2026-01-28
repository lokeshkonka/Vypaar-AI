"""Simple development server with CORS enabled."""

import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Vypaar AI Dev Server")

# Enable CORS for all origins (development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.options("/{path_name:path}")
async def preflight_handler(path_name: str):
    """Handle CORS preflight requests."""
    return JSONResponse(content={}, status_code=200)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/inventory/dashboard")
async def inventory_dashboard():
    """Inventory dashboard data."""
    return [
        {"id": 1, "product": "Tomato", "market": "APMC Vashi", "category": "Vegetables", "current": 100, "suggested": 120},
        {"id": 2, "product": "Onion", "market": "APMC Vashi", "category": "Vegetables", "current": 80, "suggested": 100},
        {"id": 3, "product": "Potato", "market": "Dadar Market", "category": "Vegetables", "current": 150, "suggested": 160},
    ]


@app.get("/api/ai/insights")
async def ai_insights():
    """AI insights data."""
    return [
        {"id": 1, "title": "Market Trend", "description": "Prices trending upward", "priority": "high"},
        {"id": 2, "title": "Demand Alert", "description": "High demand in your region", "priority": "medium"},
    ]


@app.get("/api/model/accuracy")
async def model_accuracy():
    """Model accuracy metrics."""
    return {
        "metrics": {
            "xgboost": 0.95,
            "lightgbm": 0.93,
            "random_forest": 0.91,
            "ensemble": 0.94,
        },
        "graphData": [
            {"month": "Jan", "accuracy": 0.89},
            {"month": "Feb", "accuracy": 0.91},
            {"month": "Mar", "accuracy": 0.93},
            {"month": "Apr", "accuracy": 0.94},
        ]
    }


@app.get("/api/product-analysis")
async def product_analysis():
    """Product analysis data."""
    return {
        "selectorData": [
            {"name": "Tomato", "category": "Vegetables"},
            {"name": "Onion", "category": "Vegetables"},
        ],
        "stockMetrics": {"current": 100, "suggested": 120, "safety": 20},
        "demandGraphData": [
            {"date": "2026-01-01", "demand": 50},
            {"date": "2026-01-02", "demand": 55},
        ],
        "impactData": [
            {"factor": "Weather", "impact": 0.15},
            {"factor": "Season", "impact": 0.25},
        ],
        "recommendationTable": [
            {"recommendation": "Increase stock", "reason": "High demand expected"},
        ]
    }


@app.post("/api/forecast")
async def forecast(data: dict):
    """Forecast endpoint."""
    return {
        "forecast": "test forecast",
        "confidence": 0.92,
    }


@app.post("/users/init")
async def init_user(request_data: dict = None):
    """Initialize/sync user with backend (placeholder for development)."""
    return {
        "status": "success",
        "message": "User synchronized with backend",
        "user_id": "placeholder-user-id"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
