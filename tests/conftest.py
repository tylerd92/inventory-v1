"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Set test database URL before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.db.base import Base
from app.db.session import get_db


# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with a test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Import app here to avoid database connection issues
    from app.app import app
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "sku": "TEST-001",
        "category": "Electronics"
    }


@pytest.fixture
def sample_products_data():
    """Multiple sample products for testing."""
    return [
        {"name": "Laptop", "sku": "LAP-001", "category": "Electronics"},
        {"name": "Chair", "sku": "CHR-001", "category": "Furniture"},
        {"name": "Phone", "sku": "PHN-001", "category": "Electronics"},
        {"name": "Desk", "sku": "DSK-001", "category": "Furniture"},
    ]