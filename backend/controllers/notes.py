import asyncpg
from models.note import Note

async def list_notes(db_conn: asyncpg.Connection):
    return await db_conn.fetch("SELECT * FROM notes")
            
async def create_note(db_conn: asyncpg.Connection, note: Note):
    query = "INSERT INTO notes (title, content, user_id) VALUES ($1, $2, $3) RETURNING *"
    return await db_conn.fetchrow(query, note.title, note.content, note.user_id)

async def edit_note(db_conn: asyncpg.Connection, note_id: int, note: Note):
    query = "UPDATE notes SET title = $1, user_id = $2, content = $3 WHERE id = $4 RETURNING *"    
    return await db_conn.fetchrow(query, note.title, note.user_id, note.content, note_id)

async def delete_note(db_conn: asyncpg.Connection, note_id: int):
    query = "DELETE FROM notes WHERE id = $1 RETURNING *"    
    return await db_conn.fetchrow(query, note_id)