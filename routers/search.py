from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from sqlalchemy import text
from db_orm import get_db
from models import Photo, Tag
from typing import List

router = APIRouter(prefix="/photos", tags=["Searching"])

@router.get('/search/{tag}')
def photo_by_tag(tag: str = Path(..., min_length=3, max_length=30),
                 page: int = Query(1, ge=1),
                 limit: int = Query(20, ge=1, le=100),
                 db: Session = Depends(get_db)):
    
    tag_obj = db.query(Tag).filter(Tag.name == tag).first()
    if not tag_obj:
        raise HTTPException(status_code=404, detail=f"Tag '{tag}' not found")
    
    photos = (db.query(Photo.filename)
             .filter(Photo.tags.any(Tag.id == tag_obj.id))
             .order_by(Photo.created_at.desc())
             .limit(limit + 1)
             .offset((page - 1) * limit)
             .all())
    
    has_more = len(photos) > limit
    photos_response = photos[:limit]
    
    return {"tag": tag,
            "photos": photos_response,
            "has_more": has_more}

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
    result = db.execute(query, {'tags': tuple(tags), 'limit': limit+1, 'offset': offset})
    
    photos = [row[0] for row in result.fetchall()]

    has_more = len(photos) > limit
    photos_response = photos[:limit]
    
    return {"tags": tags,
            "photos": photos_response,
            "has_more": has_more}


@router.get("/files/{filename}")
def file_by_path(filename: str):
    try:
        return FileResponse(f'E:/MyProject/MySite/Photos/{filename}')
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")