import os
import asyncpg
from dotenv import load_dotenv
from typing import AsyncGenerator

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db_conn() -> AsyncGenerator:
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        yield conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise
    finally:
        if conn:
            await conn.close()