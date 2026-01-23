"""Tests for commodity repository."""

import pytest
from sqlalchemy.orm import Session

from app.database.repositories import CommodityRepository
from app.database.models import Commodity


class TestCommodityRepository:
    """Test CommodityRepository."""
    
    @pytest.mark.asyncio
    async def test_create_commodity(self, test_async_db_session, sample_commodity_data):
        """Test creating a commodity."""
        repo = CommodityRepository(test_async_db_session)
        
        commodity = await repo.create(**sample_commodity_data)
        
        assert commodity.id is not None
        assert commodity.name == sample_commodity_data["name"]
        assert commodity.category == sample_commodity_data["category"]
    
    @pytest.mark.asyncio
    async def test_get_by_name(self, test_async_db_session, sample_commodity_data):
        """Test getting commodity by name."""
        repo = CommodityRepository(test_async_db_session)
        
        # Create commodity
        await repo.create(**sample_commodity_data)
        await test_async_db_session.commit()
        
        # Retrieve by name
        commodity = await repo.get_by_name(sample_commodity_data["name"])
        
        assert commodity is not None
        assert commodity.name == sample_commodity_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_by_category(self, test_async_db_session):
        """Test getting commodities by category."""
        repo = CommodityRepository(test_async_db_session)
        
        # Create multiple commodities
        await repo.create(name="Wheat", category="Cereals", unit="Quintal")
        await repo.create(name="Rice", category="Cereals", unit="Quintal")
        await repo.create(name="Potato", category="Vegetables", unit="Quintal")
        await test_async_db_session.commit()
        
        # Get by category
        cereals = await repo.get_by_category("Cereals")
        
        assert len(cereals) == 2
        assert all(c.category == "Cereals" for c in cereals)
    
    @pytest.mark.asyncio
    async def test_search_commodities(self, test_async_db_session):
        """Test commodity search."""
        repo = CommodityRepository(test_async_db_session)
        
        # Create commodities
        await repo.create(name="Wheat", category="Cereals", unit="Quintal")
        await repo.create(name="Rice", category="Cereals", unit="Quintal")
        await test_async_db_session.commit()
        
        # Search
        results = await repo.search("wheat")
        
        assert len(results) >= 1
        assert any("wheat" in c.name.lower() for c in results)
