from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse, InventoryWithProduct
from app.services import inventory_service
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=InventoryResponse)
def create_inventory_item(inventory: InventoryCreate, db: Session = Depends(get_db)):
    # Check if the product exists before creating inventory item
    if not inventory_service.product_exists(db=db, product_id=inventory.product_id):
        raise HTTPException(status_code=400, detail="Product with the given ID does not exist")

    """Create a new inventory item."""
    return inventory_service.create_inventory_item(db=db, inventory=inventory)

@router.get("/", response_model=List[InventoryResponse])
def get_inventory_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    location: Optional[str] = Query(None, description="Filter by location"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    include_product: bool = Query(False, description="Include product details in response"),
    db: Session = Depends(get_db)
):
    """Get all inventory items with optional filtering and pagination."""
    # Handle filtering by location
    if location:
        items = inventory_service.get_inventory_by_location(db=db, location=location, skip=skip, limit=limit)
        return items
    
    # Handle filtering by product ID
    if product_id:
        items = inventory_service.get_inventory_by_product(db=db, product_id=product_id)
        return items[skip:skip + limit]
    
    # Get all items with optional product details
    return inventory_service.get_inventory_items(db=db, skip=skip, limit=limit, include_product=include_product)

@router.get("/low-stock", response_model=List[InventoryWithProduct])
def get_low_stock_items(
    threshold: int = Query(10, ge=0, description="Stock level threshold"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """Get inventory items with stock below the specified threshold."""
    return inventory_service.get_low_stock_items(db=db, threshold=threshold, skip=skip, limit=limit)

@router.get("/{inventory_id}", response_model=InventoryWithProduct)
def get_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    """Get an inventory item by ID with product details."""
    inventory = inventory_service.get_inventory_item_with_product(db=db, inventory_id=inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory

@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory_item(inventory_id: int, inventory_update: InventoryUpdate, db: Session = Depends(get_db)):
    """Update an inventory item by ID."""
    inventory = inventory_service.update_inventory_item(db=db, inventory_id=inventory_id, inventory_update=inventory_update)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory

@router.patch("/{inventory_id}/adjust", response_model=InventoryResponse)
def adjust_inventory_quantity(
    inventory_id: int, 
    quantity_change: int = Query(..., description="Quantity to add (positive) or subtract (negative)"),
    reason: Optional[str] = Query(None, description="Reason for the adjustment"),
    performed_by: Optional[int] = Query(None, description="User ID who performed the adjustment"),
    create_transaction: bool = Query(True, description="Whether to create a transaction record"),
    db: Session = Depends(get_db)
):
    """Adjust inventory quantity by a specified amount."""
    inventory = inventory_service.adjust_inventory_quantity(
        db=db, 
        inventory_id=inventory_id, 
        quantity_change=quantity_change,
        reason=reason,
        performed_by=performed_by,
        create_transaction=create_transaction
    )
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory

@router.delete("/{inventory_id}")
def delete_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    """Delete an inventory item by ID."""
    success = inventory_service.delete_inventory_item(db=db, inventory_id=inventory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"message": "Inventory item deleted successfully"}

@router.put("/{inventory_id}/set-quantity", response_model=InventoryResponse)
def set_inventory_quantity(
    inventory_id: int,
    new_quantity: int = Query(..., ge=0, description="New quantity to set"),
    reason: str = Query(..., description="Reason for the quantity change"),
    performed_by: Optional[int] = Query(None, description="User ID who performed the change"),
    db: Session = Depends(get_db)
):
    """Set inventory quantity to a specific value and create transaction record."""
    inventory = inventory_service.update_inventory_with_transaction(
        db=db,
        inventory_id=inventory_id,
        new_quantity=new_quantity,
        reason=reason,
        performed_by=performed_by
    )
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory
