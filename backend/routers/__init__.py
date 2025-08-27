from fastapi import APIRouter
from . import notes, users, websocket, login

api_router = APIRouter()

api_router.include_router(notes.router, prefix="/notes", tags=["Notes"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(websocket.router, prefix="/websocket", tags=["Websocket"])
api_router.include_router(login.router, prefix="", tags=["LoginGoogle"])