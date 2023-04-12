import os
from database import SessionLocal
from starlette.requests import Request
from aiohttp import ClientSession

# JWT SECRET
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def client_session_dep(request: Request) -> ClientSession:
    return request.app.state.client_session