from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException, Depends, Header
from typing import Generator
from models import UserSession
from datetime import datetime

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/photos"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    session_id: str = Header(...),
    db: Session = Depends(get_db)
) -> UserSession:
    user = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.expires_at > datetime.now()
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return user