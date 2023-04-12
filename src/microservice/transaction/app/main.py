from __future__ import annotations
import asyncio
import os
from uuid import UUID
import uvicorn
import models, schemas
from aiohttp import ClientSession
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from dependencies import get_db, get_current_user_id, client_session_dep
from database import engine
import logging

ACCOUNT_URL = os.environ["ACCOUNT_URL"]

logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/transaction", openapi_url="/api/openapi.json", docs_url="/api/docs")
api_router = APIRouter(tags=["API"])

@app.on_event("startup")
async def startup_event():
    setattr(app.state, "client_session", ClientSession(raise_for_status=True))

@app.on_event("shutdown")
async def shutdown_event():
    task = asyncio.create_task(app.state.client_session.close())
    await asyncio.wait([task], timeout=5.0)

async def check_own_account(
    account_number: str,
    current_user_id: UUID,
    client_session: ClientSession = Depends(client_session_dep)
) -> schemas.Account:
    async with client_session.post(
        f"http://{ACCOUNT_URL}:8000/internal/check_own_account",
        json={
            "account_number": account_number,
            "user_id" : str(current_user_id)
        },
        raise_for_status=True
    ) as the_response:
        if not the_response.ok:
            raise HTTPException(status_code=404, detail="Account not found")
        account = schemas.Account.parse_obj(await the_response.json())
        # logging.info(account)
        return account

async def update_account_balance(
    account_number: str,
    account_balance: float,
    client_session: ClientSession = Depends(client_session_dep)
):
    async with client_session.post(
        f"http://{ACCOUNT_URL}:8000/internal/update_account_balance",
        json={
            "account_number": account_number,
            "account_balance" : account_balance
        },
        raise_for_status=True
    ) as the_response:
        if not the_response.ok:
            raise HTTPException(status_code=404, detail="Account not found")
        await the_response.json()
        # logging.info(account)

@api_router.get("/transactions/{account_number}", response_model=list[schemas.Transaction])
async def read_transactions(
    account_number: str,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    client_session: ClientSession = Depends(client_session_dep)
):
    account: schemas.Account = await check_own_account(
        account_number=account_number,
        current_user_id=current_user_id,
        client_session=client_session
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
async def deposit(
    deposit_request: schemas.DepositRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    client_session: ClientSession = Depends(client_session_dep)
):
    if deposit_request.amount < 1:
        raise HTTPException(status_code=400, detail="Amount can not less than 1")
    
    account: schemas.Account = await check_own_account(
        account_number=deposit_request.account_number,
        current_user_id=current_user_id,
        client_session=client_session
    )

    account.account_balance += deposit_request.amount
    update_acc_task = update_account_balance(
        account_number=account.account_number,
        account_balance=account.account_balance,
        client_session=client_session
    )
    transaction = models.Transaction(
        account_number=account.account_number, amount=deposit_request.amount, transaction_type='deposit'
    )
    await update_acc_task
    db.add(transaction)
    db.commit()
    return transaction

@api_router.post("/transfer", response_model=schemas.Transaction)
async def transfer(
    transfer: schemas.TransferRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    client_session: ClientSession = Depends(client_session_dep)
):
    logging.info(type(client_session))
    if transfer.fromacc == transfer.toacc:
        raise HTTPException(status_code=400, detail="Can not loop transfer")
    account_from: schemas.Account = await check_own_account(
        account_number=transfer.fromacc,
        current_user_id=current_user_id,
        client_session=client_session
    )
    async with client_session.post(
        f"http://{ACCOUNT_URL}:8000/internal/check_account_exist",
        json={
            "account_number": transfer.toacc
        },
        raise_for_status=True
    ) as the_response:
        if not the_response.ok:
            raise HTTPException(status_code=404, detail="Destination account not found")
        account_to = schemas.Account.parse_obj(await the_response.json())
        # logging.info(account)
    if account_from.account_balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Balance insufficient")
    account_from.account_balance -= transfer.amount
    update_acc_from_task = update_account_balance(
        account_number=account_from.account_number,
        account_balance=account_from.account_balance,
        client_session=client_session
    )
    account_to.account_balance += transfer.amount
    update_acc_to_task = update_account_balance(
        account_number=account_to.account_number,
        account_balance=account_to.account_balance,
        client_session=client_session
    )
    new_transaction = models.Transaction(account_number=account_from.account_number, amount=transfer.amount, transaction_type='transfer')
    new_transfer_record = models.Transfer(transaction=new_transaction, destination_account_number=account_to.account_number)
    await update_acc_from_task
    await update_acc_to_task
    db.add(new_transaction)
    db.add(new_transfer_record)
    db.commit()
    return new_transaction


app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, proxy_headers=True)