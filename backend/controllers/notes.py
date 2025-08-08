import asyncpg
from models.note import Note

async def list_notes(db_conn: asyncpg.Connection):
    notes = await db_conn.fetch("SELECT * FROM notes")
    return {"data": notes}
            
async def create_note(db_conn: asyncpg.Connection, note: Note):
    query = "INSERT INTO notes (title, content, user_id) VALUES ($1, $2, $3) RETURNING *"
    new_note = await db_conn.fetchrow(query, note.title, note.content, note.user_id)
    
    return {"note": new_note}