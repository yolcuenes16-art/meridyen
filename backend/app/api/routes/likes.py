from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.like import LikeCreate, LikeResponse
from backend.app.services.like_service import like_service
from backend.app.services.post_service import post_service


router = APIRouter(
    prefix="/api/v1/posts",
    tags=["Likes"],
)


@router.post(
    "/{post_id}/likes",
    response_model=LikeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def like_post(
    post_id: int,
    like: LikeCreate,
) -> LikeResponse:

    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    try:
        return like_service.create_like(
            post_id=post_id,
            like=like,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/{post_id}/likes",
)
async def get_post_likes(post_id: int) -> dict:
    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return {
        "post_id": post_id,
        "like_count": like_service.get_like_count(post_id),
        "likes": like_service.get_likes(post_id),
    }