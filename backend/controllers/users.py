import asyncpg

async def list_users(db_conn: asyncpg.Connection):
    return await db_conn.fetch("SELECT * FROM users")

async def get_user(db_conn: asyncpg.Connection, id: int):
    query = "SELECT * FROM users where id = $1"  
    return await db_conn.fetchrow(query, id)

async def get_user_from_email(db_conn: asyncpg.Connection, email: str):
    query = "SELECT * FROM users where email = $1"  
    return await db_conn.fetchrow(query, email)
            
async def create_user(db_conn: asyncpg.Connection, user: dict):
    query = "INSERT INTO users (google_id, name, email, photo_url) VALUES ($1, $2, $3, $4) RETURNING *"
    return await db_conn.fetchrow(query, user["google_id"], user["name"], user["email"], user["photo_url"])

async def edit_user(db_conn: asyncpg.Connection, id: int, user: dict):
    query = "UPDATE users SET name = $1, photo_url = $2 WHERE id = $3 RETURNING *"    
    return await db_conn.fetchrow(query, user["name"], user["photo_url"], id)

async def delete_user(db_conn: asyncpg.Connection, id: int):
    query = "DELETE FROM users WHERE id = $1 RETURNING *"    
    return await db_conn.fetchrow(query, id)