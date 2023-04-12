from __future__ import annotations
import asyncio
import os
import uvicorn
import models, schemas
from aiohttp import ClientSession
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dependencies import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, client_session_dep
from database import engine
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
import logging

ACCOUNT_URL = os.environ["ACCOUNT_URL"]

logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/user", openapi_url="/api/openapi.json", docs_url="/api/docs")
api_router = APIRouter(tags=["API"])

@app.on_event("startup")
async def startup_event():
    setattr(app.state, "client_session", ClientSession(raise_for_status=True))

@app.on_event("shutdown")
async def shutdown_event():
    task = asyncio.create_task(app.state.client_session.close())
    await asyncio.wait([task], timeout=5.0)

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
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    client_session: ClientSession = Depends(client_session_dep)
):
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, fullname=user.fullname, phone_no=user.phone_no, birthday=user.birthday, password=hashed_password)
    db.add(new_user)
    db.flush()
    async with client_session.post(
        f"http://{ACCOUNT_URL}:8000/internal/create_account/{str(new_user.id)}", raise_for_status=True
    ) as the_response:
        if not the_response.ok:
            raise HTTPException(status_code=500, detail="INTERNAL ERROR")
        response = await the_response.json()
        # logging.info(response)
    db.commit()
    return new_user


app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, proxy_headers=True)