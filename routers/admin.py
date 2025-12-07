from fastapi import APIRouter, HTTPException, Depends, Path, Form
from sqlalchemy.orm import Session
from models import User, Photo, UserSession
from db_orm import get_db, get_admin
import os

router = APIRouter(tags=["Admin"], prefix="/admin")

@router.post('/users/{user_id}')
def ban_user(user_id: int = Path(...),
                     current_user: UserSession = Depends(get_admin),
                     db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User doesn't exists")

    user.is_active = False
        
    return {"status": f"User {user_id} was banned"}

@router.delete('/photos/{photo_id}')
def delete_photo_admin(photo_id: int = Path(...),
                     current_user: UserSession = Depends(get_admin),
                     db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(404, "File doesn't exists")
    
    file_path = f"E:/MyProject/MySite/Photos/{photo.filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise HTTPException(404, "File already deleted")

    db.delete(photo)
        
    return {"status": f"Photo id={photo_id} deleted"}