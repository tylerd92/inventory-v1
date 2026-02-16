from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
from app.utils.current_datetime import utcnow

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
