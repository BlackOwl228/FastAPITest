from fastapi import APIRouter, UploadFile, HTTPException, Form, File, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid, datetime, os
from db_orm import get_db, get_current_user
from models import Tag, Photo, UserSession

router = APIRouter(tags=["Private"])

@router.post('/photos')
def upload_photo(current_user: UserSession = Depends(get_current_user),
                 title: str = Form(..., min_length=2, max_length=50),
                 description: Optional[str] = Form("", max_length=500),
                 is_public: bool = Form(True),
                 tags: str = Form(""),
                 photo: UploadFile = File(...),
                 db: Session = Depends(get_db)):

    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    tags = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
     
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

        existing_tags = {}
        if tags:
            existing = db.query(Tag).filter(Tag.name.in_(tags)).all()
            existing_tags = {tag.name: tag for tag in existing}

        for tag_name in tags:
            tag = existing_tags.get(tag_name)
            
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()
                existing_tags[tag_name] = tag

            new_photo.tags.append(tag)

        db.add(new_photo)
        db.commit()
        db.refresh(new_photo)
        
        return {
            "id": new_photo.id,
            "filename": file_path,
            "tags": tags,
            "message": "Photo uploaded successfully"
        }
        
    except Exception as e:
        db.rollback()
        if os.path.exists(full_path):
            os.remove(full_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete('/photos/{photo_id}')
def delete_photos(photo_id: int,
                  current_user: UserSession = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(
    Photo.id == photo_id,
    Photo.creator_id == current_user.user_id).first()

    if photo:
        file_path = f"E:/MyProject/MySite/Photos/{photo.filename}"
        if os.path.exists(file_path):
            os.remove(file_path)

        db.delete(photo)
        db.commit()
        
        return {"status": f"Photo id={photo_id} deleted"}
    else: raise HTTPException(404, "You can't delete this file")