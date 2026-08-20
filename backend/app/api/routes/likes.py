from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.like import LikeCreate, LikeResponse
from backend.app.services.post_service import post_service


router = APIRouter(
    prefix="/api/v1/posts",
    tags=["Likes"],
)


@router.post(
    "/{post_id}/likes",
    response_model=LikeResponse,
)
async def like_post(post_id: int, like: LikeCreate) -> LikeResponse:
    try:
        count, liked = post_service.toggle_like(post_id, like.username)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        ) from exc

    return LikeResponse(
        post_id=post_id,
        username=like.username,
        created_at=datetime.now(timezone.utc),
        like_count=count,
        liked=liked,
    )


@router.get("/{post_id}/likes")
async def get_post_likes(post_id: int) -> dict:
    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return {
        "post_id": post_id,
        "like_count": post.like_count,
    }
