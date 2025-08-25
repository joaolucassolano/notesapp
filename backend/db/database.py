# database.py
import os
import asyncpg
from dotenv import load_dotenv
from typing import AsyncGenerator

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def setup_database_connection(conn: asyncpg.Connection):
    """Configura os codecs para a conexão com o banco."""
    await conn.set_type_codec(
        'uuid', encoder=str, decoder=str, schema='pg_catalog'
    )
    await conn.set_type_codec(
        'timestamp', encoder=str, decoder=str, schema='pg_catalog'
    )
    await conn.set_type_codec(
        'timestamptz', encoder=str, decoder=str, schema='pg_catalog'
    )
    print("Codecs de tipo do banco de dados configurados com sucesso.")

pool = None

async def get_db_pool() -> asyncpg.Pool:
    """Retorna o pool de conexões, criando-o se não existir."""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            init=setup_database_connection
        )
    return pool

async def get_db_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Função 'dependency' que pega uma conexão do pool e a libera no final.
    """
    db_pool = await get_db_pool()
    async with db_pool.acquire() as conn:
        yield conn