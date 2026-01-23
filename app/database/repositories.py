"""Repository pattern for data access."""

from datetime import datetime, timedelta
from typing import Any, List, Optional

from loguru import logger
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import get_current_timestamp
from app.database.models import (
    Commodity,
    Market,
    MarketPrice,
    Alert,
    Inventory,
    PredictionMetrics,
    Prediction,
)


class BaseRepository:
    """Base repository with common operations."""

    def __init__(self, db: AsyncSession, model):
        self.db = db
        self.model = model

    async def create(self, **kwargs) -> Any:
        """Create and save a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        return instance

    async def get_by_id(self, id: int) -> Optional[Any]:
        """Get record by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all records with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, id: int, **kwargs) -> Optional[Any]:
        """Update a record."""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.db.flush()
        return instance

    async def delete(self, id: int) -> bool:
        """Delete a record."""
        instance = await self.get_by_id(id)
        if instance:
            await self.db.delete(instance)
            await self.db.flush()
            return True
        return False

    async def count(self) -> int:
        """Count total records."""
        query = select(self.model)
        result = await self.db.execute(query)
        return len(result.scalars().all())


class CommodityRepository(BaseRepository):
    """Repository for Commodity operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Commodity)

    async def get_by_name(self, name: str) -> Optional[Commodity]:
        """Get commodity by name."""
        query = select(Commodity).where(Commodity.name.ilike(name))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_category(self, category: str) -> List[Commodity]:
        """Get commodities by category."""
        query = select(Commodity).where(Commodity.category.ilike(category))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search(self, query_str: str) -> List[Commodity]:
        """Search commodities by name or category."""
        query = select(Commodity).where(
            or_(
                Commodity.name.ilike(f"%{query_str}%"),
                Commodity.category.ilike(f"%{query_str}%"),
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class MarketRepository(BaseRepository):
    """Repository for Market operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Market)

    async def get_by_name(self, name: str) -> Optional[Market]:
        """Get market by name."""
        query = select(Market).where(Market.name.ilike(name))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_state(self, state: str) -> List[Market]:
        """Get markets by state."""
        query = select(Market).where(Market.state.ilike(state))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_location(self, state: str, district: Optional[str] = None) -> List[Market]:
        """Get markets by location."""
        conditions = [Market.state.ilike(state)]
        if district:
            conditions.append(Market.district.ilike(district))
        
        query = select(Market).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search(self, query_str: str) -> List[Market]:
        """Search markets by name or state."""
        query = select(Market).where(
            or_(
                Market.name.ilike(f"%{query_str}%"),
                Market.state.ilike(f"%{query_str}%"),
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class MarketPriceRepository(BaseRepository):
    """Repository for MarketPrice operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, MarketPrice)

    async def get_by_commodity_market_date(
        self,
        commodity_id: int,
        market_id: int,
        date: str,
    ) -> Optional[MarketPrice]:
        """Get price for specific commodity, market, and date."""
        query = select(MarketPrice).where(
            and_(
                MarketPrice.commodity_id == commodity_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date == datetime.strptime(date, "%Y-%m-%d").date(),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_latest_price(self, commodity_id: int, market_id: int) -> Optional[MarketPrice]:
        """Get latest price for commodity and market."""
        query = (
            select(MarketPrice)
            .where(
                and_(
                    MarketPrice.commodity_id == commodity_id,
                    MarketPrice.market_id == market_id,
                )
            )
            .order_by(desc(MarketPrice.date))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_price_history(
        self,
        commodity_id: int,
        market_id: int,
        days: int = 30,
    ) -> List[MarketPrice]:
        """Get price history for commodity and market."""
        start_date = (get_current_timestamp() - timedelta(days=days)).date()
        
        query = (
            select(MarketPrice)
            .where(
                and_(
                    MarketPrice.commodity_id == commodity_id,
                    MarketPrice.market_id == market_id,
                    MarketPrice.date >= start_date,
                )
            )
            .order_by(MarketPrice.date)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_market_prices(self, market_id: int, date: Optional[str] = None) -> List[MarketPrice]:
        """Get all prices for a market on a specific date."""
        query = select(MarketPrice).where(MarketPrice.market_id == market_id)
        
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.where(MarketPrice.date == target_date)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def bulk_create(self, prices: List[dict]) -> List[MarketPrice]:
        """Create multiple price records."""
        instances = [MarketPrice(**price) for price in prices]
        self.db.add_all(instances)
        await self.db.flush()
        return instances


class AlertRepository(BaseRepository):
    """Repository for Alert operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Alert)

    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        query = select(Alert).where(Alert.status == "ACTIVE").order_by(desc(Alert.priority))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_alerts_by_commodity(self, commodity_id: int) -> List[Alert]:
        """Get alerts for a commodity."""
        query = select(Alert).where(Alert.commodity_id == commodity_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_alerts_by_status(self, status: str) -> List[Alert]:
        """Get alerts by status."""
        query = select(Alert).where(Alert.status == status)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get alerts from last N hours."""
        cutoff_time = get_current_timestamp() - timedelta(hours=hours)
        
        query = select(Alert).where(Alert.triggered_at >= cutoff_time).order_by(desc(Alert.triggered_at))
        result = await self.db.execute(query)
        return result.scalars().all()


class InventoryRepository(BaseRepository):
    """Repository for Inventory operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Inventory)

    async def get_by_commodity_market(self, commodity_id: int, market_id: int) -> Optional[Inventory]:
        """Get inventory for specific commodity and market."""
        query = select(Inventory).where(
            and_(
                Inventory.commodity_id == commodity_id,
                Inventory.market_id == market_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_low_stock_items(self, threshold_percent: float = 0.2) -> List[Inventory]:
        """Get items below threshold percentage of optimal stock."""
        query = select(Inventory).where(
            Inventory.current_stock < (Inventory.optimal_stock * threshold_percent)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_commodity(self, commodity_id: int) -> List[Inventory]:
        """Get inventory across all markets for a commodity."""
        query = select(Inventory).where(Inventory.commodity_id == commodity_id)
        result = await self.db.execute(query)
        return result.scalars().all()


class PredictionMetricsRepository(BaseRepository):
    """Repository for PredictionMetrics operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, PredictionMetrics)

    async def get_latest_metrics(self, model_name: str) -> Optional[PredictionMetrics]:
        """Get latest metrics for a model."""
        query = (
            select(PredictionMetrics)
            .where(PredictionMetrics.model_name == model_name)
            .order_by(desc(PredictionMetrics.updated_at))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_model(self, model_name: str) -> List[PredictionMetrics]:
        """Get all metrics for a model."""
        query = select(PredictionMetrics).where(PredictionMetrics.model_name == model_name)
        result = await self.db.execute(query)
        return result.scalars().all()


class PredictionRepository(BaseRepository):
    """Repository for Prediction operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Prediction)

    async def get_by_date_range(
        self,
        commodity_id: int,
        market_id: int,
        start_date: str,
        end_date: str,
    ) -> List[Prediction]:
        """Get predictions for a date range."""
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        query = select(Prediction).where(
            and_(
                Prediction.commodity_id == commodity_id,
                Prediction.market_id == market_id,
                Prediction.prediction_date >= start,
                Prediction.prediction_date <= end,
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_accuracy_for_period(self, days: int = 30) -> float:
        """Calculate average prediction accuracy for recent period."""
        cutoff_date = (get_current_timestamp() - timedelta(days=days)).date()
        
        query = select(Prediction).where(
            and_(
                Prediction.prediction_date >= cutoff_date,
                Prediction.actual_price.isnot(None),
            )
        )
        result = await self.db.execute(query)
        predictions = result.scalars().all()
        
        if not predictions:
            return 0.0
        
        return sum(p.accuracy for p in predictions if p.accuracy) / len(predictions)
