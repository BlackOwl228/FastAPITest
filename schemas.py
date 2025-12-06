from pydantic import BaseModel, Field
from fastapi import Query, Path
from typing import List, Optional

class SearchTag(BaseModel):
    tag: str = Path(..., min_length=3, max_length=30)
    page: int = Query(1, ge=1, description="Page number")
    limit: int = Query(20, ge=1, le=100, description="Items per page")

class SearchTags(BaseModel):
    tags: List[str] = Query(min_length=1, max_length=10)
    page: int = Query(1, ge=1, description="Page number")
    limit: int = Query(20, ge=1, le=100, description="Items per page")

class PhotoResponse(BaseModel):
    tag: str = Field(min_length=3, max_length=30)
    photos: List[str]
    count: int

class PhotosResponse(BaseModel):
    tags: List[str] = Field(min_length=1, max_length=10)
    photos: List[str]
    count: int

class PhotoMetadata(BaseModel):
    title: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field("", max_length=500)
    is_public: bool = Field(True)
    tags: str = Field("")
    size: Optional[int]
    mime_type: Optional[str]

class UserAccountData(BaseModel):
    username: str = Field(..., min_length=5, max_length=30)
    password: str = Field(..., min_length=8, max_length=30)