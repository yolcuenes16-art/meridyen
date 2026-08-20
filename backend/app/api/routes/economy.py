from fastapi import APIRouter, Query

from backend.app.services.post_service import post_service
from backend.app.services.ranking_service import normalize_mode


router = APIRouter(
    prefix="/api/v1/economy",
    tags=["Economy"],
)


@router.get("/creators")
async def creator_board(mode: str = Query(default="odak")):
    return {
        "mode": normalize_mode(mode),
        "weekly_pool_try": 5000,
        "formula": (
            "pay = havuz × (görünürlük_çarpanı × refah_skoru) / toplam_ağırlık"
        ),
        "creators": post_service.creator_board(mode),
    }


@router.get("/wellbeing")
async def wellbeing_snapshot(mode: str = Query(default="odak")):
    return post_service.wellbeing_snapshot(mode)
