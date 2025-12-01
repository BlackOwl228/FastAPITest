from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from db_orm import get_db, get_current_user
from models import User, UserSession

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/reg")
def registration_user(username: str,
                      password: str,
                      db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(username = username, password_hash = password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
        
    return {"status": "User created", "user_id": new_user.id}

@router.post("/login")
def login_user(username: str,
               password: str,
               db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.password_hash == password).first()
    if user:
        session = UserSession(session_id = uuid.uuid4().hex,
                              user_id = user.id,
                              expires_at = datetime.now() + timedelta(hours=24))
        db.add(session)
        db.commit()
        
        return {"session_id": session.session_id, "expires_at": session.expires_at.isoformat()}
    else: HTTPException(status_code=404, detail="Wrong username or password")

@router.post("/logout")
def logout_user(session: UserSession = Depends(get_current_user),
                db: Session = Depends(get_db)):
    db.delete(session)
    db.commit()
