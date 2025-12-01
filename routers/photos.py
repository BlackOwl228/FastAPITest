from fastapi import APIRouter, HTTPException, Query
from typing import List
from database import get_db

router = APIRouter(prefix="/photos", tags=["Photos"])

@router.get('')
def photo_by_tag(tag: str = Query(...)):
    with get_db() as cursor:
        cursor.execute('''SELECT p.filename FROM photos p
                    JOIN tags_of_photos tof ON tof.photo_id = p.id
                    JOIN tags t ON tof.tag_id = t.id
                    WHERE t.name = %s''', (tag,))
        photos = [row[0] for row in cursor.fetchall()]

    return {
            "tag":tag,
            "photos":photos,
            "count":len(photos)
            }
    
@router.get('/search')
def photo_by_tags(tags: List[str] = Query(...)):
    placeholder = ', '.join('%s' for _ in tags)

    with get_db() as cursor:
        cursor.execute(f'''SELECT p.filename,
                        COUNT(tof.tag_id) as relevance_score
                        FROM photos p
                        JOIN tags_of_photos tof ON tof.photo_id = p.id
                        JOIN tags t ON tof.tag_id = t.id
                        WHERE t.name IN ({placeholder})
                        GROUP BY p.id, p.filename
                        ORDER BY relevance_score DESC, p.id;''', tags)
        photos = [row[0] for row in cursor.fetchall()]

    return {
            "tags":tags,
            "photos":photos,
            "count":len(photos)
            }

