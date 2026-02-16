from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .product import ProductResponse
    from .user import UserResponse

class InventoryTransactionBase(BaseModel):
    product_id: int
    change_amount: int
    reason: Optional[str] = None
    performed_by: Optional[int] = None

class InventoryTransactionCreate(InventoryTransactionBase):
    pass

class InventoryTransactionUpdate(BaseModel):
    change_amount: Optional[int] = None
    reason: Optional[str] = None
    performed_by: Optional[int] = None

class InventoryTransactionResponse(InventoryTransactionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Schema with related object information included
class InventoryTransactionWithDetails(InventoryTransactionResponse):
    product: 'ProductResponse'
    user: Optional['UserResponse'] = None