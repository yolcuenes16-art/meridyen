from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.schemas.like import LikeCreate, LikeResponse
from backend.app.services.notification_service import notify_like
from backend.app.services.post_service import post_service


router = APIRouter(
    prefix="/api/v1/posts",
    tags=["Likes"],
)


@router.post(
    "/{post_id}/likes",
    response_model=LikeResponse,
)
async def like_post(post_id: int, like: LikeCreate, db: AsyncSession = Depends(get_db)) -> LikeResponse:
    try:
        count, liked = await post_service.toggle_like(post_id, like.username, db)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        ) from exc

    if liked:
        post = await post_service.get_post(post_id, db)
        if post and post.author_username.lower() != like.username.lower():
            await notify_like(post.author_username, like.username, post_id)

    return LikeResponse(
        post_id=post_id,
        username=like.username,
        created_at=datetime.now(timezone.utc),
        like_count=count,
        liked=liked,
    )


@router.get("/{post_id}/likes")
async def get_post_likes(post_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    post = await post_service.get_post(post_id, db)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return {
        "post_id": post_id,
        "like_count": post.like_count,
    }
