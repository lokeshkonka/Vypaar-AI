#!/usr/bin/env python3
"""Seed the database with sample commodities, markets, prices, and inventory."""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from app.database.connection import get_async_session, init_async_db
from app.database.repositories import (
    CommodityRepository,
    MarketRepository,
    MarketPriceRepository,
    InventoryRepository,
)

COMMODITIES = [
    # Cereals
    {"name": "Wheat", "category": "Cereals", "unit": "Quintal"},
    {"name": "Rice", "category": "Cereals", "unit": "Quintal"},
    {"name": "Maize", "category": "Cereals", "unit": "Quintal"},
    # Vegetables
    {"name": "Potato", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Onion", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Tomato", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Garlic", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Ginger", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Chilli", "category": "Vegetables", "unit": "Quintal"},
    # Oilseeds
    {"name": "Soybean", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Groundnut", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Mustard", "category": "Oilseeds", "unit": "Quintal"},
    # Cash Crops
    {"name": "Cotton", "category": "Cash Crops", "unit": "Quintal"},
    {"name": "Sugarcane", "category": "Cash Crops", "unit": "Quintal"},
    # Spices
    {"name": "Turmeric", "category": "Spices", "unit": "Quintal"},
]

MARKETS = [
    {"name": "Azadpur", "state": "Delhi", "district": "North Delhi"},
    {"name": "Mumbai APMC", "state": "Maharashtra", "district": "Mumbai"},
    {"name": "Chennai Koyambedu", "state": "Tamil Nadu", "district": "Chennai"},
    {"name": "Bangalore APMC", "state": "Karnataka", "district": "Bangalore"},
    {"name": "Kolkata Mechua", "state": "West Bengal", "district": "Kolkata"},
    {"name": "Ahmedabad APMC", "state": "Gujarat", "district": "Ahmedabad"},
    {"name": "Lucknow Aminabad", "state": "Uttar Pradesh", "district": "Lucknow"},
    {"name": "Hyderabad Bowenpally", "state": "Telangana", "district": "Hyderabad"},
    {"name": "Pune Market Yard", "state": "Maharashtra", "district": "Pune"},
    {"name": "Jaipur Muhana", "state": "Rajasthan", "district": "Jaipur"},
]

async def seed():
    await init_async_db()
    async for session in get_async_session():
        commodity_repo = CommodityRepository(session)
        market_repo = MarketRepository(session)
        price_repo = MarketPriceRepository(session)
        inventory_repo = InventoryRepository(session)

        # Upsert commodities
        commodity_ids = {}
        for c in COMMODITIES:
            existing = await commodity_repo.get_by_name(c["name"])
            if existing:
                commodity_ids[c["name"]] = existing.id
                continue
            created = await commodity_repo.create(**c)
            commodity_ids[c["name"]] = created.id
        logger.info(f"Commodities seeded: {commodity_ids}")

        # Upsert markets
        market_ids = {}
        for m in MARKETS:
            existing = await market_repo.get_by_name(m["name"])
            if existing:
                market_ids[m["name"]] = existing.id
                continue
            created = await market_repo.create(**m)
            market_ids[m["name"]] = created.id
        logger.info(f"Markets seeded: {market_ids}")

        # Seed 30 days of prices for all commodities in all markets
        start_date = datetime.utcnow().date() - timedelta(days=30)
        prices = []
        market_names = [m["name"] for m in MARKETS]
        
        for day in range(30):
            date = start_date + timedelta(days=day)
            for market_name in market_names:
                market_id = market_ids[market_name]
                for commodity in COMMODITIES:
                    commodity_id = commodity_ids[commodity["name"]]
                    # Base prices per commodity category
                    if commodity["category"] == "Cereals":
                        base_price = 2500.0
                    elif commodity["category"] == "Vegetables":
                        base_price = 2000.0
                    elif commodity["category"] == "Oilseeds":
                        base_price = 5000.0
                    elif commodity["category"] == "Cash Crops":
                        base_price = 4000.0
                    elif commodity["category"] == "Spices":
                        base_price = 8000.0
                    else:
                        base_price = 3000.0
                    
                    # Add variation based on commodity and market
                    base_price += (commodity_id * 100) + (market_id * 50)
                    # Sinusoidal daily variation
                    modal = base_price * (1 + (0.05 * ((day % 7) - 3) / 3))
                    prices.append({
                        "commodity_id": commodity_id,
                        "market_id": market_id,
                        "date": date,
                        "price": round(modal, 2),
                        "min_price": round(modal * 0.9, 2),
                        "max_price": round(modal * 1.1, 2),
                        "modal_price": round(modal, 2),
                        "arrival": round(1000 + 50 * day + market_id * 100, 2),
                    })
        upserted = 0
        for price in prices:
            await price_repo.create_or_update_price(price)
            upserted += 1
        logger.info(f"Seeded {upserted} market price records")

        # Seed inventory for Wheat in Azadpur
        wheat_id = commodity_ids["Wheat"]
        azadpur_id = market_ids["Azadpur"]
        existing_inv = await inventory_repo.get_by_commodity_market(wheat_id, azadpur_id)
        if not existing_inv:
            inv = await inventory_repo.create(
                commodity_id=wheat_id,
                market_id=azadpur_id,
                current_stock=1200.0,
                optimal_stock=2000.0,
                min_stock=800.0,
                max_stock=3000.0,
                reorder_point=1500.0,
            )
            logger.info(f"Created inventory id={inv.id} for Wheat@Azadpur")
        else:
            logger.info("Inventory already exists for Wheat@Azadpur")

        # Commit
        await session.commit()
        logger.success("✅ Seeding completed")

if __name__ == "__main__":
    try:
        asyncio.run(seed())
    except Exception as e:
        logger.exception(f"Seeding failed: {e}")
        sys.exit(1)
