from fastapi import APIRouter

from backend.app.services.gamification_service import gamification_service

router = APIRouter(
    prefix="/api/v1/gamification",
    tags=["Gamification"],
)


@router.get("/{username}")
async def get_user_gamification(username: str):
    return gamification_service.get_user_stats(username)
