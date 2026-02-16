from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.inventory_transaction import (
    InventoryTransactionCreate, 
    InventoryTransactionUpdate, 
    InventoryTransactionResponse, 
    InventoryTransactionWithDetails
)
from app.services import inventory_transaction_service
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=InventoryTransactionResponse)
def create_transaction(transaction: InventoryTransactionCreate, db: Session = Depends(get_db)):
    """Create a new inventory transaction record."""
    return inventory_transaction_service.create_transaction(db=db, transaction=transaction)

@router.get("/", response_model=List[InventoryTransactionResponse])
def get_transactions(
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of transactions to return"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    reason: Optional[str] = Query(None, description="Filter by reason (partial match)"),
    db: Session = Depends(get_db)
):
    """Get inventory transactions with optional filtering and pagination."""
    # Filter by product
    if product_id is not None:
        return inventory_transaction_service.get_transactions_by_product(
            db=db, product_id=product_id, skip=skip, limit=limit
        )
    
    # Filter by user
    if user_id is not None:
        return inventory_transaction_service.get_transactions_by_user(
            db=db, user_id=user_id, skip=skip, limit=limit
        )
    
    # Filter by reason
    if reason is not None:
        return inventory_transaction_service.get_transactions_by_reason(
            db=db, reason=reason, skip=skip, limit=limit
        )
    
    # Get all transactions
    return inventory_transaction_service.get_transactions(db=db, skip=skip, limit=limit)

@router.get("/summary/{product_id}")
def get_product_transaction_summary(product_id: int, db: Session = Depends(get_db)):
    """Get transaction summary for a specific product."""
    return inventory_transaction_service.get_product_transaction_summary(db=db, product_id=product_id)

@router.get("/{transaction_id}", response_model=InventoryTransactionWithDetails)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get a transaction by ID with product and user details."""
    transaction = inventory_transaction_service.get_transaction_with_details(db=db, transaction_id=transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/{transaction_id}", response_model=InventoryTransactionResponse)
def update_transaction(
    transaction_id: int, 
    transaction_update: InventoryTransactionUpdate, 
    db: Session = Depends(get_db)
):
    """Update a transaction (limited fields for audit integrity)."""
    transaction = inventory_transaction_service.update_transaction(
        db=db, transaction_id=transaction_id, transaction_update=transaction_update
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Delete a transaction (use sparingly - breaks audit trail)."""
    success = inventory_transaction_service.delete_transaction(db=db, transaction_id=transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully", "warning": "Audit trail integrity may be compromised"}