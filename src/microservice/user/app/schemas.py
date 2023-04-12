from datetime import date
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: str
    fullname: str
    phone_no: str
    birthday: date
    
    class Config:
        orm_mode = True

class UserCreate(User):
    password: str