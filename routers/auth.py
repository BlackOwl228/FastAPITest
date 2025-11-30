from fastapi import APIRouter, HTTPException, Form
from datetime import datetime, timedelta
import uuid
from database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/reg")
def registration_user(username: str,
                      password: str):
    with get_db() as cursor:
        cursor.execute('''INSERT INTO users(username, password)
                    VALUES (?,?)''', (username, password))
        
    return {"status": "User created"}

@router.post("/login")
def login_user(username: str,
               password: str):
    with get_db() as cursor:
        cursor.execute('''SELECT id FROM users
                    WHERE username = ? AND password = ?''', (username, password))
        
        user_id = cursor.fetchone()[0]
        session_id = uuid.uuid4().hex
        expires_at = datetime.now() + timedelta(hours=24)

        cursor.execute(f'''INSERT INTO sessions (session_id, user_id, expires_at)
                    VALUES(?, ?, ?)''', (session_id, user_id, expires_at))
        
    return {"session_id": session_id, "expires_at": expires_at.isoformat()}

@router.post("/logout")
def logout_user(session_id: str):
    with get_db() as cursor:
        cursor.execute('''DELETE FROM sessions WHERE session_id = ?''', (session_id,))
    return {"status": "Session deleted"}
