from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: EmailStr
    fullname: str
    phone_no: str
    birthday: date
    
    class Config:
        orm_mode = True

class UserCreate(User):
    password: str

class AccountResponse(BaseModel):
    account_number: str
    account_balance: float
    created_at: datetime
    
    class Config:
        orm_mode = True

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