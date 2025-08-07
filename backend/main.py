from typing import Optional
from fastapi import FastAPI
from models.note import Note
from routers import api_router


app = FastAPI()

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à sua API!"}