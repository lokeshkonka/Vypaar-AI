#!/usr/bin/env python

import asyncio
from datetime import datetime, timedelta
from loguru import logger

from app.database.connection import init_async_db, get_async_session
from app.database.repositories import (
    CommodityRepository,
    MarketRepository,
    MarketPriceRepository,
)
from app.database.models import Commodity, Market, MarketPrice

COMMODITIES = [
    {"name": "Wheat", "category": "Cereals"},
    {"name": "Rice", "category": "Cereals"},
    {"name": "Maize", "category": "Cereals"},
    {"name": "Potato", "category": "Vegetables"},
    {"name": "Onion", "category": "Vegetables"},
    {"name": "Tomato", "category": "Vegetables"},
]

MARKETS = [
    {"name": "Azadpur", "state": "Delhi", "city": "Delhi"},
    {"name": "Mumbai (Dadar)", "state": "Maharashtra", "city": "Mumbai"},
    {"name": "Bangalore", "state": "Karnataka", "city": "Bangalore"},
    {"name": "Chennai", "state": "Tamil Nadu", "city": "Chennai"},
]

COMMODITY_PRICES = {
    "Wheat": {"base": 2500, "std": 200},
    "Rice": {"base": 3200, "std": 250},
    "Maize": {"base": 1800, "std": 150},
    "Potato": {"base": 2000, "std": 300},
    "Onion": {"base": 2500, "std": 400},
    "Tomato": {"base": 3000, "std": 500},
}

async def seed():

    await init_async_db()
    
    async for session in get_async_session():
        try:
            commodity_repo = CommodityRepository(session)
            market_repo = MarketRepository(session)
            price_repo = MarketPriceRepository(session)
            
            commodity_ids = {}
            for c in COMMODITIES:
                existing = await commodity_repo.get_by_name(c["name"])
                if existing:
                    commodity_ids[c["name"]] = existing.id
                else:
                    created = await commodity_repo.create(**c)
                    commodity_ids[c["name"]] = created.id
            logger.info(f"Commodities: {commodity_ids}")
            
            market_ids = {}
            for m in MARKETS:
                existing = await market_repo.get_by_name(m["name"])
                if existing:
                    market_ids[m["name"]] = existing.id
                else:
                    created = await market_repo.create(**m)
                    market_ids[m["name"]] = created.id
            logger.info(f"Markets: {market_ids}")
            
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
                        
                        noise = random.gauss(0, std_dev)
                        trend = (current_date - start_date).days * 2
                        price = base_price + trend + noise
                        price = max(price, base_price * 0.7)
                        
                        arrival = random.uniform(500, 5000)
                        
                        price_data = {
                            "commodity_id": commodity_id,
                            "market_id": market_id,
                            "date": current_date,
                            "price": round(price, 2),
                            "arrival": round(arrival, 2),
                        }
                        
                        try:
                            await price_repo.create(**price_data)
                            prices_created += 1
                        except:
                            pass
                        
                        current_date += timedelta(days=1)
            
            await session.commit()
            logger.success(f" Created {prices_created} price records")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    print("\n Seeding comprehensive commodity data...\n")
    asyncio.run(seed())
    print("\n Seeding complete!\n")
