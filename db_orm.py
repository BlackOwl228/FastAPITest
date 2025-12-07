from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException, Depends, Cookie
from typing import Generator
from models import UserSession
from datetime import datetime, timezone
from fastapi.security.api_key import APIKeyHeader

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/photos"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

session_token = APIKeyHeader(name="X-Session-Token", auto_error=False)

def get_current_user(session_id: str = Depends(session_token),
                     db: Session = Depends(get_db)) -> UserSession:
    user = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return user

def get_admin(session_id: str = Depends(session_token),
              db: Session = Depends(get_db)
) -> UserSession:
    user = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if user.is_admin == False: 
        raise HTTPException(status_code=403, detail="You aren't admin")
    
    return user