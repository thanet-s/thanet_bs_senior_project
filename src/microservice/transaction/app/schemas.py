from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class Account(BaseModel):
    user_id: UUID
    account_number: str
    account_balance: float
    created_at: datetime

class Transfer(BaseModel):
    destination_account_number: str
    
    class Config:
        orm_mode = True

class Transaction(BaseModel):
    id: UUID
    account_number: str
    amount: float
    transaction_type: str
    created_at: datetime
    transfer: Transfer | None
    
    class Config:
        orm_mode = True

class DepositRequest(BaseModel):
    account_number: str
    amount: float

class TransferRequest(BaseModel):
    fromacc: str
    toacc: str
    amount: float