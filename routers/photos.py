from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from db_orm import get_db
from schemas import PhotoResponse, PhotosResponse
from models import Photo, Tag
from typing import List

router = APIRouter(prefix="/photos", tags=["Searching"])

@router.get('/tags')
def photo_by_tag(tag: str = Query(..., min_length=3, max_length=30, description="Tag for searching"),
                     db: Session = Depends(get_db)):
    
    tag_obj = db.query(Tag).filter(Tag.name == tag).first()
    
    photo_filenames = [photo.filename for photo in tag_obj.photos]
    return PhotoResponse(
        tag=tag,
        photos=photo_filenames,
        count=len(photo_filenames))

@router.get('/search')
def photo_by_tags(tags: List[str] = Query(..., min_length=1, max_length=30, description="Tags for searching"),
                  db: Session = Depends(get_db)):
    query = text("""
        SELECT p.filename,
        COUNT(tof.tag_id) as relevance_score
        FROM photos p
        JOIN tags_of_photos tof ON tof.photo_id = p.id
        JOIN tags t ON tof.tag_id = t.id
        WHERE t.name IN :tags
        GROUP BY p.id, p.filename
        ORDER BY relevance_score DESC, p.id
    """)
    
    result = db.execute(query, {'tags': tuple(tags)})
    
    rows = result.fetchall()
    photo_filenames = [row[0] for row in rows]  
    
    return PhotosResponse(
            tags = tags,
            photos = photo_filenames,
            count = len(photo_filenames))