from fastapi import APIRouter

from backend.app.schemas.analysis import ContentAnalysis
from backend.app.services.analysis_service import content_analysis_service


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)


@router.post(
    "/content",
    response_model=ContentAnalysis,
)
async def analyze_content(
    title: str,
    description: str,
    category: str,
) -> ContentAnalysis:
    return content_analysis_service.analyze(
        title=title,
        description=description,
        category=category,
    )