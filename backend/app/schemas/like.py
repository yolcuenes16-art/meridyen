from datetime import datetime

from pydantic import BaseModel, Field


class LikeCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)


class LikeResponse(BaseModel):
    post_id: int
    username: str
    created_at: datetime
    like_count: int = 0
    liked: bool = True
