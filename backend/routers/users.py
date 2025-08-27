from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from db.database import get_db_conn
import controllers.users as users_controller
import asyncpg
from utils.security import get_current_user

router =  APIRouter()

@router.get("/")
async def list_users(db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await users_controller.list_users(db_conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{id}")
async def get_user(id: int, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await users_controller.get_user(db_conn, id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
            
@router.post("/")
async def create_user(user: dict, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await users_controller.create_user(db_conn, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{id}")
async def edit_user(id: int, user: dict, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await users_controller.edit_user(db_conn, id, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{id}")
async def delete_user(id: int, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await users_controller.delete_user(db_conn, id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))