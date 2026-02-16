from .product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithInventory,
)
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
)
from .inventory import (
    InventoryBase,
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    InventoryWithProduct,
)
from .inventory_transaction import (
    InventoryTransactionBase,
    InventoryTransactionCreate,
    InventoryTransactionUpdate,
    InventoryTransactionResponse,
    InventoryTransactionWithDetails,
)
from .chat_log import (
    ChatLogBase,
    ChatLogCreate,
    ChatLogUpdate,
    ChatLogResponse,
    ChatLogWithUser,
)

# Resolve forward references after all imports are complete
# This is necessary for schemas that use forward references (e.g., 'ProductResponse')
InventoryWithProduct.model_rebuild()
ProductWithInventory.model_rebuild()
InventoryTransactionWithDetails.model_rebuild()
ChatLogWithUser.model_rebuild()

__all__ = [
    # Product schemas
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductWithInventory",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # Inventory schemas
    "InventoryBase",
    "InventoryCreate",
    "InventoryUpdate",
    "InventoryResponse",
    "InventoryWithProduct",
    # Inventory Transaction schemas
    "InventoryTransactionBase",
    "InventoryTransactionCreate",
    "InventoryTransactionUpdate",
    "InventoryTransactionResponse",
    "InventoryTransactionWithDetails",
    # Chat Log schemas
    "ChatLogBase",
    "ChatLogCreate",
    "ChatLogUpdate",
    "ChatLogResponse",
    "ChatLogWithUser",
]
