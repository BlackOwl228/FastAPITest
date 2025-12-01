from pydantic import BaseModel, Field
from typing import List

 
class PhotoResponse(BaseModel):
    tag: str = Field(min_length=3, max_length=30)
    photos: List[str]
    count: int

class PhotosResponse(BaseModel):
    tags: List[str] = Field(min_length=1, max_length=10)
    photos: List[str]
    count: int
