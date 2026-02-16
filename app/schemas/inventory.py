from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .product import ProductResponse

class InventoryBase(BaseModel):
    quantity: int
    location: str
    product_id: int

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    location: Optional[str] = None

class InventoryResponse(InventoryBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Schema with product information included
class InventoryWithProduct(InventoryResponse):
    product: 'ProductResponse'