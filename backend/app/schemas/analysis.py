from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    label: str
    weight: float = Field(ge=0, le=1)
    value: float = Field(ge=0, le=100)
    contribution: float


class ContentAnalysis(BaseModel):
    quality_score: float = Field(ge=0, le=100)
    educational_score: float = Field(ge=0, le=100)
    safety_score: float = Field(ge=0, le=100)
    spam_score: float = Field(ge=0, le=100)
    wellbeing_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)
    focus_fit: float = Field(ge=0, le=100)
    learn_fit: float = Field(ge=0, le=100)
    fun_fit: float = Field(ge=0, le=100)
    visibility_multiplier: float = Field(ge=0, le=2)
    reasons: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    engine: str = "tr-lexicon-v2"
    latency_ms: float = 0.0
