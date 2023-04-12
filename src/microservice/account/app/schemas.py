from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AccountResponse(BaseModel):
    user_id: UUID
    account_number: str
    account_balance: float
    created_at: datetime
    
    class Config:
        orm_mode = True

class ChecAccountExistRequest(BaseModel):
    account_number: str

class CheckOwnAccountRequest(ChecAccountExistRequest):
    user_id: UUID

class UpdateAccountBalanceRequest(ChecAccountExistRequest):
    account_balance: float