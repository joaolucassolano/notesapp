from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from db.database import get_db_conn
from models.note import Note
import controllers.notes as notes_controller
import asyncpg

router =  APIRouter()

@router.get("/")
async def list_notes(db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        notes = await notes_controller.list_notes(db_conn)
        return {"data": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
            
@router.post("/")
async def create_note(note: Note, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        new_note = await notes_controller.create_note(db_conn, note)
        return {"note": new_note}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))