from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from db_orm import get_db
from schemas import SearchTag, SearchTags, PhotoResponse, PhotosResponse
from models import Photo, Tag
from typing import List, Optional

router = APIRouter(prefix="/photos", tags=["Searching"])

@router.get('/search/{tag}')
def photo_by_tag(tag: str = Path(..., min_length=3, max_length=30),
                 page: int = Query(1, ge=1),
                 limit: int = Query(20, ge=1, le=100),
                 db: Session = Depends(get_db)):
    
    tag_obj = db.query(Tag).filter(Tag.name == tag).first()
    if not tag_obj:
        raise HTTPException(status_code=404, detail=f"Tag '{tag}' not found")
    
    photos_found = (db.query(Photo.filename)
                    .filter(Photo.tags.any(Tag.id == tag_obj.id))
                    .order_by(Photo.created_at.desc())
                    .limit(limit)
                    .offset((page - 1) * limit)
                    .all())
    
    return PhotoResponse(
        tag=tag,
        photos=[p.filename for p in photos_found],
        count=len(photos_found))

@router.get('/search')
def photo_by_tags(tags: List[str] = Query(...),
                  page: int = Query(1, ge=1),
                  limit: int = Query(20, ge=1, le=100),
                  db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    query = text("""
        SELECT p.filename,
        COUNT(tof.tag_id) as relevance_score
        FROM photos p
        JOIN tags_of_photos tof ON tof.photo_id = p.id
        JOIN tags t ON tof.tag_id = t.id
        WHERE t.name IN :tags
        GROUP BY p.id, p.filename
        ORDER BY relevance_score DESC, p.id
        LIMIT :limit
        OFFSET :offset
    """)
    result = db.execute(query, {'tags': tuple(tags), 'limit': limit, 'offset': offset})
    
    rows = result.fetchall()
    photo_filenames = [row[0] for row in rows]  
    
    return PhotosResponse(
            tags = tags,
            photos = photo_filenames,
            count = len(photo_filenames))