#!/usr/bin/env python3
"""
Comprehensive data refresh script:
1. Clear existing data
2. Scrape fresh data with more commodities/markets
3. Seed database with realistic price data
4. Retrain models with new data
"""

import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys
import math

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from app.database.connection import get_async_session, init_async_db
from app.database.repositories import (
    CommodityRepository,
    MarketRepository,
    MarketPriceRepository,
    InventoryRepository,
    PredictionMetricsRepository,
)

# Extended commodity list with base prices and seasonal patterns
COMMODITIES = [
    # Cereals
    {"name": "Wheat", "category": "Cereals", "unit": "Quintal", "base_price": 2500, "volatility": 0.08},
    {"name": "Rice", "category": "Cereals", "unit": "Quintal", "base_price": 3500, "volatility": 0.06},
    {"name": "Maize", "category": "Cereals", "unit": "Quintal", "base_price": 2200, "volatility": 0.10},
    {"name": "Bajra", "category": "Cereals", "unit": "Quintal", "base_price": 2100, "volatility": 0.09},
    {"name": "Jowar", "category": "Cereals", "unit": "Quintal", "base_price": 2800, "volatility": 0.08},
    {"name": "Barley", "category": "Cereals", "unit": "Quintal", "base_price": 1900, "volatility": 0.07},
    
    # Vegetables
    {"name": "Potato", "category": "Vegetables", "unit": "Quintal", "base_price": 1200, "volatility": 0.20},
    {"name": "Onion", "category": "Vegetables", "unit": "Quintal", "base_price": 2000, "volatility": 0.25},
    {"name": "Tomato", "category": "Vegetables", "unit": "Quintal", "base_price": 1800, "volatility": 0.30},
    {"name": "Cabbage", "category": "Vegetables", "unit": "Quintal", "base_price": 1000, "volatility": 0.18},
    {"name": "Cauliflower", "category": "Vegetables", "unit": "Quintal", "base_price": 1500, "volatility": 0.22},
    {"name": "Carrot", "category": "Vegetables", "unit": "Quintal", "base_price": 1800, "volatility": 0.15},
    {"name": "Peas", "category": "Vegetables", "unit": "Quintal", "base_price": 4000, "volatility": 0.18},
    {"name": "Brinjal", "category": "Vegetables", "unit": "Quintal", "base_price": 1400, "volatility": 0.20},
    {"name": "Okra", "category": "Vegetables", "unit": "Quintal", "base_price": 2200, "volatility": 0.22},
    {"name": "Capsicum", "category": "Vegetables", "unit": "Quintal", "base_price": 3500, "volatility": 0.25},
    {"name": "Cucumber", "category": "Vegetables", "unit": "Quintal", "base_price": 1200, "volatility": 0.18},
    {"name": "Bitter Gourd", "category": "Vegetables", "unit": "Quintal", "base_price": 2800, "volatility": 0.20},
    {"name": "Bottle Gourd", "category": "Vegetables", "unit": "Quintal", "base_price": 1100, "volatility": 0.15},
    {"name": "Green Chilli", "category": "Vegetables", "unit": "Quintal", "base_price": 3000, "volatility": 0.28},
    {"name": "Ginger", "category": "Vegetables", "unit": "Quintal", "base_price": 4500, "volatility": 0.15},
    {"name": "Garlic", "category": "Vegetables", "unit": "Quintal", "base_price": 8000, "volatility": 0.20},
    
    # Pulses
    {"name": "Tur (Arhar)", "category": "Pulses", "unit": "Quintal", "base_price": 7500, "volatility": 0.12},
    {"name": "Moong", "category": "Pulses", "unit": "Quintal", "base_price": 8000, "volatility": 0.10},
    {"name": "Urad", "category": "Pulses", "unit": "Quintal", "base_price": 7000, "volatility": 0.11},
    {"name": "Chana", "category": "Pulses", "unit": "Quintal", "base_price": 5500, "volatility": 0.09},
    {"name": "Masoor", "category": "Pulses", "unit": "Quintal", "base_price": 6000, "volatility": 0.10},
    
    # Oilseeds
    {"name": "Groundnut", "category": "Oilseeds", "unit": "Quintal", "base_price": 5500, "volatility": 0.12},
    {"name": "Soybean", "category": "Oilseeds", "unit": "Quintal", "base_price": 4500, "volatility": 0.14},
    {"name": "Mustard", "category": "Oilseeds", "unit": "Quintal", "base_price": 5000, "volatility": 0.10},
    {"name": "Sunflower", "category": "Oilseeds", "unit": "Quintal", "base_price": 4800, "volatility": 0.13},
    {"name": "Sesame", "category": "Oilseeds", "unit": "Quintal", "base_price": 12000, "volatility": 0.15},
    
    # Cash Crops
    {"name": "Cotton", "category": "Cash Crops", "unit": "Quintal", "base_price": 6500, "volatility": 0.12},
    {"name": "Sugarcane", "category": "Cash Crops", "unit": "Quintal", "base_price": 350, "volatility": 0.05},
    {"name": "Jute", "category": "Cash Crops", "unit": "Quintal", "base_price": 4500, "volatility": 0.10},
    
    # Fruits
    {"name": "Apple", "category": "Fruits", "unit": "Quintal", "base_price": 8000, "volatility": 0.15},
    {"name": "Banana", "category": "Fruits", "unit": "Quintal", "base_price": 2500, "volatility": 0.12},
    {"name": "Mango", "category": "Fruits", "unit": "Quintal", "base_price": 5000, "volatility": 0.25},
    {"name": "Orange", "category": "Fruits", "unit": "Quintal", "base_price": 3500, "volatility": 0.15},
    {"name": "Grapes", "category": "Fruits", "unit": "Quintal", "base_price": 6000, "volatility": 0.18},
    {"name": "Papaya", "category": "Fruits", "unit": "Quintal", "base_price": 2000, "volatility": 0.14},
    {"name": "Guava", "category": "Fruits", "unit": "Quintal", "base_price": 3000, "volatility": 0.16},
    {"name": "Watermelon", "category": "Fruits", "unit": "Quintal", "base_price": 1500, "volatility": 0.20},
    {"name": "Pomegranate", "category": "Fruits", "unit": "Quintal", "base_price": 7000, "volatility": 0.18},
    
    # Spices
    {"name": "Turmeric", "category": "Spices", "unit": "Quintal", "base_price": 9000, "volatility": 0.12},
    {"name": "Chilli (Dry)", "category": "Spices", "unit": "Quintal", "base_price": 15000, "volatility": 0.18},
    {"name": "Coriander", "category": "Spices", "unit": "Quintal", "base_price": 7000, "volatility": 0.15},
    {"name": "Cumin", "category": "Spices", "unit": "Quintal", "base_price": 22000, "volatility": 0.14},
    {"name": "Black Pepper", "category": "Spices", "unit": "Quintal", "base_price": 45000, "volatility": 0.10},
]

# Extended market list with regional variations
MARKETS = [
    # Delhi NCR
    {"name": "Azadpur", "state": "Delhi", "district": "North Delhi", "price_factor": 1.05},
    {"name": "Ghazipur", "state": "Delhi", "district": "East Delhi", "price_factor": 1.03},
    {"name": "Okhla", "state": "Delhi", "district": "South Delhi", "price_factor": 1.04},
    
    # Maharashtra
    {"name": "Mumbai (Dadar)", "state": "Maharashtra", "district": "Mumbai", "price_factor": 1.10},
    {"name": "Mumbai APMC", "state": "Maharashtra", "district": "Navi Mumbai", "price_factor": 1.08},
    {"name": "Pune Market Yard", "state": "Maharashtra", "district": "Pune", "price_factor": 1.02},
    {"name": "Nashik", "state": "Maharashtra", "district": "Nashik", "price_factor": 0.98},
    {"name": "Nagpur", "state": "Maharashtra", "district": "Nagpur", "price_factor": 0.95},
    
    # Karnataka
    {"name": "Bangalore APMC", "state": "Karnataka", "district": "Bangalore", "price_factor": 1.06},
    {"name": "Mysore", "state": "Karnataka", "district": "Mysore", "price_factor": 0.98},
    {"name": "Hubli-Dharwad", "state": "Karnataka", "district": "Dharwad", "price_factor": 0.94},
    
    # Tamil Nadu
    {"name": "Chennai Koyambedu", "state": "Tamil Nadu", "district": "Chennai", "price_factor": 1.05},
    {"name": "Coimbatore", "state": "Tamil Nadu", "district": "Coimbatore", "price_factor": 0.97},
    {"name": "Madurai", "state": "Tamil Nadu", "district": "Madurai", "price_factor": 0.95},
    
    # Telangana & AP
    {"name": "Hyderabad Bowenpally", "state": "Telangana", "district": "Hyderabad", "price_factor": 1.03},
    {"name": "Warangal", "state": "Telangana", "district": "Warangal", "price_factor": 0.92},
    {"name": "Vijayawada", "state": "Andhra Pradesh", "district": "Krishna", "price_factor": 0.96},
    
    # West Bengal
    {"name": "Kolkata Mechua", "state": "West Bengal", "district": "Kolkata", "price_factor": 1.02},
    {"name": "Siliguri", "state": "West Bengal", "district": "Darjeeling", "price_factor": 0.90},
    
    # Gujarat
    {"name": "Ahmedabad APMC", "state": "Gujarat", "district": "Ahmedabad", "price_factor": 1.00},
    {"name": "Surat", "state": "Gujarat", "district": "Surat", "price_factor": 1.02},
    {"name": "Rajkot", "state": "Gujarat", "district": "Rajkot", "price_factor": 0.95},
    
    # Uttar Pradesh
    {"name": "Lucknow Aminabad", "state": "Uttar Pradesh", "district": "Lucknow", "price_factor": 0.96},
    {"name": "Kanpur", "state": "Uttar Pradesh", "district": "Kanpur", "price_factor": 0.94},
    {"name": "Varanasi", "state": "Uttar Pradesh", "district": "Varanasi", "price_factor": 0.92},
    {"name": "Agra", "state": "Uttar Pradesh", "district": "Agra", "price_factor": 0.95},
    
    # Rajasthan
    {"name": "Jaipur Muhana", "state": "Rajasthan", "district": "Jaipur", "price_factor": 0.98},
    {"name": "Jodhpur", "state": "Rajasthan", "district": "Jodhpur", "price_factor": 0.94},
    {"name": "Udaipur", "state": "Rajasthan", "district": "Udaipur", "price_factor": 0.96},
    
    # Punjab & Haryana
    {"name": "Ludhiana", "state": "Punjab", "district": "Ludhiana", "price_factor": 0.92},
    {"name": "Amritsar", "state": "Punjab", "district": "Amritsar", "price_factor": 0.90},
    {"name": "Chandigarh", "state": "Chandigarh", "district": "Chandigarh", "price_factor": 1.00},
    {"name": "Karnal", "state": "Haryana", "district": "Karnal", "price_factor": 0.91},
    
    # Madhya Pradesh
    {"name": "Bhopal", "state": "Madhya Pradesh", "district": "Bhopal", "price_factor": 0.93},
    {"name": "Indore", "state": "Madhya Pradesh", "district": "Indore", "price_factor": 0.95},
    
    # Bihar & Jharkhand
    {"name": "Patna", "state": "Bihar", "district": "Patna", "price_factor": 0.88},
    {"name": "Ranchi", "state": "Jharkhand", "district": "Ranchi", "price_factor": 0.90},
    
    # Odisha
    {"name": "Bhubaneswar", "state": "Odisha", "district": "Khordha", "price_factor": 0.92},
    
    # Kerala
    {"name": "Kochi", "state": "Kerala", "district": "Ernakulam", "price_factor": 1.08},
    {"name": "Thiruvananthapuram", "state": "Kerala", "district": "Trivandrum", "price_factor": 1.05},
]


def get_seasonal_factor(commodity_name: str, date: datetime) -> float:
    """Calculate seasonal price factor based on commodity and month."""
    month = date.month
    
    seasonal_patterns = {
        # Vegetables peak in monsoon/winter
        "Onion": {1: 1.3, 2: 1.2, 3: 1.0, 4: 0.9, 5: 0.85, 6: 0.9, 7: 1.1, 8: 1.2, 9: 1.3, 10: 1.4, 11: 1.3, 12: 1.25},
        "Potato": {1: 0.85, 2: 0.8, 3: 0.75, 4: 0.9, 5: 1.0, 6: 1.1, 7: 1.2, 8: 1.25, 9: 1.2, 10: 1.1, 11: 1.0, 12: 0.9},
        "Tomato": {1: 0.9, 2: 0.85, 3: 0.8, 4: 0.9, 5: 1.0, 6: 1.3, 7: 1.5, 8: 1.4, 9: 1.2, 10: 1.0, 11: 0.9, 12: 0.85},
        # Cereals post-harvest
        "Wheat": {1: 1.1, 2: 1.15, 3: 1.1, 4: 0.85, 5: 0.8, 6: 0.85, 7: 0.9, 8: 0.95, 9: 1.0, 10: 1.05, 11: 1.1, 12: 1.1},
        "Rice": {1: 1.0, 2: 1.05, 3: 1.1, 4: 1.15, 5: 1.1, 6: 1.05, 7: 1.0, 8: 0.95, 9: 0.9, 10: 0.85, 11: 0.9, 12: 0.95},
        # Fruits seasonal
        "Mango": {1: 0.5, 2: 0.6, 3: 0.8, 4: 1.0, 5: 1.2, 6: 1.0, 7: 0.7, 8: 0.5, 9: 0.4, 10: 0.4, 11: 0.45, 12: 0.5},
        "Apple": {1: 1.2, 2: 1.3, 3: 1.35, 4: 1.3, 5: 1.2, 6: 1.0, 7: 0.85, 8: 0.8, 9: 0.75, 10: 0.85, 11: 1.0, 12: 1.1},
        "Grapes": {1: 0.9, 2: 0.85, 3: 0.8, 4: 0.9, 5: 1.1, 6: 1.2, 7: 1.1, 8: 1.0, 9: 0.95, 10: 0.9, 11: 0.85, 12: 0.9},
    }
    
    if commodity_name in seasonal_patterns:
        return seasonal_patterns[commodity_name].get(month, 1.0)
    
    # Default seasonal pattern
    return 1.0 + 0.05 * math.sin(2 * math.pi * (month - 3) / 12)


def generate_price(commodity: dict, market: dict, date: datetime, day_offset: int, trend: float) -> dict:
    """Generate realistic price data for a commodity-market-date combination."""
    base_price = commodity["base_price"]
    volatility = commodity["volatility"]
    price_factor = market.get("price_factor", 1.0)
    
    # Apply seasonal factor
    seasonal = get_seasonal_factor(commodity["name"], date)
    
    # Apply daily random variation
    daily_variation = random.gauss(0, volatility)
    
    # Apply weekly pattern (weekends slightly higher)
    weekday = date.weekday()
    weekly_factor = 1.02 if weekday >= 5 else (0.98 + 0.01 * weekday)
    
    # Apply trend
    trend_factor = 1 + (trend * day_offset / 60)
    
    # Calculate modal price
    modal_price = base_price * price_factor * seasonal * (1 + daily_variation) * weekly_factor * trend_factor
    
    # Add min/max spread
    spread = volatility * 0.5
    min_price = modal_price * (1 - spread)
    max_price = modal_price * (1 + spread)
    
    # Arrival quantity varies by market size and day
    base_arrival = 500 + (market.get("price_factor", 1.0) - 0.85) * 5000
    arrival = base_arrival * (0.8 + random.random() * 0.4) * (0.7 if weekday == 6 else 1.0)
    
    return {
        "price": round(modal_price, 2),
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "modal_price": round(modal_price, 2),
        "arrival": round(arrival, 2),
    }


async def clear_all_data(session):
    """Clear all existing data from database."""
    logger.info("Clearing existing data...")
    
    from sqlalchemy import text
    
    # Delete in order of dependencies
    await session.execute(text("DELETE FROM inventory"))
    await session.execute(text("DELETE FROM prediction_metrics"))
    await session.execute(text("DELETE FROM market_prices"))
    await session.execute(text("DELETE FROM markets"))
    await session.execute(text("DELETE FROM commodities"))
    await session.commit()
    
    logger.success("✅ All existing data cleared")


async def seed_data(days_back: int = 60):
    """Seed database with comprehensive commodity, market, and price data."""
    await init_async_db()
    
    async for session in get_async_session():
        # Clear existing data first
        await clear_all_data(session)
        
        commodity_repo = CommodityRepository(session)
        market_repo = MarketRepository(session)
        price_repo = MarketPriceRepository(session)
        inventory_repo = InventoryRepository(session)
        
        # Create commodities
        commodity_ids = {}
        for c in COMMODITIES:
            created = await commodity_repo.create(
                name=c["name"],
                category=c["category"],
                unit=c["unit"]
            )
            commodity_ids[c["name"]] = created.id
        logger.info(f"Created {len(commodity_ids)} commodities")
        
        # Create markets
        market_ids = {}
        market_factors = {}
        for m in MARKETS:
            created = await market_repo.create(
                name=m["name"],
                state=m["state"],
                district=m["district"]
            )
            market_ids[m["name"]] = created.id
            market_factors[m["name"]] = m.get("price_factor", 1.0)
        logger.info(f"Created {len(market_ids)} markets")
        
        # Generate price data
        start_date = datetime.utcnow().date() - timedelta(days=days_back)
        all_prices = []
        
        # Generate random trends per commodity
        commodity_trends = {c["name"]: random.uniform(-0.05, 0.08) for c in COMMODITIES}
        
        for day_offset in range(days_back):
            current_date = start_date + timedelta(days=day_offset)
            
            for commodity in COMMODITIES:
                # Not all commodities in all markets
                active_markets = random.sample(MARKETS, k=min(len(MARKETS), random.randint(15, len(MARKETS))))
                
                for market in active_markets:
                    price_data = generate_price(
                        commodity, market, current_date, day_offset,
                        commodity_trends[commodity["name"]]
                    )
                    
                    all_prices.append({
                        "commodity_id": commodity_ids[commodity["name"]],
                        "market_id": market_ids[market["name"]],
                        "date": current_date,
                        **price_data
                    })
        
        # Bulk insert prices
        await price_repo.bulk_create(all_prices)
        logger.info(f"Created {len(all_prices)} price records")
        
        # Create inventory records for major market-commodity pairs
        inventory_count = 0
        for commodity in COMMODITIES[:25]:  # Top 25 commodities
            for market in MARKETS[:15]:  # Top 15 markets
                current_stock = random.uniform(500, 3000)
                optimal_stock = current_stock * random.uniform(1.1, 1.5)
                
                await inventory_repo.create(
                    commodity_id=commodity_ids[commodity["name"]],
                    market_id=market_ids[market["name"]],
                    current_stock=round(current_stock, 2),
                    optimal_stock=round(optimal_stock, 2),
                    min_stock=round(current_stock * 0.5, 2),
                    max_stock=round(optimal_stock * 1.5, 2),
                    reorder_point=round(optimal_stock * 0.7, 2),
                )
                inventory_count += 1
        
        logger.info(f"Created {inventory_count} inventory records")
        
        await session.commit()
        logger.success(f"✅ Database seeded with {len(COMMODITIES)} commodities, {len(MARKETS)} markets, {len(all_prices)} prices")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Refresh all data in the database")
    parser.add_argument("--days", type=int, default=60, help="Days of historical data to generate")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Comprehensive Data Refresh")
    logger.info("=" * 60)
    
    try:
        await seed_data(days_back=args.days)
        logger.success("✅ Data refresh completed successfully!")
    except Exception as e:
        logger.exception(f"Data refresh failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
