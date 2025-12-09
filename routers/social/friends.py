from fastapi import APIRouter, HTTPException, Depends, Path, Form
from sqlalchemy.orm import Session
from models import User, Photo, UserSession
from db_orm import get_db, get_current_user

router = APIRouter(prefix='/friends', tags=["Friend"])


