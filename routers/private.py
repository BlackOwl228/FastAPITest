from fastapi import APIRouter, UploadFile, HTTPException, Form, File, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid, datetime, os
from db_orm import get_db, get_current_user
from models import Tag, Photo, UserSession, Album

router = APIRouter(tags=["Private"])

@router.post('/photos')
def upload_photo(title: str = Form(..., min_length=2, max_length=50),
                 description: str = Form("", max_length=500),
                 is_public: bool = Form(..., Optional=True),
                 tags: str = Form(...),
                 size: int = Form(None),
                 mime_type: str = Form(None),
                 photo: UploadFile = File(...),
                 current_user: UserSession = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    dir_path = "E:/MyProject/MySite/Photos"
    filename = photo.filename or ""
    ext = os.path.splitext(filename)[1]
    if not ext or len(ext) > 5: ext = ".jpg"
    else: ext = ext.lower()
    file_path = f"{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(dir_path, file_path)
    with open(full_path, "wb") as f:
        f.write(photo.file.read())

    try:
        new_photo = Photo(
            title=title,
            description=description,
            filename=file_path,
            creator_id=current_user.user_id,
            is_public=is_public
        )

        db_tags = db.query(Tag).filter(Tag.name.in_(tags)).all()
        found_names = {t.name for t in db_tags}
        new_photo.tags.extend(db_tags)

        db.add(new_photo)
        db.flush()
        db.refresh(new_photo)
        
        return {
            "id": new_photo.id,
            "filename": file_path,
            "tags": tags,
            "message": "Photo uploaded successfully"
        }
        
    except Exception as e:
        if os.path.exists(full_path):
            os.remove(full_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
@router.put('/photos/{photo_id}')
def edit_photo(photo_id: int = Path(...),
               title: str = Form(..., min_length=2, max_length=50),
               description: str = Form("", max_length=500),
               is_public: bool = Form(..., Optional=True),
               tags: List[str] = Form([]),
               current_user: UserSession = Depends(get_current_user),
               db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(
    Photo.id == photo_id,
    Photo.creator_id == current_user.user_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")    

    photo.title, photo.description, photo.is_public = title, description, is_public

    if tags:
        photo.tags.clear()
        new_tags = db.query(Tag).filter(Tag.name.in_(tags)).all()
        found_names = {t.name for t in new_tags}
        photo.tags.extend(new_tags)

    return {"status": "Photo updated", "photo_id": photo.id}

@router.delete('/photos/{photo_id}')
def delete_photo(photo_id: int = Path(...),
                 current_user: UserSession = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(
    Photo.id == photo_id,
    Photo.creator_id == current_user.user_id).first()

    if photo:
        raise HTTPException(404, "You can't delete this file")
    
    file_path = f"E:/MyProject/MySite/Photos/{photo.filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise HTTPException(404, "File already deleted")

    db.delete(photo)
        
    return {"status": f"Photo id={photo_id} deleted"}
    
