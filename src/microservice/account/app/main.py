import random
import string
from uuid import UUID
import uvicorn
import models, schemas
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user_id
from database import engine
import logging

logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/account", openapi_url="/api/openapi.json", docs_url="/api/docs")
api_router = APIRouter(tags=["API"])
internal_router = APIRouter(include_in_schema=False)

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

@internal_router.post("/create_account/{user_id}", response_model=schemas.AccountResponse)
async def account_list(user_id: str, db: Session = Depends(get_db)):
    all_acc_no = [id[0] for id in db.query(models.Account.account_number).all()]
    rand_acc_no = ''.join(random.choice(string.digits) for _ in range(10))
    while rand_acc_no in all_acc_no:
        rand_acc_no = ''.join(random.choice(string.digits) for _ in range(10))
    new_account = models.Account(user_id=UUID(user_id), account_number=rand_acc_no, account_balance=0)
    db.add(new_account)
    db.commit()
    return new_account

@internal_router.post("/check_own_account", response_model=schemas.AccountResponse)
async def internal_check_own_account(input: schemas.CheckOwnAccountRequest, db: Session = Depends(get_db)):
    account: models.Account = check_own_account(
        account_number=input.account_number,
        current_user_id=input.user_id,
        db=db
    )
    return account

@internal_router.post("/check_account_exist", response_model=schemas.AccountResponse)
async def check_account_exist(input: schemas.ChecAccountExistRequest, db: Session = Depends(get_db)):
    account: models.Account = (
        db.query(models.Account)
        .filter(models.Account.account_number == input.account_number)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@internal_router.post("/update_account_balance")
async def update_account_balance(input: schemas.UpdateAccountBalanceRequest, db: Session = Depends(get_db)):
    account: models.Account = (
        db.query(models.Account)
        .filter(models.Account.account_number == input.account_number)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.account_balance = input.account_balance
    db.commit()
    return {"success": True}

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


app.include_router(api_router, prefix="/api")
app.include_router(internal_router, prefix="/internal")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, proxy_headers=True)