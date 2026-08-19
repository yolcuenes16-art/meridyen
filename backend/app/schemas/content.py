from datetime import datetime

from pydantic import BaseModel, Field


class ContentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    category: str = Field(min_length=2, max_length=50)
    source: str = Field(min_length=2, max_length=200)


class ContentResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    source: str
    created_at: datetime