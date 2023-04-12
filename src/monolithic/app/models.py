from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime, Enum, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
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


class Account(Base):
    __tablename__ = "accounts"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        )
    )
    account_number = Column(String(255), unique=True, index=True)
    account_balance = Column(Float)
    created_at = Column(DateTime, server_default=func.now())


transaction_type = Enum(
    'transfer',
    'deposit',
    'withdraw',
    name='transaction_type'
)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True
    )
    account_number = Column(
        String(255),
        ForeignKey(
            "accounts.account_number",
            ondelete="CASCADE"
        )
    )
    amount = Column(Float, default=0)
    transaction_type = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    transfer = relationship(
        "Transfer",
        back_populates="transaction",
        uselist=False
    )


class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "transactions.id",
            ondelete="CASCADE"),
        primary_key=True
    )
    transaction = relationship(
        "Transaction",
        back_populates="transfer",
        uselist=False
    )
    destination_account_number = Column(
        String(255),
        ForeignKey(
            "accounts.account_number",
            ondelete="CASCADE"
        )
    )
