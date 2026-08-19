from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    author_username: str = Field(
        min_length=3,
        max_length=30,
    )
    content: str = Field(
        min_length=1,
        max_length=5000,
    )
    category: str = Field(
        min_length=2,
        max_length=50,
    )


class PostResponse(BaseModel):
    id: int
    author_username: str
    content: str
    category: str
    created_at: datetime

    quality_score: float
    educational_score: float
    safety_score: float
    spam_score: float
    wellbeing_score: float
    overall_score: float

    is_publishable: bool