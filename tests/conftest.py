"""Pytest configuration and shared fixtures."""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database.models import Base
from app.database.connection import get_async_session
from app.config import settings


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_agritech.db"
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test_agritech.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    # Clean up test database file
    Path("test_agritech.db").unlink(missing_ok=True)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
async def test_async_db_engine():
    """Create test async database engine."""
    engine = create_async_engine(TEST_ASYNC_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    # Clean up test database file
    Path("test_agritech.db").unlink(missing_ok=True)


@pytest.fixture(scope="function")
async def test_async_db_session(test_async_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test async database session."""
    async_session_factory = async_sessionmaker(
        test_async_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope="function")
def test_client(test_async_db_session):
    """Create test client with dependency overrides."""
    async def override_get_db():
        yield test_async_db_session
    
    app.dependency_overrides[get_async_session] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_commodity_data():
    """Sample commodity data for tests."""
    return {
        "name": "Test Wheat",
        "category": "Cereals",
        "unit": "Quintal",
    }


@pytest.fixture(scope="function")
def sample_market_data():
    """Sample market data for tests."""
    return {
        "name": "Test Market",
        "state": "Test State",
        "district": "Test District",
    }


@pytest.fixture(scope="function")
def sample_price_data():
    """Sample price data for tests."""
    return {
        "commodity_id": 1,
        "market_id": 1,
        "date": "2026-01-15",
        "price": 2500.0,
        "min_price": 2250.0,
        "max_price": 2750.0,
        "modal_price": 2500.0,
        "arrival": 1000.0,
    }


@pytest.fixture(scope="function")
def sample_inventory_data():
    """Sample inventory data for tests."""
    return {
        "commodity_id": 1,
        "market_id": 1,
        "current_stock": 1500.0,
        "optimal_stock": 2000.0,
        "min_stock": 800.0,
        "max_stock": 3000.0,
        "reorder_point": 1200.0,
    }
