from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.utils.current_datetime import utcnow

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    change_amount = Column(Integer, nullable=False)
    reason = Column(String(100))
    performed_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    product = relationship("Product")
    user = relationship("User")
