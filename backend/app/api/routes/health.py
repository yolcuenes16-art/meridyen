from fastapi import APIRouter

from backend.app.core.config import settings
from backend.app.services.analysis_service import ENGINE_NAME, BERT_SWAP_NOTE


router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "meridyen-api",
        "version": settings.app_version,
        "nlp_engine": ENGINE_NAME,
        "privacy": "Ruh hali veya gizli duygu çıkarımı yapılmaz; tek sinyal kullanıcının seçtiği moddur.",
        "nlp_roadmap": BERT_SWAP_NOTE,
    }
