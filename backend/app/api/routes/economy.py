from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.services.post_service import post_service
from backend.app.services.ranking_service import normalize_mode


router = APIRouter(
    prefix="/api/v1/economy",
    tags=["Economy"],
)


@router.get("/creators")
async def creator_board(mode: str = Query(default="odak"), db: AsyncSession = Depends(get_db)):
    return {
        "mode": normalize_mode(mode),
        "weekly_pool_try": 5000,
        "formula": (
            "pay = havuz x (gorunurluk_carpmani * refah_skoru) / toplam_agirlik"
        ),
        "creators": await post_service.creator_board(db, mode),
    }


@router.get("/wellbeing")
async def wellbeing_snapshot(mode: str = Query(default="odak"), db: AsyncSession = Depends(get_db)):
    return await post_service.wellbeing_snapshot(db, mode)
