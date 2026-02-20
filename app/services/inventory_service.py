from sqlalchemy.orm import Session, joinedload
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.schemas.inventory_transaction import InventoryTransactionCreate
from app.services import product_service
from typing import List, Optional

# Import transaction service (avoid circular imports by importing within functions when needed)

def create_inventory_item(db: Session, inventory: InventoryCreate) -> Inventory:
    """Create a new inventory item in the database."""
    db_inventory = Inventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

def get_inventory_item(db: Session, inventory_id: int) -> Optional[Inventory]:
    """Get an inventory item by ID."""
    return db.query(Inventory).filter(Inventory.id == inventory_id).first()

def get_inventory_item_with_product(db: Session, inventory_id: int) -> Optional[Inventory]:
    """Get an inventory item by ID with product details."""
    return db.query(Inventory).options(joinedload(Inventory.product)).filter(Inventory.id == inventory_id).first()

def get_inventory_items(db: Session, skip: int = 0, limit: int = 100, include_product: bool = False) -> List[Inventory]:
    """Get all inventory items with pagination."""
    query = db.query(Inventory)
    if include_product:
        query = query.options(joinedload(Inventory.product))
    return query.offset(skip).limit(limit).all()

def get_inventory_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[Inventory]:
    """Get all inventory items for a specific product."""
    return db.query(Inventory).filter(Inventory.product_id == product_id).offset(skip).limit(limit).all()

def get_inventory_by_location(db: Session, location: str, skip: int = 0, limit: int = 100) -> List[Inventory]:
    """Get inventory items by location."""
    return db.query(Inventory).filter(Inventory.location.ilike(f"%{location}%")).offset(skip).limit(limit).all()

def update_inventory_item(db: Session, inventory_id: int, inventory_update: InventoryUpdate) -> Optional[Inventory]:
    """Update an existing inventory item."""
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory:
        update_data = inventory_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_inventory, field, value)
        db.commit()
        db.refresh(db_inventory)
    return db_inventory

def delete_inventory_item(db: Session, inventory_id: int) -> bool:
    """Delete an inventory item by ID."""
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory:
        db.delete(db_inventory)
        db.commit()
        return True
    return False

def adjust_inventory_quantity(db: Session, inventory_id: int, quantity_change: int, reason: Optional[str] = None, performed_by: Optional[int] = None, create_transaction: bool = True) -> Optional[Inventory]:
    """Adjust inventory quantity by a specified amount (positive or negative)."""
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory:
        old_quantity = db_inventory.quantity
        db_inventory.quantity += quantity_change
        # Ensure quantity doesn't go negative
        if db_inventory.quantity < 0:
            db_inventory.quantity = 0
        
        # Calculate the actual change (may be different if quantity went negative)
        actual_change = db_inventory.quantity - old_quantity
        
        db.commit()
        db.refresh(db_inventory)
        
        # Create transaction record if requested
        if create_transaction and actual_change != 0:
            from app.services import inventory_transaction_service
            transaction_data = InventoryTransactionCreate(
                product_id=db_inventory.product_id,
                change_amount=actual_change,
                reason=reason or "Quantity adjustment",
                performed_by=performed_by
            )
            inventory_transaction_service.create_transaction(db=db, transaction=transaction_data)
    
    return db_inventory

def get_low_stock_items(db: Session, threshold: int = 10, skip: int = 0, limit: int = 100) -> List[Inventory]:
    """Get inventory items with quantity at or below the specified threshold."""
    return db.query(Inventory).options(joinedload(Inventory.product)).filter(Inventory.quantity <= threshold).offset(skip).limit(limit).all()

def update_inventory_with_transaction(db: Session, inventory_id: int, new_quantity: int, reason: str, performed_by: Optional[int] = None) -> Optional[Inventory]:
    """Update inventory quantity and create a transaction record."""
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory:
        old_quantity = db_inventory.quantity
        quantity_change = new_quantity - old_quantity
        
        # Update inventory
        db_inventory.quantity = new_quantity
        db.commit()
        db.refresh(db_inventory)
        
        # Create transaction record
        if quantity_change != 0:
            from app.services import inventory_transaction_service
            transaction_data = InventoryTransactionCreate(
                product_id=db_inventory.product_id,
                change_amount=quantity_change,
                reason=reason,
                performed_by=performed_by
            )
            inventory_transaction_service.create_transaction(db=db, transaction=transaction_data)
    
    return db_inventory

def product_exists(db: Session, product_id: int) -> bool:
    """Check if a product exists in the database."""
    return product_service.get_product(db=db, product_id=product_id) is not None
