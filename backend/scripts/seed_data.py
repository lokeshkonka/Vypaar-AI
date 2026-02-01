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
    # Cereals/Grains
    {"name": "Wheat", "category": "Grains", "unit": "Quintal"},
    {"name": "Rice", "category": "Grains", "unit": "Quintal"},
    {"name": "Maize", "category": "Grains", "unit": "Quintal"},
    {"name": "Bajra", "category": "Grains", "unit": "Quintal"},
    {"name": "Jowar", "category": "Grains", "unit": "Quintal"},
    # Vegetables
    {"name": "Potato", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Tomato", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Onion", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Brinjal", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Cabbage", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Cauliflower", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Carrot", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Green Chilli", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Lady Finger", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Capsicum", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Ginger", "category": "Vegetables", "unit": "Quintal"},
    {"name": "Garlic", "category": "Vegetables", "unit": "Quintal"},
    # Pulses
    {"name": "Tur (Arhar)", "category": "Pulses", "unit": "Quintal"},
    {"name": "Chana", "category": "Pulses", "unit": "Quintal"},
    {"name": "Moong Dal", "category": "Pulses", "unit": "Quintal"},
    {"name": "Urad Dal", "category": "Pulses", "unit": "Quintal"},
    # Fruits
    {"name": "Apple", "category": "Fruits", "unit": "Quintal"},
    {"name": "Banana", "category": "Fruits", "unit": "Quintal"},
    {"name": "Mango", "category": "Fruits", "unit": "Quintal"},
    {"name": "Orange", "category": "Fruits", "unit": "Quintal"},
    {"name": "Grapes", "category": "Fruits", "unit": "Quintal"},
    {"name": "Papaya", "category": "Fruits", "unit": "Quintal"},
    {"name": "Pomegranate", "category": "Fruits", "unit": "Quintal"},
    # Spices
    {"name": "Turmeric", "category": "Spices", "unit": "Quintal"},
    {"name": "Coriander", "category": "Spices", "unit": "Quintal"},
    {"name": "Cumin", "category": "Spices", "unit": "Quintal"},
    {"name": "Red Chilli", "category": "Spices", "unit": "Quintal"},
    # Oilseeds
    {"name": "Groundnut", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Mustard", "category": "Oilseeds", "unit": "Quintal"},
    {"name": "Soyabean", "category": "Oilseeds", "unit": "Quintal"},
]

MARKETS = [
    {"name": "Azadpur", "state": "Delhi", "district": "North Delhi"},
    {"name": "Mumbai (Dadar)", "state": "Maharashtra", "district": "Mumbai"},
    {"name": "Kolkata (Howrah)", "state": "West Bengal", "district": "Howrah"},
    {"name": "Chennai (Koyambedu)", "state": "Tamil Nadu", "district": "Chennai"},
    {"name": "Bangalore (Yeshwanthpur)", "state": "Karnataka", "district": "Bangalore"},
    {"name": "Hyderabad (Bowenpally)", "state": "Telangana", "district": "Hyderabad"},
    {"name": "Ahmedabad (Jamalpur)", "state": "Gujarat", "district": "Ahmedabad"},
    {"name": "Pune (Market Yard)", "state": "Maharashtra", "district": "Pune"},
    {"name": "Jaipur (Muhana)", "state": "Rajasthan", "district": "Jaipur"},
    {"name": "Lucknow (Aishbagh)", "state": "Uttar Pradesh", "district": "Lucknow"},
    {"name": "Indore (Choithram)", "state": "Madhya Pradesh", "district": "Indore"},
    {"name": "Chandigarh (Sector 26)", "state": "Punjab", "district": "Chandigarh"},
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

        # Base prices for different commodities (Rs per Quintal)
        BASE_PRICES = {
            "Wheat": 2500, "Rice": 3000, "Maize": 1800, "Bajra": 2200, "Jowar": 2100,
            "Potato": 1500, "Tomato": 2000, "Onion": 1800, "Brinjal": 2500, "Cabbage": 1200,
            "Cauliflower": 2200, "Carrot": 1800, "Green Chilli": 3500, "Lady Finger": 2800,
            "Capsicum": 4000, "Ginger": 8000, "Garlic": 12000,
            "Tur (Arhar)": 7500, "Chana": 5500, "Moong Dal": 8000, "Urad Dal": 9000,
            "Apple": 8000, "Banana": 2500, "Mango": 5000, "Orange": 3500, "Grapes": 6000,
            "Papaya": 2000, "Pomegranate": 7000,
            "Turmeric": 8000, "Coriander": 7000, "Cumin": 18000, "Red Chilli": 12000,
            "Groundnut": 5500, "Mustard": 5000, "Soyabean": 4500,
        }

        # Seed 30 days of prices for all commodities in all markets
        import random
        from datetime import timezone
        start_date = datetime.now(timezone.utc).date() - timedelta(days=30)
        prices = []
        skipped = 0
        for commodity_name, commodity_id in commodity_ids.items():
            base_price = BASE_PRICES.get(commodity_name, 2000)
            for market_name, market_id in market_ids.items():
                # Add market-based price variation
                market_factor = 1.0 + random.uniform(-0.1, 0.1)
                for day in range(30):
                    date = start_date + timedelta(days=day)
                    # Check if price already exists
                    existing = await price_repo.get_by_commodity_market_date(commodity_id, market_id, date.isoformat())
                    if existing:
                        skipped += 1
                        continue
                    # Price variation: seasonal + random
                    seasonal = 0.05 * ((day % 7) - 3) / 3
                    daily_var = random.uniform(-0.03, 0.03)
                    modal = base_price * market_factor * (1 + seasonal + daily_var)
                    prices.append({
                        "commodity_id": commodity_id,
                        "market_id": market_id,
                        "date": date,
                        "price": round(modal, 2),
                        "min_price": round(modal * 0.92, 2),
                        "max_price": round(modal * 1.08, 2),
                        "modal_price": round(modal, 2),
                        "arrival": round(500 + random.uniform(0, 1000), 2),
                    })
        if prices:
            await price_repo.bulk_create(prices)
        logger.info(f"Seeded {len(prices)} market price records (skipped {skipped} existing)")

        # Seed inventory for multiple commodities in Azadpur market
        azadpur_id = market_ids["Azadpur"]
        inventory_count = 0
        for commodity_name, commodity_id in list(commodity_ids.items())[:15]:  # Top 15 commodities
            existing_inv = await inventory_repo.get_by_commodity_market(commodity_id, azadpur_id)
            if not existing_inv:
                base_stock = random.uniform(500, 2000)
                await inventory_repo.create(
                    commodity_id=commodity_id,
                    market_id=azadpur_id,
                    current_stock=round(base_stock, 2),
                    optimal_stock=round(base_stock * 1.3, 2),
                    min_stock=round(base_stock * 0.5, 2),
                    max_stock=round(base_stock * 2.0, 2),
                    reorder_point=round(base_stock * 0.8, 2),
                )
                inventory_count += 1
        logger.info(f"Created {inventory_count} inventory records")

        # Commit
        await session.commit()
        logger.success("✅ Seeding completed")

if __name__ == "__main__":
    try:
        asyncio.run(seed())
    except Exception as e:
        logger.exception(f"Seeding failed: {e}")
        sys.exit(1)
