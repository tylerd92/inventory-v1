"""Database initialization script to create all tables."""
from app.db.base import Base
from app.db.session import engine

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    create_tables()