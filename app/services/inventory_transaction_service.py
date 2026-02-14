from sqlalchemy.orm import Session, joinedload
from app.models.inventory_transaction import InventoryTransaction
from app.schemas.inventory_transaction import InventoryTransactionCreate, InventoryTransactionUpdate
from typing import List, Optional

def create_transaction(db: Session, transaction: InventoryTransactionCreate) -> InventoryTransaction:
    """Create a new inventory transaction record."""
    db_transaction = InventoryTransaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction(db: Session, transaction_id: int) -> Optional[InventoryTransaction]:
    """Get a transaction by ID."""
    return db.query(InventoryTransaction).filter(InventoryTransaction.id == transaction_id).first()

def get_transaction_with_details(db: Session, transaction_id: int) -> Optional[InventoryTransaction]:
    """Get a transaction by ID with product and user details."""
    return db.query(InventoryTransaction).options(
        joinedload(InventoryTransaction.product),
        joinedload(InventoryTransaction.user)
    ).filter(InventoryTransaction.id == transaction_id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[InventoryTransaction]:
    """Get all transactions with pagination, ordered by most recent first."""
    return db.query(InventoryTransaction).order_by(
        InventoryTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()

def get_transactions_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[InventoryTransaction]:
    """Get all transactions for a specific product."""
    return db.query(InventoryTransaction).filter(
        InventoryTransaction.product_id == product_id
    ).order_by(
        InventoryTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()

def get_transactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[InventoryTransaction]:
    """Get all transactions performed by a specific user."""
    return db.query(InventoryTransaction).filter(
        InventoryTransaction.performed_by == user_id
    ).order_by(
        InventoryTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()

def get_transactions_by_reason(db: Session, reason: str, skip: int = 0, limit: int = 100) -> List[InventoryTransaction]:
    """Get transactions filtered by reason (partial match)."""
    return db.query(InventoryTransaction).filter(
        InventoryTransaction.reason.ilike(f"%{reason}%")
    ).order_by(
        InventoryTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()

def update_transaction(db: Session, transaction_id: int, transaction_update: InventoryTransactionUpdate) -> Optional[InventoryTransaction]:
    """Update a transaction (limited fields for audit integrity)."""
    db_transaction = db.query(InventoryTransaction).filter(InventoryTransaction.id == transaction_id).first()
    if db_transaction:
        # Only allow updating reason and performed_by for audit trail corrections
        # change_amount should generally not be modified once recorded
        update_data = transaction_update.model_dump(exclude_unset=True)
        allowed_fields = {'reason', 'performed_by'}
        
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(db_transaction, field, value)
        
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int) -> bool:
    """Delete a transaction (use sparingly - breaks audit trail)."""
    db_transaction = db.query(InventoryTransaction).filter(InventoryTransaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return True
    return False

def get_product_transaction_summary(db: Session, product_id: int) -> dict:
    """Get transaction summary for a product (total in/out, transaction count)."""
    transactions = db.query(InventoryTransaction).filter(InventoryTransaction.product_id == product_id).all()
    
    total_in = sum(t.change_amount for t in transactions if t.change_amount > 0)
    total_out = sum(abs(t.change_amount) for t in transactions if t.change_amount < 0)
    transaction_count = len(transactions)
    
    return {
        "product_id": product_id,
        "total_in": total_in,
        "total_out": total_out,
        "net_change": total_in - total_out,
        "transaction_count": transaction_count
    }