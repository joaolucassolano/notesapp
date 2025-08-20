from fastapi import APIRouter
from . import notes, websocket

api_router = APIRouter()

api_router.include_router(notes.router, prefix="/notes", tags=["Notes"])
api_router.include_router(websocket.router, prefix="/websocket", tags=["Websocket"])