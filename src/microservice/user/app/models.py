from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime, Date
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True
    )
    email = Column(String(255), unique=True, index=True)
    fullname = Column(String(255))
    phone_no = Column(String(10))
    birthday = Column(DateTime)
    password = Column(String(255))
    created_at = Column(Date, server_default=func.now())
