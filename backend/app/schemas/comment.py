from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
    )
    content: str = Field(
        min_length=1,
        max_length=1000,
    )


class CommentResponse(BaseModel):
    id: int
    post_id: int
    username: str
    content: str
    created_at: datetime