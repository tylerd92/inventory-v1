from fastapi import APIRouter
from app.api.v1.endpoints import product, inventory, inventory_transaction, chat

api_router = APIRouter()
api_router.include_router(product.router, prefix="/products", tags=["Products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(inventory_transaction.router, prefix="/inventory-transactions", tags=["Inventory Transactions"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chatbot"])
