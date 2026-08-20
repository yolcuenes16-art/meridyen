from datetime import datetime

from pydantic import BaseModel, Field


class RankBreakdownItem(BaseModel):
    label: str
    weight: float
    value: float
    contribution: float


class PostCreate(BaseModel):
    author_username: str = Field(min_length=3, max_length=30)
    content: str = Field(min_length=1, max_length=5000)
    category: str = Field(min_length=2, max_length=50)
    display_name: str | None = Field(default=None, max_length=50)
    image_url: str | None = Field(default=None)


class PostUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=5000)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    image_url: str | None = None


class PostResponse(BaseModel):
    id: int
    author_username: str
    display_name: str
    content: str
    category: str
    image_url: str | None = None
    created_at: datetime

    quality_score: float
    educational_score: float
    safety_score: float
    spam_score: float
    wellbeing_score: float
    overall_score: float
    focus_fit: float
    learn_fit: float
    fun_fit: float
    visibility_multiplier: float
    estimated_weekly_share: float = 0
    analysis_reasons: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    engine: str = "tr-lexicon-v2"
    latency_ms: float = 0.0

    rank_score: float = 0
    rank_reasons: list[str] = Field(default_factory=list)
    rank_breakdown: list[RankBreakdownItem] = Field(default_factory=list)
    active_mode: str = "odak"

    like_count: int = 0
    comment_count: int = 0
    liked_by_me: bool = False

    is_publishable: bool
    moderation_note: str | None = None
