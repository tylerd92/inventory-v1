from sqlalchemy import Column, Integer, String, DateTime
from app.utils.current_datetime import utcnow
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True)
    sku = Column(String(100), unique=True, index=True)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
