from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProductBase(BaseModel):
    name: str
    quantity: int
    category: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
