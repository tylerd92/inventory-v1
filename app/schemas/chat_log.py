from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .user import UserResponse

class ChatLogBase(BaseModel):
    user_id: Optional[int] = None
    question: str
    response: str

class ChatLogCreate(ChatLogBase):
    pass

class ChatLogUpdate(BaseModel):
    question: Optional[str] = None
    response: Optional[str] = None

class ChatLogResponse(ChatLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Schema with user information included
class ChatLogWithUser(ChatLogResponse):
    user: Optional['UserResponse'] = None