from fastapi import APIRouter, HTTPException, UploadFile, Depends, Query, File, Form
from typing import List
import sqlite3
import uuid
from database import get_db

router = APIRouter(prefix="/photos", tags=["Photos"])

@router.get('')
def photo_by_tag(tag: str = Query(...)):
    with get_db() as cursor:
        cursor.execute('''SELECT p.path FROM photos p
                    JOIN tags_of_photo tof ON tof.photo_id = p.id
                    JOIN tags t ON tof.tag_id = t.id
                    WHERE t.name = ?''', (tag,))
        photos = [row[0] for row in cursor.fetchall()]

    return {
            "tag":tag,
            "photos":photos,
            "count":len(photos)
            }
    
@router.get('/search')
def photo_by_tags(tags: List[str] = Query(...)):
    placeholder = ', '.join('?' for _ in tags)

    with get_db() as cursor:
        cursor.execute(f'''SELECT p.path,
                        COUNT(tof.tag_id) as relevance_score
                        FROM photos p
                        JOIN tags_of_photo tof ON tof.photo_id = p.id
                        JOIN tags t ON tof.tag_id = t.id
                        WHERE t.name IN ({placeholder})
                        GROUP BY p.id, p.path
                        ORDER BY relevance_score DESC, p.id;''', tags)
        photos = [row[0] for row in cursor.fetchall()]

    return {
            "tags":tags,
            "photos":photos,
            "count":len(photos)
            }

@router.post('')
def upload_photo(name: str = Form(...),
                tags: List[str] = Form(...),
                photo: UploadFile = File(...)):
    
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.replace(";", ",").split(",") if t.strip()]
    if isinstance(tags, (list, tuple)):
        out = []
        for t in tags:
            if isinstance(t, str):
                out.extend([p.strip() for p in t.replace(";", ",").split(",") if p.strip()])
        tags =  out
     
    dir_path = "E:/Web Project/photos"
    

    orig_ext = (photo.filename or "").split(".")[-1]
    ext = orig_ext if orig_ext and len(orig_ext) <= 6 else "jpg"
    file_path = f"{uuid.uuid4().hex}.{ext}"

    full_path = f"{dir_path}/{file_path}"
    with open(full_path, "wb") as f:
        f.write(photo.file.read())    
    
    with get_db() as cursor:
        cursor.execute('''INSERT INTO photos (name, path)
                        VALUES (?, ?)
                        ''', (name, file_path))
        photo_id = cursor.lastrowid
            
        for tag in tags:
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
            tag_id = cursor.fetchone()[0]
                
            cursor.execute("""INSERT INTO tags_of_photo (photo_id, tag_id) VALUES (?, ?)""", (photo_id, tag_id))

