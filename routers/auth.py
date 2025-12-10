from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid
from db_orm import get_db, get_current_user
from models import User, UserSession
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/reg")
def registration_user(username: str = Form(..., min_length=5, max_length=30),
                      password: str = Form(..., min_length=8, max_length=30),
                      db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    password_hash = pwd_context.hash(password)
    new_user = User(username=username, password_hash=password_hash)
    db.add(new_user)
    db.flush()
    db.refresh(new_user)
        
    return {"status": "User created", "user_id": new_user.id}

@router.post("/login")
def login_user(username: str = Form(..., min_length=3, max_length=30),
               password: str = Form(..., min_length=3, max_length=30),
               db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    
    session = UserSession(session_id=uuid.uuid4().hex,
                          user_id=user.id,
                          expires_at=datetime.now(timezone.utc) + timedelta(hours=24))
    db.add(session)
        
    return {"session_id": session.session_id, "expires_at": session.expires_at.isoformat()}

@router.post("/logout")
def logout_user(session: UserSession = Depends(get_current_user),
                db: Session = Depends(get_db)):
    db.delete(session)