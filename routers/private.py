from fastapi import APIRouter, UploadFile, HTTPException, Form, File, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid, datetime, os
from db_orm import get_db, get_current_user
from models import Tag, Photo, UserSession
from schemas import PhotoMetadata

router = APIRouter(tags=["Private"])

@router.post('/photos')
def upload_photo(metadata: PhotoMetadata = Form(...),
                 photo: UploadFile = File(...),
                 current_user: UserSession = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    title = metadata.title
    description = metadata.description or ""
    tags = [t.strip() for t in metadata.tags.split(",") if t.strip()] if metadata.tags else []
    is_public = metadata.is_public

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
    
@router.patch('/photos/{photo_id}')
def edit_photo(photo_id: int,
               metadata: PhotoMetadata,
               current_user: UserSession = Depends(get_current_user),
               db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(
    Photo.id == photo_id,
    Photo.creator_id == current_user.user_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")    
    
    title = metadata.title
    description = metadata.description or ""
    tags = [t.strip() for t in metadata.tags.split(",") if t.strip()] if metadata.tags else []
    is_public = metadata.is_public
    size = metadata.size
    mime_type = metadata.mime_type

    photo.title, photo.description, photo.is_public = title, description, is_public
    photo.size, photo.mime_type = size, mime_type

    photo.tags.clear()
    for tag_name in tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        photo.tags.append(tag)

    return {"status": "Photo updated", "photo_id": photo.id}

@router.delete('/photos/{photo_id}')
def delete_photo(photo_id: int,
                 current_user: UserSession = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(
    Photo.id == photo_id,
    Photo.creator_id == current_user.user_id).first()

    if photo:
        file_path = f"E:/MyProject/MySite/Photos/{photo.filename}"
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise HTTPException(404, "File already deleted")

        db.delete(photo)
        
        return {"status": f"Photo id={photo_id} deleted"}
    else:
        raise HTTPException(404, "You can't delete this file")