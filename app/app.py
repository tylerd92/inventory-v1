"""Main application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.api_router import api_router
from app.db.base import Base
from app.db.session import engine

# Import all models to register them with SQLAlchemy
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.chat_log import ChatLog
from app.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - runs on startup and shutdown."""
    # Startup
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    yield
    
    # Shutdown (if needed)
    print("Application shutting down...")

app = FastAPI(
    title="Inventory Management API",
    description="A comprehensive inventory management system with AI chatbot integration",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1", tags=["api"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Inventory Management API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}