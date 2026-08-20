from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.schemas.analysis import ContentAnalysis
from backend.app.services.analysis_service import (
    BERT_SWAP_NOTE,
    ENGINE_NAME,
    content_analysis_service,
)
from backend.app.services.ranking_service import MODE_WEIGHTS, rank_content


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)


class AnalysisRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: str = "Genel"
    mode: str = "odak"


@router.post(
    "/content",
    response_model=ContentAnalysis,
)
async def analyze_content(payload: AnalysisRequest) -> ContentAnalysis:
    return content_analysis_service.analyze(
        title=payload.title,
        description=payload.description,
        category=payload.category,
    )


@router.post("/preview")
async def analyze_and_rank(payload: AnalysisRequest):
    analysis = content_analysis_service.analyze(
        title=payload.title,
        description=payload.description,
        category=payload.category,
    )
    ranking = rank_content(analysis, payload.mode)
    return {
        "analysis": analysis,
        "ranking": ranking,
        "privacy": "Mod kullanıcı tarafından seçilir; gizli ruh hali tahmini yoktur.",
        "engine": ENGINE_NAME,
        "nlp_roadmap": BERT_SWAP_NOTE,
        "mode_weights": {
            key: [
                {"label": label, "field": field, "weight": weight}
                for label, field, weight in weights
            ]
            for key, weights in MODE_WEIGHTS.items()
        },
    }