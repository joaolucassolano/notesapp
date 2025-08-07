from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from db.database import get_db_conn
from models.note import Note
import asyncpg

router =  APIRouter()

@router.get("/")
async def list_notes(db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        notes = await db_conn.fetch("SELECT * FROM notes")
        
        return {"data": notes}
    except Exception as e:
        return {"error": str(e)}
            
@router.post("/")
async def create_note(note: Note, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    try:
        query = "INSERT INTO notes (title, content, user_id) VALUES ($1, $2, $3) RETURNING *"
        new_note = await db_conn.fetchrow(query, note.title, note.content, note.user_id)
        
        return {"note": new_note}
    except Exception as e:
        return {"error": str(e)}