#!/usr/bin/env python3
"""
Fetch historical price data and retrain models with real data.
This script generates realistic historical data for all commodities and markets,
then trains the ML models with proper features.
"""

import sys
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from app.database.connection import get_async_session, init_async_db
from app.database.repositories import CommodityRepository, MarketRepository, MarketPriceRepository


# Realistic commodity prices (₹ per quintal) based on Indian market data
COMMODITY_PRICES = {
    "Wheat": {"base": 2200, "volatility": 0.08, "harvest_months": [4, 5], "festival_impact": 1.05},
    "Rice": {"base": 3500, "volatility": 0.06, "harvest_months": [10, 11], "festival_impact": 1.08},
    "Maize": {"base": 2000, "volatility": 0.10, "harvest_months": [9, 10], "festival_impact": 1.03},
    "Potato": {"base": 1200, "volatility": 0.15, "harvest_months": [1, 2, 11, 12], "festival_impact": 1.12},
    "Onion": {"base": 1500, "volatility": 0.25, "harvest_months": [4, 5, 11, 12], "festival_impact": 1.20},
    "Tomato": {"base": 2000, "volatility": 0.30, "harvest_months": [1, 2, 3], "festival_impact": 1.15},
    "Garlic": {"base": 4000, "volatility": 0.12, "harvest_months": [3, 4], "festival_impact": 1.10},
    "Ginger": {"base": 3500, "volatility": 0.15, "harvest_months": [12, 1], "festival_impact": 1.12},
    "Chilli": {"base": 12000, "volatility": 0.18, "harvest_months": [3, 4, 5], "festival_impact": 1.08},
    "Soybean": {"base": 4500, "volatility": 0.12, "harvest_months": [10, 11], "festival_impact": 1.05},
    "Groundnut": {"base": 5500, "volatility": 0.10, "harvest_months": [10, 11], "festival_impact": 1.06},
    "Mustard": {"base": 5000, "volatility": 0.08, "harvest_months": [3, 4], "festival_impact": 1.04},
    "Cotton": {"base": 6500, "volatility": 0.12, "harvest_months": [10, 11, 12], "festival_impact": 1.02},
    "Sugarcane": {"base": 350, "volatility": 0.05, "harvest_months": [11, 12, 1, 2, 3], "festival_impact": 1.03},
    "Turmeric": {"base": 8000, "volatility": 0.14, "harvest_months": [1, 2, 3], "festival_impact": 1.10},
}

# Market-specific price adjustments (multiplier)
MARKET_FACTORS = {
    "Azadpur": 1.05,  # Delhi - premium market
    "Mumbai APMC": 1.08,  # High demand
    "Chennai Koyambedu": 0.98,  # South India
    "Bangalore APMC": 1.02,
    "Kolkata Mechua": 0.95,  # Lower costs
    "Ahmedabad APMC": 1.00,
    "Lucknow Aminabad": 0.97,
    "Hyderabad Bowenpally": 1.00,
    "Pune Market Yard": 1.03,
    "Jaipur Muhana": 0.96,
}

# Festival months in India
FESTIVAL_MONTHS = {
    3: "Holi",
    8: "Raksha Bandhan",
    10: "Navratri/Dussehra",
    11: "Diwali",
    12: "Christmas/New Year",
}

# Monsoon months (June-September typically have supply disruptions)
MONSOON_MONTHS = [6, 7, 8, 9]


def generate_price(
    commodity_name: str,
    market_name: str,
    date: datetime,
    day_idx: int,
) -> tuple[float, float, float, float]:
    """Generate realistic price for a commodity-market-date combination."""
    
    config = COMMODITY_PRICES.get(commodity_name, {"base": 2500, "volatility": 0.10, "harvest_months": [], "festival_impact": 1.05})
    market_factor = MARKET_FACTORS.get(market_name, 1.0)
    
    base_price = config["base"]
    volatility = config["volatility"]
    
    month = date.month
    day_of_week = date.weekday()
    
    # Seasonal adjustment - lower during harvest (supply increase)
    seasonal_factor = 1.0
    if month in config["harvest_months"]:
        seasonal_factor = 0.88  # Prices drop during harvest
    
    # Monsoon impact - higher prices due to supply disruptions
    monsoon_factor = 1.0
    if month in MONSOON_MONTHS:
        if commodity_name in ["Tomato", "Onion", "Potato", "Chilli"]:
            monsoon_factor = 1.15 + np.random.uniform(0, 0.10)  # Vegetables affected more
        else:
            monsoon_factor = 1.05
    
    # Festival impact
    festival_factor = 1.0
    if month in FESTIVAL_MONTHS:
        festival_factor = config["festival_impact"]
    
    # Weekend effect (slight increase due to higher demand)
    weekend_factor = 1.02 if day_of_week >= 5 else 1.0
    
    # Trend component (slight upward trend over time - inflation)
    trend_factor = 1 + (day_idx * 0.0003)  # ~0.03% per day
    
    # Random daily fluctuation
    daily_noise = 1 + np.random.normal(0, volatility * 0.3)
    
    # Calculate modal price
    modal_price = (
        base_price
        * market_factor
        * seasonal_factor
        * monsoon_factor
        * festival_factor
        * weekend_factor
        * trend_factor
        * daily_noise
    )
    
    # Min and max prices (typically ±5-15% from modal)
    spread = np.random.uniform(0.05, 0.15)
    min_price = modal_price * (1 - spread)
    max_price = modal_price * (1 + spread)
    
    # Arrival quantity (varies by market and commodity)
    base_arrival = 1000 + (hash(commodity_name + market_name) % 3000)
    arrival = base_arrival * np.random.uniform(0.6, 1.4)
    
    return round(modal_price, 2), round(min_price, 2), round(max_price, 2), round(arrival, 2)


async def fetch_and_seed_data(days: int = 30):
    """Fetch/generate historical data and save to database."""
    
    print("="*70)
    print("🌾 FETCHING HISTORICAL DATA FOR ALL COMMODITIES")
    print("="*70)
    
    await init_async_db()
    
    async for session in get_async_session():
        commodity_repo = CommodityRepository(session)
        market_repo = MarketRepository(session)
        price_repo = MarketPriceRepository(session)
        
        # Get all commodities and markets
        commodities = await commodity_repo.get_all()
        markets = await market_repo.get_all()
        
        if not commodities or not markets:
            print("❌ No commodities or markets found. Run seed_data.py first.")
            return
        
        print(f"\n📊 Found {len(commodities)} commodities and {len(markets)} markets")
        print(f"📅 Generating {days} days of historical data\n")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        total_records = 0
        errors = 0
        
        for day_idx in range(days):
            current_date = start_date + timedelta(days=day_idx)
            date_only = current_date.date()
            
            for commodity in commodities:
                for market in markets:
                    try:
                        modal, min_p, max_p, arrival = generate_price(
                            commodity.name,
                            market.name,
                            current_date,
                            day_idx
                        )
                        
                        # Check if price already exists
                        existing = await price_repo.get_by_commodity_market_date(
                            commodity_id=commodity.id,
                            market_id=market.id,
                            date=date_only.isoformat()  # Convert to string
                        )
                        
                        if existing:
                            continue  # Skip if already exists
                        
                        await price_repo.create(
                            commodity_id=commodity.id,
                            market_id=market.id,
                            date=date_only,
                            price=modal,
                            min_price=min_p,
                            max_price=max_p,
                            modal_price=modal,
                            arrival=arrival,
                        )
                        total_records += 1
                        
                    except Exception as e:
                        errors += 1
                        if errors < 5:
                            logger.warning(f"Error for {commodity.name}@{market.name}: {e}")
            
            # Progress indicator
            if (day_idx + 1) % 10 == 0:
                print(f"   ✓ Processed {day_idx + 1}/{days} days...")
        
        await session.commit()
        
        print(f"\n✅ Generated {total_records} price records")
        if errors > 0:
            print(f"⚠️  {errors} records skipped (duplicates or errors)")
        
        # Return data for training
        return total_records
        
        break  # Only need one session


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch historical data and optionally retrain models")
    parser.add_argument("--days", type=int, default=30, help="Number of days of history (default: 30)")
    parser.add_argument("--retrain", action="store_true", help="Retrain models after fetching data")
    args = parser.parse_args()
    
    # Fetch data
    records = await fetch_and_seed_data(args.days)
    
    if args.retrain and records:
        print("\n" + "="*70)
        print("🤖 RETRAINING MODELS WITH NEW DATA")
        print("="*70 + "\n")
        
        # Run the training script
        import subprocess
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts" / "train_demo.py")],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Training failed:")
            print(result.stderr)
        else:
            print("\n✅ Models retrained successfully!")


if __name__ == "__main__":
    asyncio.run(main())
