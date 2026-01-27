from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.current_datetime import utcnow


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    location = Column(String(150))
    product_id = Column(Integer, ForeignKey("products.id"), ondelete="CASCADE", nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    product = relationship("Product", back_populates="inventory_items")