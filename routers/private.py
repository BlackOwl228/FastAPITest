from fastapi import APIRouter, UploadFile, HTTPException, Form, File
from typing import List
import uuid 
from database import get_db

router = APIRouter(tags=["Private"])

@router.post('/photos')
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

@router.delete('/photos')
def delete_photos(session_id: str,
                  photo_id: int):
    with get_db() as cursor:
        cursor.execute('''SELECT user_id FROM sessions
                       WHERE session_id = ?''', (session_id,))
        row = cursor.fetchone()
        if not row: raise HTTPException(status_code=401, detail="Invalid session")
        else: user_id = row[0]
        cursor.execute('''DELETE FROM photos
                       WHERE id = ? AND creator_id = ?''', (photo_id, user_id))
    return {"status": f"Photo id={photo_id} deleted"}
