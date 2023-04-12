from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime, Float
from database import Base


class Account(Base):
    __tablename__ = "accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True))
    account_number = Column(String(255), unique=True, index=True)
    account_balance = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
