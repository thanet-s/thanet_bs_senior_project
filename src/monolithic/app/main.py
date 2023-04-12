from uuid import UUID
import uvicorn
import random
import string
import models, schemas
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from dependencies import get_db, get_current_user_id, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import engine
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
import logging

logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(openapi_url="/api/openapi.json", docs_url="/api/docs")
api_router = APIRouter(tags=["API"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def check_own_account(account_number: str, current_user_id: UUID, db: Session) -> models.Account:
    account: models.Account = (
        db.query(models.Account)
        .filter(models.Account.account_number == account_number)
        .filter(models.Account.user_id == current_user_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@api_router.post("/signin", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user: models.User = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email")
    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@api_router.post("/signup", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    all_acc_no = [id[0] for id in db.query(models.Account.account_number).all()]
    rand_acc_no = ''.join(random.choice(string.digits) for _ in range(10))
    while rand_acc_no in all_acc_no:
        rand_acc_no = ''.join(random.choice(string.digits) for _ in range(10))
    new_user = models.User(email=user.email, fullname=user.fullname, phone_no=user.phone_no, birthday=user.birthday, password=hashed_password, created_at=datetime.utcnow())
    db.add(new_user)
    db.flush()
    new_account = models.Account(user_id=new_user.id, account_number=rand_acc_no, account_balance=0, created_at=datetime.utcnow())
    db.add(new_account)
    db.commit()
    return new_user

@api_router.get("/accounts", response_model=list[schemas.AccountResponse])
async def account_list(current_user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    accounts = db.query(models.Account).filter(models.Account.user_id == current_user_id).all()
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    return accounts

@api_router.get("/balance/{account_number}")
async def account_balance(account_number: str, current_user_id: UUID = Depends(get_current_user_id),db: Session = Depends(get_db)):
    account: models.Account = check_own_account(
        account_number=account_number,
        current_user_id=current_user_id,
        db=db
    )
    return {"balance": account.account_balance}

@api_router.get("/transactions/{account_number}", response_model=list[schemas.Transaction])
async def read_transactions(account_number: str, current_user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    account: models.Account = check_own_account(
        account_number=account_number,
        current_user_id=current_user_id,
        db=db
    )
    
    normal_subquery = (
        db.query(models.Transaction.id)
        .filter(models.Transaction.account_number == account.account_number)
        .subquery()
    )
    
    receive_transfer_subquery = (
        db.query(models.Transfer.id)
        .filter(models.Transfer.destination_account_number == account.account_number)
        .subquery()
    )
    
    stmt = (
        db.query(models.Transaction)
        .filter(
            or_(
                models.Transaction.id.in_(normal_subquery.element),
                models.Transaction.id.in_(receive_transfer_subquery.element)
            )
        )
        .order_by(
            models.Transaction.created_at.desc()
        )
    )
    transactions = stmt.all()
    # logging.info(stmt.statement)
    return transactions

@api_router.post("/deposit", response_model=schemas.Transaction)
async def deposit(deposit_request: schemas.DepositRequest, current_user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if deposit_request.amount < 1:
        raise HTTPException(status_code=400, detail="Amount can not less than 1")
    
    account: models.Account = check_own_account(
        account_number=deposit_request.account_number,
        current_user_id=current_user_id,
        db=db
    )

    account.account_balance += deposit_request.amount
    transaction = models.Transaction(
        account_number=account.account_number, amount=deposit_request.amount, transaction_type='deposit'
    )
    db.add(transaction)
    db.commit()
    return transaction

@api_router.post("/transfer", response_model=schemas.Transaction)
async def transfer(transfer: schemas.TransferRequest, current_user_id: UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if transfer.fromacc == transfer.toacc:
        raise HTTPException(status_code=400, detail="Can not loop transfer")
    account_from: models.Account = check_own_account(
        account_number=transfer.fromacc,
        current_user_id=current_user_id,
        db=db
    )
    account_to: models.Account = db.query(models.Account).filter(models.Account.account_number == transfer.toacc).first()
    if not account_to:
        raise HTTPException(status_code=404, detail="Destination account not found")
    if account_from.account_balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Balance insufficient")
    account_from.account_balance -= transfer.amount
    account_to.account_balance += transfer.amount
    new_transaction = models.Transaction(account_number=account_from.account_number, amount=transfer.amount, transaction_type='transfer')
    new_transfer_record = models.Transfer(transaction=new_transaction, destination_account_number=account_to.account_number)
    db.add(new_transaction)
    db.add(new_transfer_record)
    db.commit()
    return new_transaction


app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, proxy_headers=True)