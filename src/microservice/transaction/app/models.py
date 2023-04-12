from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


transaction_type = Enum('transfer', 'deposit', 'withdraw', name='transaction_type')

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    account_number = Column(String(255))
    amount = Column(Float, default=0)
    transaction_type = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    transfer = relationship("Transfer", back_populates="transaction", uselist=False)
    
class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), primary_key=True)
    transaction = relationship("Transaction", back_populates="transfer", uselist=False)
    destination_account_number = Column(String(255))