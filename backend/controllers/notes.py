import asyncpg
from models.note import Note

async def list_notes(db_conn: asyncpg.Connection):
    return await db_conn.fetch("SELECT * FROM notes")

async def get_note(db_conn: asyncpg.Connection, note_id: int):
    query = "SELECT * FROM notes where id = $1"  
    return await db_conn.fetchrow(query, note_id)
            
async def create_note(db_conn: asyncpg.Connection, note: dict):
    query = "INSERT INTO notes (title, content, user_id) VALUES ($1, $2, $3) RETURNING *"
    return await db_conn.fetchrow(query, note["title"], note["content"], note["user_id"])

async def edit_note(db_conn: asyncpg.Connection, note_id: int, note: Note):
    query = "UPDATE notes SET title = $1, content = $2 WHERE id = $3 RETURNING *"    
    return await db_conn.fetchrow(query, note.title, note.content, note_id)

async def delete_note(db_conn: asyncpg.Connection, note_id: int):
    query = "DELETE FROM notes WHERE id = $1 RETURNING *"    
    return await db_conn.fetchrow(query, note_id)