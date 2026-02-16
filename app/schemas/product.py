from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .inventory import InventoryResponse

class ProductBase(BaseModel):
    name: str
    sku: str
    category: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Schema with inventory items included
class ProductWithInventory(ProductResponse):
    inventory_items: list['InventoryResponse'] = []
