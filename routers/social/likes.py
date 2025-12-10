from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from models import Photo, UserSession
from db_orm import get_db, get_current_user

router = APIRouter(prefix='/like', tags=["Like"])

@router.post('/{photo_id}')
def like_photo(photo_id: int = Path(...),
               user: UserSession = Depends(get_current_user),
               db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id,
            (Photo.creator_id == user.user_id) | (Photo.is_public == True)).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if user in photo.liked_by:
        raise HTTPException(status_code=409, detail="Photo is already liked")

    photo.liked_by.append(user)

@router.delete('/{photo_id}')
def like_photo(photo_id: int = Path(...),
               user: UserSession = Depends(get_current_user),
               db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id,
            (Photo.creator_id == user.user_id) | (Photo.is_public == True)).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if user in photo.liked_by:
        raise HTTPException(status_code=400, detail="Photo isn't liked yet")

    photo.liked_by.remove(user)