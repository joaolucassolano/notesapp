from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from db.database import get_db_conn
from models.note import Note
import controllers.notes as notes_controller
import asyncpg
from fastapi.security import OAuth2PasswordBearer
import requests
import os
from jose import jwt
from dotenv import load_dotenv
from utils.security import create_access_token

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

router =  APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/google"

@router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }

@router.get("/auth/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    response = requests.post(token_url, data = data)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not exchange code for token")
    
    access_token_google = response.json().get("access_token")
    
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token_google}"}
    )
    
    if user_info_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not fetch user info from Google")
    
    user_info = user_info_response.json()
    email = user_info.get("email")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google account")
    
    token_payload = {"sub": email}
    jwt_token = create_access_token(data=token_payload)
    return {"access_token": jwt_token, "token_type": "bearer"}

@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=['HS256'])