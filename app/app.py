"""Main application entry point."""
from fastapi import FastAPI
from app.api.v1.api_router import api_router

app = FastAPI(
    title="Inventory Management API",
    description="A comprehensive inventory management system with AI chatbot integration",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1", tags=["api"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Inventory Management API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}