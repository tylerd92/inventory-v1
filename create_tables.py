"""Database initialization script to create all tables."""
from app.db.base import Base
from app.db.session import engine
from app.models.product import Product  # Import all models

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    create_tables()