from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional

def create_product(db: Session, product: ProductCreate) -> Product:
    """Create a new product in the database."""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get a product by ID."""
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Get all products with pagination."""
    return db.query(Product).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    """Update an existing product."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        update_data = product_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> bool:
    """Delete a product by ID."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

def search_products(db: Session, name: Optional[str] = None, category: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Product]:
    """Search products by name or category."""
    query = db.query(Product)
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    return query.offset(skip).limit(limit).all()