from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from meridyen.domain.models import ContentInput, Mode


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)


class RankRequest(BaseModel):
    mode: Mode
    content: list[ContentInput] = Field(min_length=1, max_length=500)


class RewardRequest(RankRequest):
    pool_amount: float = Field(gt=0)


class ConsentRequest(BaseModel):
    user_id: UUID
    mode: Mode
    consent: bool


class AggregateRequest(BaseModel):
    metric: str = Field(pattern="^[a-z0-9_.-]{1,80}$")
    count: int = Field(ge=0)
