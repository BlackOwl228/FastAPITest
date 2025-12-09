from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlalchemy.orm import Session
from db_orm import get_db, get_current_user
from models import Album, Photo, UserSession

router = APIRouter(prefix='/album', tags=["Album"])

@router.post('/{album_id}')
def add_photo_to_album(album_id: int = Path(...),
                       photo_id: int = Query(...),
                       current_user: UserSession = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.id == album_id, Album.creator_id == current_user.user_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    photo = db.query(Photo).filter(Photo.id == photo_id,
            (Photo.creator_id == current_user.user_id) | (Photo.is_public == True)).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    album.photos.append(photo)

    return {"status": "Photo added to album", "album_id": album_id, "photo_id": photo.id}

@router.delete('/{album_id}')
def add_photo_to_album(album_id: int = Path(...),
                       photo_id: int = Query(...),
                       current_user: UserSession = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.id == album_id, Album.creator_id == current_user.user_id).first()
    if not album:
        raise HTTPException(404, "Album not found")
    
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(404, "Photo not found")
    
    if photo in album.photos:
        album.photos.remove(photo)
    else:
        raise HTTPException(404, "Photo not in album")

    return {"status": "Photo added to album", "album_id": album_id, "photo_id": photo.id}