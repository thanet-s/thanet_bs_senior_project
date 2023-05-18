from datetime import date
from pydantic import BaseModel, EmailStr

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