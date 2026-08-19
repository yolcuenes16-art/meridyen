from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.post import PostCreate, PostResponse
from backend.app.services.post_service import post_service


router = APIRouter(
    prefix="/api/v1/posts",
    tags=["Posts"],
)


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post: PostCreate) -> PostResponse:
    return post_service.create_post(post)


@router.get(
    "/feed",
    response_model=list[PostResponse],
)
async def get_feed() -> list[PostResponse]:
    return post_service.get_feed()


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post(post_id: int) -> PostResponse:
    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return post