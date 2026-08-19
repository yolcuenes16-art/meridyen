from pydantic import BaseModel, Field


class ContentAnalysis(BaseModel):
    quality_score: float = Field(ge=0, le=100)
    educational_score: float = Field(ge=0, le=100)
    safety_score: float = Field(ge=0, le=100)
    spam_score: float = Field(ge=0, le=100)
    wellbeing_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)