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
    {"name": "Wheat", "category": "Cereals", "unit": "Quintal"},
    {"name": "Rice", "category": "Cereals", "unit": "Quintal"},
    {"name": "Potato", "category": "Vegetables", "unit": "Quintal"},
]

MARKETS = [
    {"name": "Azadpur", "state": "Delhi", "district": "North Delhi"},
    {"name": "Mumbai (Dadar)", "state": "Maharashtra", "district": "Mumbai"},
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

        # Seed 14 days of prices for all commodities in Azadpur and Mumbai
        start_date = datetime.utcnow().date() - timedelta(days=14)
        prices = []
        for day in range(14):
            date = start_date + timedelta(days=day)
            for market_name in ["Azadpur", "Mumbai (Dadar)"]:
                market_id = market_ids[market_name]
                for commodity in COMMODITIES:
                    commodity_id = commodity_ids[commodity["name"]]
                    base_price = 2500.0 + (commodity_id * 120)
                    # simple sinusoidal variation
                    modal = base_price * (1 + (0.05 * ((day % 7) - 3) / 3))
                    prices.append({
                        "commodity_id": commodity_id,
                        "market_id": market_id,
                        "date": date,
                        "price": round(modal, 2),
                        "min_price": round(modal * 0.9, 2),
                        "max_price": round(modal * 1.1, 2),
                        "modal_price": round(modal, 2),
                        "arrival": round(1000 + 50 * day, 2),
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
