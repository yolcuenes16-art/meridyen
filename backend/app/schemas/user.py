from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    display_name: str = Field(min_length=2, max_length=50)
    bio: str = Field(default="", max_length=160)
    category: str = Field(default="Genel", max_length=50)


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=50)
    bio: str | None = Field(default=None, max_length=160)
    category: str | None = Field(default=None, max_length=50)


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    bio: str
    category: str
    followers_count: int
    following_count: int
    post_count: int
    wellbeing_score: float
    created_at: datetime


class UserPreferences(BaseModel):
    preferred_categories: list[str] = Field(default_factory=list)
    wellbeing_mode: bool = True
    safe_content: bool = True
    usage_mode: str = "odak"
