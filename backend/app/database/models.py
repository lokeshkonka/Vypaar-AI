"""SQLAlchemy ORM models for agricultural market data."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    Index,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Commodity(Base):
    """Commodity model."""

    __tablename__ = "commodities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)
    unit = Column(String(50), default="Quintal")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    market_prices = relationship("MarketPrice", back_populates="commodity", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="commodity", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="commodity", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Commodity(id={self.id}, name={self.name})>"


class Market(Base):
    """Market model."""

    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    state = Column(String(100), index=True)
    district = Column(String(100), index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    market_prices = relationship("MarketPrice", back_populates="market", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="market", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="market", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("name", "state", name="uq_market_state"),
    )

    def __repr__(self):
        return f"<Market(id={self.id}, name={self.name}, state={self.state})>"


class MarketPrice(Base):
    """Market price history model."""

    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    modal_price = Column(Float, nullable=True)  # Most common/average price
    price = Column(Float, nullable=False)  # Current/average price
    arrival = Column(Float, nullable=True)  # Quantity arrived
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    commodity = relationship("Commodity", back_populates="market_prices")
    market = relationship("Market", back_populates="market_prices")

    __table_args__ = (
        Index("ix_market_price_date", "date"),
        Index("ix_market_price_commodity_market_date", "commodity_id", "market_id", "date"),
        UniqueConstraint("commodity_id", "market_id", "date", name="uq_market_price"),
    )

    def __repr__(self):
        return f"<MarketPrice(id={self.id}, commodity_id={self.commodity_id}, market_id={self.market_id}, date={self.date})>"


class Alert(Base):
    """Alert model for price and inventory alerts."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=True)
    alert_type = Column(String(50), nullable=False, index=True)  # PRICE_THRESHOLD, INVENTORY_LOW, etc.
    priority = Column(String(20), default="MEDIUM", index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, RESOLVED, DISMISSED
    conditions = Column(JSON, nullable=True)  # Store conditions as JSON
    notification_channels = Column(JSON, default=lambda: ["in_app"], nullable=False)  # Store as JSON array
    message = Column(Text, nullable=True)
    triggered_at = Column(DateTime, nullable=True, index=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    commodity = relationship("Commodity", back_populates="alerts")
    market = relationship("Market", back_populates="alerts")

    __table_args__ = (
        Index("ix_alert_status_priority", "status", "priority"),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, alert_type={self.alert_type}, status={self.status})>"


class Inventory(Base):
    """Inventory model for commodity stock levels."""

    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    current_stock = Column(Float, default=0.0, nullable=False)
    optimal_stock = Column(Float, nullable=True)
    min_stock = Column(Float, nullable=True)
    max_stock = Column(Float, nullable=True)
    reorder_point = Column(Float, nullable=True)
    last_restocked_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    commodity = relationship("Commodity", back_populates="inventory")
    market = relationship("Market", back_populates="inventory")

    __table_args__ = (
        UniqueConstraint("commodity_id", "market_id", name="uq_inventory"),
    )

    def __repr__(self):
        return f"<Inventory(id={self.id}, commodity_id={self.commodity_id}, market_id={self.market_id})>"


class PredictionMetrics(Base):
    """Model for storing prediction metrics and model performance."""

    __tablename__ = "prediction_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    accuracy = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    training_samples = Column(Integer, nullable=True)
    validation_samples = Column(Integer, nullable=True)
    test_samples = Column(Integer, nullable=True)
    training_duration_minutes = Column(Float, nullable=True)
    last_trained_at = Column(DateTime, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_prediction_metrics_model", "model_name", "model_version"),
    )

    def __repr__(self):
        return f"<PredictionMetrics(id={self.id}, model_name={self.model_name}, version={self.model_version})>"


class Prediction(Base):
    """Model for storing historical predictions and their accuracy."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    prediction_date = Column(Date, nullable=False, index=True)
    predicted_price = Column(Float, nullable=False)
    actual_price = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)
    error = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_prediction_date_commodity_market", "prediction_date", "commodity_id", "market_id"),
    )

    def __repr__(self):
        return f"<Prediction(id={self.id}, commodity_id={self.commodity_id}, market_id={self.market_id})>"
