#!/usr/bin/env python
"""Extended seeding with more comprehensive data."""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from app.database.connection import init_async_db, get_async_session
from app.database.repositories import (
    CommodityRepository,
    MarketRepository,
    MarketPriceRepository,
)
from app.database.models import Commodity, Market, MarketPrice


# Extended commodity and market list - comprehensive agricultural products
COMMODITIES = [
    # Cereals
    {"name": "Wheat", "category": "Cereals", "unit": "Quintal"},
    {"name": "Rice", "category": "Cereals", "unit": "Quintal"},
    {"name": "Maize", "category": "Cereals", "unit": "Quintal"},
    {"name": "Bajra", "category": "Cereals", "unit": "Quintal"},
    {"name": "Jowar", "category": "Cereals", "unit": "Quintal"},
    {"name": "Barley", "category": "Cereals", "unit": "Quintal"},
    {"name": "Ragi", "category": "Cereals", "unit": "Quintal"},
    
    # Vegetables
    {"name": "Potato", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Onion", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Tomato", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Brinjal", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Cabbage", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Cauliflower", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Carrot", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Peas", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Beans", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Okra", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Capsicum", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Cucumber", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Bitter Gourd", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Bottle Gourd", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Radish", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Spinach", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Green Chilli", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Ginger", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Garlic", "category": "Vegetables", "unit": "Quintal"},
    
    # Cash Crops
    {"name": "Cotton", "category": "Cash Crops", "unit": "Quintal"},
    {"name": "Sugarcane", "category": "Cash Crops", "unit": "Quintal"},
    {"name": "Jute", "category": "Cash Crops", "unit": "Quintal"},
    {"name": "Tobacco", "category": "Cash Crops", "unit": "Quintal"},
    
    # Oilseeds
    {"name": "Groundnut", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Soybean", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Mustard", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Sunflower", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Sesame", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Castor Seed", "category": "Oilseeds", "unit": "Quintal"},
    
    # Pulses
    {"name": "Tur", "category": "Pulses", "unit": "Quintal"},
    {"name": "Moong", "category": "Pulses", "unit": "Quintal"},
    {"name": "Urad", "category": "Pulses", "unit": "Quintal"},
    {"name": "Masoor", "category": "Pulses", "unit": "Quintal"},
    {"name": "Gram", "category": "Pulses", "unit": "Quintal"},
    {"name": "Chana", "category": "Pulses", "unit": "Quintal"},
    
    # Fruits
    {"name": "Apple", "category": "Fruits", "unit": "Quintal"},
    {"name": "Banana", "category": "Fruits", "unit": "Quintal"},
    {"name": "Mango", "category": "Fruits", "unit": "Quintal"},
    {"name": "Orange", "category": "Fruits", "unit": "Quintal"},
    {"name": "Grapes", "category": "Fruits", "unit": "Quintal"},
    {"name": "Pomegranate", "category": "Fruits", "unit": "Quintal"},
    {"name": "Papaya", "category": "Fruits", "unit": "Quintal"},
    {"name": "Guava", "category": "Fruits", "unit": "Quintal"},
    {"name": "Watermelon", "category": "Fruits", "unit": "Quintal"},
    {"name": "Pineapple", "category": "Fruits", "unit": "Quintal"},
    
    # Spices
    {"name": "Turmeric", "category": "Spices", "unit": "Quintal"},
    {"name": "Chilli", "category": "Spices", "unit": "Quintal"},
    {"name": "Coriander", "category": "Spices", "unit": "Quintal"},
    {"name": "Cumin", "category": "Spices", "unit": "Quintal"},
    {"name": "Black Pepper", "category": "Spices", "unit": "Quintal"},
    {"name": "Cardamom", "category": "Spices", "unit": "Quintal"},
]

MARKETS = [
    {"name": "Azadpur", "state": "Delhi", "district": "North Delhi"},
    {"name": "Anaj Mandi", "state": "Delhi", "district": "Central Delhi"},
    {"name": "Ghazipur", "state": "Delhi", "district": "East Delhi"},
    {"name": "Mumbai (Dadar)", "state": "Maharashtra", "district": "Mumbai"},
    {"name": "Pune", "state": "Maharashtra", "district": "Pune"},
    {"name": "Nashik", "state": "Maharashtra", "district": "Nashik"},
    {"name": "Nagpur", "state": "Maharashtra", "district": "Nagpur"},
    {"name": "Bangalore", "state": "Karnataka", "district": "Bangalore Urban"},
    {"name": "Mysore", "state": "Karnataka", "district": "Mysore"},
    {"name": "Chennai", "state": "Tamil Nadu", "district": "Chennai"},
    {"name": "Coimbatore", "state": "Tamil Nadu", "district": "Coimbatore"},
    {"name": "Hyderabad", "state": "Telangana", "district": "Hyderabad"},
    {"name": "Kolkata", "state": "West Bengal", "district": "Kolkata"},
    {"name": "Jaipur", "state": "Rajasthan", "district": "Jaipur"},
    {"name": "Lucknow", "state": "Uttar Pradesh", "district": "Lucknow"},
    {"name": "Kanpur", "state": "Uttar Pradesh", "district": "Kanpur"},
    {"name": "Ahmedabad", "state": "Gujarat", "district": "Ahmedabad"},
    {"name": "Surat", "state": "Gujarat", "district": "Surat"},
    {"name": "Chandigarh", "state": "Chandigarh", "district": "Chandigarh"},
    {"name": "Ludhiana", "state": "Punjab", "district": "Ludhiana"},
    {"name": "Bhopal", "state": "Madhya Pradesh", "district": "Bhopal"},
    {"name": "Indore", "state": "Madhya Pradesh", "district": "Indore"},
]

# Base prices for all commodities
COMMODITY_PRICES = {
    # Cereals
    "Wheat": {"base": 2500, "std": 200},
    "Rice": {"base": 3200, "std": 250},
    "Maize": {"base": 1800, "std": 150},
    "Bajra": {"base": 2200, "std": 180},
    "Jowar": {"base": 2100, "std": 170},
    "Barley": {"base": 1900, "std": 160},
    "Ragi": {"base": 3000, "std": 220},
    
    # Vegetables
    "Potato": {"base": 1500, "std": 300},
    "Onion": {"base": 2000, "std": 400},
    "Tomato": {"base": 2500, "std": 500},
    "Brinjal": {"base": 1800, "std": 350},
    "Cabbage": {"base": 1200, "std": 250},
    "Cauliflower": {"base": 2000, "std": 350},
    "Carrot": {"base": 2200, "std": 300},
    "Peas": {"base": 4000, "std": 500},
    "Beans": {"base": 3500, "std": 450},
    "Okra": {"base": 2800, "std": 400},
    "Capsicum": {"base": 3000, "std": 450},
    "Cucumber": {"base": 1500, "std": 300},
    "Bitter Gourd": {"base": 2500, "std": 350},
    "Bottle Gourd": {"base": 1800, "std": 300},
    "Radish": {"base": 1200, "std": 200},
    "Spinach": {"base": 2000, "std": 350},
    "Green Chilli": {"base": 3500, "std": 600},
    "Ginger": {"base": 5000, "std": 700},
    "Garlic": {"base": 6000, "std": 800},
    
    # Cash Crops
    "Cotton": {"base": 6500, "std": 500},
    "Sugarcane": {"base": 350, "std": 30},
    "Jute": {"base": 4500, "std": 400},
    "Tobacco": {"base": 8000, "std": 700},
    
    # Oilseeds
    "Groundnut": {"base": 5500, "std": 400},
    "Soybean": {"base": 4000, "std": 350},
    "Mustard": {"base": 5000, "std": 400},
    "Sunflower": {"base": 4500, "std": 380},
    "Sesame": {"base": 12000, "std": 1000},
    "Castor Seed": {"base": 5500, "std": 450},
    
    # Pulses
    "Tur": {"base": 7000, "std": 500},
    "Moong": {"base": 8000, "std": 600},
    "Urad": {"base": 7500, "std": 550},
    "Masoor": {"base": 6000, "std": 450},
    "Gram": {"base": 5500, "std": 400},
    "Chana": {"base": 5500, "std": 400},
    
    # Fruits
    "Apple": {"base": 8000, "std": 1000},
    "Banana": {"base": 1800, "std": 300},
    "Mango": {"base": 4000, "std": 800},
    "Orange": {"base": 3500, "std": 500},
    "Grapes": {"base": 5000, "std": 700},
    "Pomegranate": {"base": 7000, "std": 900},
    "Papaya": {"base": 2000, "std": 350},
    "Guava": {"base": 2500, "std": 400},
    "Watermelon": {"base": 1500, "std": 300},
    "Pineapple": {"base": 3000, "std": 450},
    
    # Spices
    "Turmeric": {"base": 8000, "std": 800},
    "Chilli": {"base": 12000, "std": 1500},
    "Coriander": {"base": 7000, "std": 600},
    "Cumin": {"base": 20000, "std": 2000},
    "Black Pepper": {"base": 45000, "std": 4000},
    "Cardamom": {"base": 100000, "std": 10000},
}


async def seed():
    """Seed comprehensive data."""
    await init_async_db()
    
    async for session in get_async_session():
        try:
            commodity_repo = CommodityRepository(session)
            market_repo = MarketRepository(session)
            price_repo = MarketPriceRepository(session)
            
            # Upsert commodities
            commodity_ids = {}
            for c in COMMODITIES:
                existing = await commodity_repo.get_by_name(c["name"])
                if existing:
                    commodity_ids[c["name"]] = existing.id
                else:
                    created = await commodity_repo.create(**c)
                    commodity_ids[c["name"]] = created.id
            logger.info(f"Commodities: {commodity_ids}")
            
            # Upsert markets
            market_ids = {}
            for m in MARKETS:
                existing = await market_repo.get_by_name(m["name"])
                if existing:
                    market_ids[m["name"]] = existing.id
                else:
                    created = await market_repo.create(**m)
                    market_ids[m["name"]] = created.id
            logger.info(f"Markets: {market_ids}")
            
            # Generate historical prices (90 days)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)
            
            prices_created = 0
            for commodity_name, commodity_id in commodity_ids.items():
                for market_name, market_id in market_ids.items():
                    base_price = COMMODITY_PRICES[commodity_name]["base"]
                    std_dev = COMMODITY_PRICES[commodity_name]["std"]
                    
                    current_date = start_date
                    while current_date <= end_date:
                        import random
                        import math
                        
                        # Generate realistic price variation
                        noise = random.gauss(0, std_dev)
                        trend = (current_date - start_date).days * 2
                        price = base_price + trend + noise
                        price = max(price, base_price * 0.7)
                        
                        arrival = random.uniform(500, 5000)
                        min_price = price * random.uniform(0.85, 0.95)
                        max_price = price * random.uniform(1.05, 1.15)
                        
                        price_data = {
                            "commodity_id": commodity_id,
                            "market_id": market_id,
                            "date": current_date,
                            "price": round(price, 2),
                            "min_price": round(min_price, 2),
                            "max_price": round(max_price, 2),
                            "modal_price": round(price, 2),
                            "arrival": round(arrival, 2),
                        }
                        
                        # Try to create, ignore if exists
                        try:
                            await price_repo.create(**price_data)
                            prices_created += 1
                        except:
                            pass
                        
                        current_date += timedelta(days=1)
            
            await session.commit()
            logger.success(f"✅ Created {prices_created} price records")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    print("\n🌱 Seeding comprehensive commodity data...\n")
    asyncio.run(seed())
    print("\n✅ Seeding complete!\n")
