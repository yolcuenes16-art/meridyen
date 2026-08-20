from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class Mode(StrEnum):
    FOCUS = "focus"
    LEARN = "learn"
    FUN = "fun"


class ContentInput(BaseModel):
    content_id: UUID = Field(default_factory=uuid4)
    creator_id: UUID
    text: str = Field(min_length=1, max_length=10_000)
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engagement_rate: float = Field(default=0.0, ge=0, le=1)
    creator_followers: int = Field(default=0, ge=0)
    opted_in_creator_rewards: bool = True

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.split())


class SignalScores(BaseModel):
    sentiment: float = Field(ge=-1, le=1)
    toxicity: float = Field(ge=0, le=1)
    spam: float = Field(ge=0, le=1)
    focus_fit: float = Field(ge=0, le=1)
    learning_fit: float = Field(ge=0, le=1)
    fun_fit: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    model_version: str


class ScoreCard(BaseModel):
    wellbeing_score: float = Field(ge=0, le=100)
    safety_score: float = Field(ge=0, le=100)
    quality_score: float = Field(ge=0, le=100)
    rank_weight: float = Field(ge=0, le=100)
    visibility_multiplier: float = Field(ge=0, le=2)
    eligibility: bool
    reasons: list[str]


class RankedContent(BaseModel):
    content: ContentInput
    signals: SignalScores
    scorecard: ScoreCard
    position: int


class ConsentRecord(BaseModel):
    user_id: UUID
    mode: Mode
    consented_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None


class RewardLedgerEntry(BaseModel):
    entry_id: UUID = Field(default_factory=uuid4)
    content_id: UUID
    creator_id: UUID
    gross_pool_share: float = Field(ge=0)
    platform_commission: float = Field(ge=0)
    creator_payout: float = Field(ge=0)
    visibility_multiplier: float = Field(ge=0, le=2)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
