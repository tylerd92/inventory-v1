from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base
from app.utils.current_datetime import utcnow

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(50), default="user")

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
