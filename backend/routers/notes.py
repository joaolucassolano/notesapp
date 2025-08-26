from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from db.database import get_db_conn
from models.note import Note
import controllers.notes as notes_controller
import asyncpg
from utils.security import get_current_user

router =  APIRouter()

@router.get("/")
async def list_notes(db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await notes_controller.list_notes(db_conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{note_id}")
async def get_note(note_id: int, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await notes_controller.get_note(db_conn, note_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
            
@router.post("/")
async def create_note(note: dict, db_conn: asyncpg.Connection = Depends(get_db_conn), current_user: str = Depends(get_current_user)):
    print(f"Usuário '{current_user}' está criando uma nota com conteúdo: '{note}'")
    try:
        return await notes_controller.create_note(db_conn, note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{note_id}")
async def edit_note(note_id: int, note: Note, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await notes_controller.edit_note(db_conn, note_id, note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{note_id}")
async def delete_note(note_id: int, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        return await notes_controller.delete_note(db_conn, note_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))